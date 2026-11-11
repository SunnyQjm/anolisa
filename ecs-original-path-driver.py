import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import tomllib


os.umask(0o077)
ROOT = Path(sys.argv[1])
CORE = ROOT / "frozen/cosh-core"
OUT = ROOT / "registry-evidence"
OUT.mkdir(mode=0o700)
EXPECTED = "328a9fdd7b96e9592f9172f822fe6d7bdd9e13dd"
PROJECT = '''[ai]
active_model = "qwen3.9-probe"
active_provider = "should-be-ignored"

[ai.providers.should-be-ignored]
type = "dashscope"
model = "should-be-ignored"
'''
PAYLOAD = {"type": "registry_request", "request_id": "r1", "domain": "auth", "action": "activate_trial", "params": None}


def fingerprint(path):
    stat = path.stat()
    return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "inode": stat.st_ino, "device": stat.st_dev, "size": stat.st_size}


def invoke(home, cwd, messages, directory, label, arguments):
    env = {"HOME": str(home), "PATH": "/usr/sbin:/usr/bin:/sbin:/bin"}
    stdout, stderr = "", ""
    communicated = False
    process = subprocess.Popen([str(CORE), *arguments], cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        deadline = time.monotonic() + 10
        while True:
            executable = Path(f"/proc/{process.pid}/exe")
            try:
                if os.readlink(executable) == str(CORE):
                    loaded = fingerprint(executable)
                    break
            except FileNotFoundError:
                pass
            assert process.poll() is None, "Core exited before ELF observation"
            assert time.monotonic() < deadline, "Core ELF observation timed out"
            time.sleep(0.01)
        assert loaded == INITIAL, "Loaded Core differs from frozen binary"
        stdout, stderr = process.communicate("".join(json.dumps(message) + "\n" for message in messages), timeout=45)
        communicated = True
    finally:
        if not communicated:
            if process.poll() is None:
                process.kill()
            stdout, stderr = process.communicate()
        (directory / (label + "-stdout.jsonl")).write_text(stdout)
        (directory / (label + "-stderr.txt")).write_text(stderr)
    assert process.returncode == 0, f"{label} exit={process.returncode}: {stderr}"
    return {"argv": ["cosh-core", *arguments], "cwd": str(cwd), "env_keys": sorted(env), "input_messages": messages, "exit_code": process.returncode, "loaded_binary": loaded, "output_messages": [json.loads(line) for line in stdout.splitlines() if line.strip()], "stderr": stderr}


def request(home, cwd, message, directory, label):
    record = invoke(home, cwd, [message], directory, label, ["--registry"])
    assert len(record["output_messages"]) == 1
    response = record["output_messages"][0]
    assert response["success"] is True, response
    assert response["request_id"] == message["request_id"]
    return {**record, "response": response}


def reload_engine(home, cwd, directory):
    messages = [
        {"type": "control_request", "request_id": "neutral-init", "request": {"subtype": "initialize", "protocol_version": 1, "fire_session_start": False, "capabilities": {"can_handle_ecs_trial_v1": True}}},
        {"type": "control_request", "request_id": "stop", "request": {"subtype": "shutdown"}},
    ]
    record = invoke(home, cwd, messages, directory, "neutral-engine", ["--headless", "--cosh-shell-transport", "--workspace", str(cwd)])
    outputs = record["output_messages"]
    initialized = [message for message in outputs if message.get("type") == "system" and message.get("subtype") == "init"]
    assert len(initialized) == 1, outputs
    assert initialized[0]["model"] == "auto", initialized
    assert not any(message.get("type") == "assistant" for message in outputs)
    return {**record, "initialized_engine_model": initialized[0]["model"]}


def verify_case(scenario, number):
    directory = OUT / f"{scenario}-{number}"
    directory.mkdir()
    home, cwd, neutral = [directory / name for name in ["home", "project", "neutral"]]
    for path in [home, cwd, neutral]:
        path.mkdir()
    project_config = cwd / ".copilot-shell/config.toml"
    if scenario != "neutral-control":
        project_config.parent.mkdir()
        project_config.write_text(PROJECT if scenario == "original-project" else '[ai]\nactive_model = "qwen3.9-probe"\n')
    user_config = home / ".copilot-shell/config.toml"
    assert not user_config.exists()
    assert not (neutral / ".copilot-shell/config.toml").exists()
    activation = request(home, cwd, PAYLOAD, directory, "activation")
    data = activation["response"]["data"]
    saved_text = user_config.read_text()
    saved = tomllib.loads(saved_text)["ai"]
    saved_hash = hashlib.sha256(user_config.read_bytes()).hexdigest()
    provider_id = data["active_provider"]
    provider = saved["providers"][provider_id]
    assert provider_id == "ecs-free-trial"
    assert provider["type"] == "aliyun" and provider["auth_source"] == "ecs_identity"
    assert "should-be-ignored" not in saved["providers"]
    assert all(not provider.get(k) for k in ["api_key", "access_key_id", "access_key_secret", "security_token"])
    if scenario == "original-project":
        assert "ignoring active_provider from project config" in activation["stderr"]
        assert "ignoring ai.providers from project config" in activation["stderr"]
    reload_message = {**PAYLOAD, "request_id": "reload", "action": "state"}
    reload_result = request(home, neutral, reload_message, directory, "neutral-reload")
    state = reload_result["response"]["data"]
    active = [item for item in state["saved_providers"] if item["active"]]
    assert len(active) == 1
    loaded = active[0]
    assert loaded["provider_id"] == provider_id and loaded["source"] == "user"
    assert loaded["auth_source"] == "ecs_identity"
    assert state["effective_auth_required"] is False
    engine = reload_engine(home, neutral, directory)
    models = {"activation_returned": data["model"], "user_active_model": saved["active_model"], "user_provider_model": provider["model"], "neutral_reload_reported_provider_model": loaded["model"], "neutral_initialized_engine_model": engine["initialized_engine_model"]}
    assert set(models.values()) == {"auto"}, models
    assert "qwen3.9-probe" not in saved_text
    assert hashlib.sha256(user_config.read_bytes()).hexdigest() == saved_hash
    (directory / "saved-user-config.toml").write_text(saved_text)
    result = {"scenario": scenario, "round": number, "project_config": project_config.read_text() if project_config.exists() else None, "fresh_user_config_absent": True, "neutral_project_config_absent": True, "activation": activation, "persisted_user_config_sha256": saved_hash, "persisted_ai": saved, "neutral_reload": reload_result, "neutral_engine": engine, "reload_user_config_unchanged": True, "models": models, "assertions_passed": True}
    (directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"{scenario} #{number}: returned=auto | user.active_model=auto", flush=True)
    print("  user.provider.model=auto | neutral new-engine=auto | source=user", flush=True)
    return result


INITIAL = fingerprint(CORE)
print("ISSUE9840 ORIGINAL PATH READY", flush=True)
assert input() == "run"
results = []
status = 0
failure = None
try:
    assert not Path("/etc/copilot-shell/config.toml").exists()
    for scenario in ["original-project", "neutral-control", "project-model-only"]:
        for number in range(1, 4):
            results.append(verify_case(scenario, number))
except Exception as error:
    status = 1
    failure = f"{type(error).__name__}: {error}"
    print(failure, flush=True)
finally:
    final = fingerprint(CORE)
    if final != INITIAL:
        status = 1
        failure = "Frozen Core binary identity changed"
    summary = {"candidate_sha": EXPECTED, "original_payload": PAYLOAD, "core_start": INITIAL, "core_end": final, "binary_identity_unchanged": INITIAL == final, "completed_cases": len(results), "expected_cases": 9, "all_passed": status == 0 and len(results) == 9 and INITIAL == final, "failure": failure, "real_model_inference_requests": 0, "results": results}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if summary["all_passed"]:
        print("ORIGINAL PATH VERIFIED: 9/9 complete activation-persist-reload chains", flush=True)
    print("CORE SHA256 " + INITIAL["sha256"], flush=True)
    print("ISSUE9840 ORIGINAL PATH FINISHED", flush=True)
assert input() == "exit"
raise SystemExit(status)
