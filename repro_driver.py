#!/usr/bin/env python3
"""Issue #1940 real-PTY acceptance driver (D3 scenarios).

Spawns the real `cosh-shell raw cosh-core` binary inside a PTY (trust
approval mode) and drives the post-fix acceptance scenarios:

p1: #1920 regression — same sandbox_bypass trigger; the approval card
    surfaces, Enter approves it, cosh-core retries the original command
    and the turn completes. Also proves the batch drain never touches a
    request that has a home (the surfaced card).
w1: I2 legitimate wait — same trigger, but the card is left untouched
    for 60 seconds before approving. PASS requires: no deny/timeout
    response reaches cosh-core during the wait (no "denied"/"timed out"
    text, no turn termination), the card is still actionable after 60s,
    and the post-approve retry completes. Guards against both an
    over-eager shell drain and the core residual timeout misfiring.
c1: control, plain greeting -> real adapter turn completes.

Runs inside the cosh-lab container (python 3.11, stdlib only).
"""
import argparse
import fcntl
import json
import os
import pty
import re
import select
import signal
import struct
import sys
import time

import termios

COLS = 120
ROWS = 40
HARD_TIMEOUT = 320.0

TRIGGER = ("?? 帮我把这条命令原样执行一次，不要修改也不要解释："
           "linux-sandbox --sandbox-policy-cwd /tmp -- bash -c 'echo bypass-probe-1920'\r")

SCENARIOS = {
    "p1-trust-sandbox-bypass-approved": {
        "steps": [
            (6.0, TRIGGER),
            (35.0, "\r"),                  # approve the surfaced card
            (60.0, ""),                    # retried command + final reply
            (3.0, "exit\r"),
        ],
    },
    "w1-trust-card-wait-60s": {
        "steps": [
            (6.0, TRIGGER),
            (35.0, ""),                    # card surfacing window
            (60.0, ""),                    # I2: legitimate wait, untouched
            (2.0, "\r"),                   # approve after the wait
            (45.0, ""),                    # retried command + final reply
            (3.0, "exit\r"),
        ],
    },
    "c1-trust-control-greeting": {
        "steps": [
            (6.0, "你好\r"),
            (110.0, ""),                   # real adapter turn
            (2.0, "exit\r"),
        ],
    },
}


def run_scenario(name, spec, binary, outdir, workdir=None):
    os.makedirs(outdir, exist_ok=True)
    cast_path = os.path.join(outdir, name + ".cast")
    raw_path = os.path.join(outdir, name + ".raw")
    start = time.time()
    events = []
    raw = bytearray()

    pid, master = pty.fork()
    if pid == 0:
        if workdir:
            os.chdir(workdir)
        os.environ["TERM"] = "xterm-256color"
        os.environ["LANG"] = "zh_CN.UTF-8"
        os.environ["LC_ALL"] = "zh_CN.UTF-8"
        os.environ["COSH_SHELL_RAW_SHELL"] = "bash"
        os.environ["COSH_SHELL_APPROVAL_MODE"] = "trust"
        os.execv(binary, [binary, "raw", "cosh-core"])
        os._exit(127)

    fcntl.ioctl(master, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))

    def pump(duration):
        deadline = time.time() + duration
        while time.time() < deadline:
            remain = max(0.05, deadline - time.time())
            ready, _, _ = select.select([master], [], [], remain)
            if master in ready:
                try:
                    chunk = os.read(master, 65536)
                except OSError:
                    return False
                if not chunk:
                    return False
                raw.extend(chunk)
                events.append([round(time.time() - start, 6), "o",
                               chunk.decode("utf-8", "replace")])
        return True

    alive = True
    for delay, keys in spec["steps"]:
        if not alive or time.time() - start > HARD_TIMEOUT:
            break
        alive = pump(delay)
        if keys and alive:
            events.append([round(time.time() - start, 6), "i", keys])
            os.write(master, keys.encode("utf-8"))
    if alive:
        pump(3.0)

    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass
    deadline = time.time() + 5
    status = None
    while time.time() < deadline:
        done, code = os.waitpid(pid, os.WNOHANG)
        if done == pid:
            status = code
            break
        time.sleep(0.1)
    if status is None:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
        _, status = os.waitpid(pid, 0)
    os.close(master)

    with open(raw_path, "wb") as fh:
        fh.write(bytes(raw))
    header = {"version": 2, "width": COLS, "height": ROWS,
              "timestamp": int(start), "title": "cosh #1940 " + name,
              "env": {"TERM": "xterm-256color", "SHELL": "/bin/bash"}}
    with open(cast_path, "w") as fh:
        fh.write(json.dumps(header) + "\n")
        for event in events:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    text = bytes(raw).decode("utf-8", "replace")
    # Signals are matched on ANSI-stripped text: the card renderer interleaves
    # CSI sequences inside glyphs, so raw-byte matching misses visible cards.
    plain = re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", text)
    plain = re.sub(r"\x1b\][^\x07]*\x07", "", plain)
    return {"scenario": name, "cast": cast_path, "raw": raw_path,
            "exit_status": status, "output_bytes": len(raw),
            "saw_bypass_probe": "bypass-probe-1920" in plain,
            "saw_approval_card": ("Approval req" in plain or "\u5ba1\u6279 req" in plain
                              or "sandbox_bypass" in plain),
            "saw_approved": "\u5df2\u6279\u51c6 req" in plain or "approved" in plain.lower(),
            "saw_denied": "denied" in plain.lower(),
            "saw_timed_out": "timed out" in plain.lower()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--only", default=None)
    parser.add_argument("--cwd", default=None,
                        help="chdir for the spawned shell (default: keep cwd)")
    args = parser.parse_args()

    names = [args.only] if args.only else list(SCENARIOS)
    results = []
    for name in names:
        print("[repro-1940] scenario %s ..." % name, flush=True)
        results.append(run_scenario(name, SCENARIOS[name], args.binary,
                                    args.outdir, workdir=args.cwd))
        print(json.dumps(results[-1], ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
