import ast
import base64
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
NEW = "c89e56108c8abd9c164e53cb9302a4a5b1db6265811779922d20a93642b1404b"
OLD = "aa42e64319bbf76fd44720908801b10aefee331fc5509e3d7b6a92eb9487d72e"
ARGV = ["/usr/bin/python3", "/usr/bin/dnf", "check-update", "cosh-ng"]
IDENTITY = ("pid", "start_ticks", "cgroup", "cgroup_device", "cgroup_inode")


def proof(value, *, root=False):
    assert value["stable"] is True
    assert value["before"] == value["after"]
    assert value["command_before"] == value["command_after"] == {
        "exe": value["exe"], "argv": value["argv"]
    }
    group = {key: value[key] for key in ("cgroup_device", "cgroup_inode")}
    assert value["cgroup_identity_before"] == group == value["cgroup_identity_after"]
    assert value["exe"] == ("/usr/libexec/anolisa/cosh-ng/cosh-shell" if root else "/usr/bin/python3.11")
    assert value["argv"] == (["-cosh"] if root else ARGV)
    return {**value["before"], **group}


def observation(result, raw, blocking):
    assert len(result["observations"]) == 1
    row = result["observations"][0]
    assert row["process"] == raw and row["blocking"] is blocking
    assert result["blocking_processes"] == ([raw] if blocking else [])
    assert row["classification"] == ("foreign-or-unknown" if blocking else "candidate-update-probe")
    return row["evidence"]


def owned(result, raw, seed):
    evidence = observation(result, raw, False)
    child, root = proof(evidence["child"]), proof(evidence["root"], root=True)
    assert child["pid"] == raw["pid"] and child["start_ticks"] == raw["start_ticks"]
    assert {key: root[key] for key in IDENTITY} == seed == evidence["held_identity"]
    assert child["ppid"] == root["pid"]
    for key in ("cgroup", "cgroup_device", "cgroup_inode"):
        assert child[key] == root[key]
    return child


script = D / "Root-c89-live-collector-paused.py"
tree = ast.parse(script.read_bytes())
new_source = next(
    base64.b64decode(node.value.value)
    for node in tree.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "MODULE_B64" for target in node.targets)
)
assert hashlib.sha256(new_source).hexdigest() == NEW
embedded_old = [
    base64.b64decode(node.args[0].value)
    for node in ast.walk(tree)
    if isinstance(node, ast.Call)
    and isinstance(node.func, ast.Attribute)
    and node.func.attr == "b64decode"
    and node.args
    and isinstance(node.args[0], ast.Constant)
]
assert any(hashlib.sha256(source).hexdigest() == OLD for source in embedded_old)
root_receipt = json.loads((D / "ROOT-C89-DUAL-NATIVE-VERIFIED.json").read_text())
summary = {}
for architecture in ("aarch64", "x86_64"):
    path = D / (architecture + "-ROOT-C89-LIVE-PAUSED.json")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == root_receipt["architectures"][architecture]["sha256"]
    envelope = json.loads(path.read_bytes())
    assert envelope["ok"] and envelope["data"]["exit_code"] == 0
    operation_path = Path(envelope["meta"]["run_dir"]) / "run.json"
    operation = json.loads(operation_path.read_bytes())
    environment_path = operation_path.parent.parent / operation["environment_ref"] / "run.json"
    environment = json.loads(environment_path.read_bytes())
    assert environment["profile"]["arch"] == architecture
    host = environment["backend"]["transport"]["public_host"]
    assert any("root@" + host in probe.get("argv", []) for probe in envelope["data"]["probes"])
    data = json.loads(envelope["data"]["stdout"])
    assert data["module_sha256"] == NEW and data["source"] == "f81ffa2672f56849157bf400a0d3b012ed0f948a"
    assert data["held_count"] == data["seed_count"] == 8
    details = data["details"]
    assert len(details["owned"]) == 16 and len(details["external"]) == 8
    assert len(details["negative_controls"]) == 6
    for row in details["owned"]:
        assert row["old_held_busy_policy_contended"]
        owned(row["result"], row["original_busy_record"], row["root_seeds"][0])
    for row in details["external"]:
        child = proof(observation(row["result"], row["raw"], True)["child"])
        assert all(child["cgroup"] != seed["cgroup"] for seed in row["seeds"])
    for row in details["negative_controls"]:
        observation(row["result"], row["input"], True)
        assert row["blocked"]
    assert {row["suffix"] for row in details["sibling_controls"]} == {repr(x) for x in (" ", "\t", "\r")}
    for row in details["sibling_controls"]:
        suffix = ast.literal_eval(row["suffix"])
        before = owned(row["before_move"], row["raw"], row["seed"])
        restored = owned(row["restored"], row["raw"], row["seed"])
        old = owned(row["old_aa42"], row["raw"], row["seed"])
        evidence = observation(row["new"], row["raw"], True)
        child, root = proof(evidence["child"]), proof(evidence["root"], root=True)
        assert child["cgroup"] == root["cgroup"] + suffix
        assert child["cgroup_inode"] != root["cgroup_inode"]
        assert child["cgroup_device"] == root["cgroup_device"]
        for key in ("pid", "start_ticks", "ppid"):
            assert child[key] == before[key] == old[key] == restored[key]
        assert all(row[key] for key in ("actual_membership_preserved", "new_blocked", "old_false_owned", "valid_RED_GREEN", "sibling_removed"))
    assert data["all_owned_groups_removed"] and data["all_negatives_blocked"]
    first_path = D / (architecture + "-ROOT-C89-LIVE.json")
    first = json.loads(json.loads(first_path.read_bytes())["data"]["stdout"])
    assert len(first["details"]["sibling_controls"]) == 3
    assert all(not row["observations"] and row["valid_RED_GREEN"] is False and row["sibling_removed"] for row in first["details"]["sibling_controls"])
    summary[architecture] = {"raw_sha256": digest, "environment_ref": operation["environment_ref"], "environment_manifest_sha256": hashlib.sha256(environment_path.read_bytes()).hexdigest(), "architecture_and_transport_binding_verified": True, "owned": 16, "external_blocked": 8, "negative_controls": 6, "actual_sibling_RED_GREEN_restore": 3, "owned_and_sibling_cleanup_zero": True, "first_no_capture_sha256": hashlib.sha256(first_path.read_bytes()).hexdigest(), "first_no_capture_not_claimed_green": True}
result = {"module_sha256": NEW, "old_module_sha256": OLD, "collector_sha256": hashlib.sha256(script.read_bytes()).hexdigest(), "architectures": summary, "scope": "independent check of native diagnostic receipts; scoped SIGSTOP/SIGCONT, not formal performance", "first_no_capture_attempt_retained": True}
(D / "INDEPENDENT-C89-DUAL-NATIVE-CHECK.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
