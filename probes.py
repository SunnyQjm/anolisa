#!/usr/bin/env python3
"""cosh-2597 invocation-transparency probes (B1-B10).

Runs against an installed layout:
  /usr/bin/cosh -> /usr/libexec/anolisa/cosh-ng/cosh-shell (symlink)
  /usr/libexec/anolisa/cosh-ng/{cosh-shell,cosh-core}

Oracle: /bin/bash. Each probe prints PASS/FAIL plus evidence; exit code is
the number of failures. PTY probes are event-driven (marker polling with a
deadline), never fixed sleeps.

Usage: python3 probes.py [--cosh /usr/bin/cosh] [--only B1,B2,...]
"""

import argparse
import os
import pty
import select
import signal
import subprocess
import sys
import time

DEADLINE = float(os.environ.get("COSH_PROBE_DEADLINE", "20"))
# Shell prompt marker: root prompts end with '#', non-root with '$'.
PROMPT = "# " if os.geteuid() == 0 else "$ "


def run(cmd, stdin=None, env=None, preexec_fn=None):
    proc = subprocess.run(
        cmd,
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        preexec_fn=preexec_fn,
        timeout=DEADLINE,
    )
    return proc.returncode, proc.stdout, proc.stderr


def pty_session(cmd, steps, env=None):
    """Spawn cmd on a real PTY; for each (wait_marker, send) step, poll the
    transcript until the marker appears, then write. Returns transcript."""
    pid, fd = pty.fork()
    if pid == 0:
        if env:
            os.environ.update(env)
        os.execvp(cmd[0], cmd)
    transcript = b""
    try:
        for marker, send in steps:
            deadline = time.time() + DEADLINE
            while marker.encode() not in transcript:
                if time.time() > deadline:
                    raise TimeoutError(
                        f"marker {marker!r} not seen; transcript={transcript!r}"
                    )
                ready, _, _ = select.select([fd], [], [], 0.2)
                if ready:
                    try:
                        chunk = os.read(fd, 4096)
                    except OSError:
                        chunk = b""
                    if not chunk:
                        break
                    transcript += chunk
            if send:
                os.write(fd, send.encode())
        deadline = time.time() + DEADLINE
        while True:
            if time.time() > deadline:
                break
            ready, _, _ = select.select([fd], [], [], 0.2)
            if ready:
                try:
                    chunk = os.read(fd, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                transcript += chunk
            else:
                done, _ = os.waitpid(pid, os.WNOHANG)
                if done:
                    break
    finally:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            os.waitpid(pid, 0)
        except ChildProcessError:
            pass
        os.close(fd)
    return transcript


RESULTS = []


def report(probe, ok, evidence):
    RESULTS.append((probe, ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {probe}: {evidence}")


def paired(probe, cosh, bash_argv, cosh_argv, stdin=None, env=None, preexec_fn=None):
    brc, bout, berr = run(bash_argv, stdin=stdin, env=env, preexec_fn=preexec_fn)
    crc, cout, cerr = run(cosh_argv, stdin=stdin, env=env, preexec_fn=preexec_fn)
    ok = (brc, bout) == (crc, cout)
    report(
        probe,
        ok,
        f"bash rc={brc} out={bout!r} | cosh rc={crc} out={cout!r} cerr={cerr!r}",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cosh", default="/usr/bin/cosh")
    parser.add_argument("--only", default="")
    args = parser.parse_args()
    cosh = args.cosh
    only = {p.strip().upper() for p in args.only.split(",") if p.strip()}

    def want(name):
        if only and name not in only:
            return False
        return True

    def guarded(name, runner):
        if not want(name):
            return
        try:
            runner()
        except Exception as error:  # noqa: BLE001 - one probe must not sink the rest
            report(name, False, f"probe error: {error}")

    if want("B1"):
        paired(
            "B1 -lc dash-combined",
            cosh,
            ["/bin/bash", "-lc", 'printf %s "$-"'],
            [cosh, "-lc", 'printf %s "$-"'],
        )
    if want("B2"):
        paired(
            "B2 --posix",
            cosh,
            ["/bin/bash", "--posix", "-c", "set -o | grep '^posix'"],
            [cosh, "--posix", "-c", "set -o | grep '^posix'"],
        )
    if want("B3"):
        rc, out, err = run([cosh, "--definitely-invalid"])
        report("B3 invalid option", rc == 2 and out == b"", f"rc={rc} out={out!r} err={err!r}")
    if want("B4"):
        rc, out, err = run([cosh, "/definitely/not/present"])
        report("B4 missing script", rc == 127, f"rc={rc} err={err!r}")
    if want("B5"):
        rc, out, err = run([cosh, "--resume"], stdin=b"")
        # TUI-only flags on the exec path reach the inner shell verbatim and
        # fail loudly (bash: invalid option, exit 2) — never silently drop
        # semantics, never emit TUI bytes into a pipe.
        report(
            "B5 tui-only flag + pipe fails loud via shell",
            rc == 2 and b"\x1b[" not in out and b"--resume" in err,
            f"rc={rc} out={out!r} err={err[:120]!r}",
        )
    def probe_b6():
        transcript = pty_session([cosh], [(PROMPT, "exit\n")])
        # TUI banner: rounded frame titled "cosh-shell" (or the block logo).
        ok = (
            b"cosh-shell" in transcript
            or b"COSH" in transcript
            or b"\xe2\x96\x88" in transcript
        )
        report("B6 bare tty still TUI", ok, f"tail={transcript[-160:]!r}")

    guarded("B6", probe_b6)

    def probe_b11():
        # Explicit `-l` on a full terminal is an allowlist TUI shape; it must
        # start the login TUI, not be misread as an adapter name.
        transcript = pty_session([cosh, "-l"], [(PROMPT, "exit\n")])
        ok = b"unknown adapter" not in transcript and (
            b"cosh-shell" in transcript
            or b"COSH" in transcript
            or b"\xe2\x96\x88" in transcript
        )
        report("B11 -l enters login TUI", ok, f"tail={transcript[-160:]!r}")

    guarded("B11", probe_b11)

    def probe_b7():
        transcript = pty_session(
            [cosh, "--norc", "--noprofile", "-i"],
            [(PROMPT, 'printf "[%s]" "$0"\n'), ("]", "exit\n")],
        )
        ok = (
            b"[" + os.path.basename(cosh).encode() + b"]" in transcript
            or b"[/usr/bin/cosh]" in transcript
        )
        ok = ok and b"COSH" not in transcript
        report("B7 -i goes native bash", ok, f"tail={transcript[-200:]!r}")

    guarded("B7", probe_b7)

    def probe_b8():
        rc, out, err = run(["su", "-", "cosh2597", "-c", 'echo "$0"'])
        report(
            "B8 login $0 dash prefix",
            rc == 0 and out.strip() == b"-cosh",
            f"rc={rc} out={out!r} err={err!r} (requires user cosh2597 with shell /usr/bin/cosh)",
        )

    guarded("B8", probe_b8)
    if want("B9"):
        script = 'set -o pipefail; yes x 2>/dev/null | head -n 1 >/dev/null; printf %s "${PIPESTATUS[*]}"'
        paired(
            "B9a sigpipe dfl",
            cosh,
            ["/bin/bash", "-c", script],
            [cosh, "-c", script],
        )

        def ignore_pipe():
            signal.signal(signal.SIGPIPE, signal.SIG_IGN)

        paired(
            "B9b sigpipe ign inherited",
            cosh,
            ["/bin/bash", "-c", script],
            [cosh, "-c", script],
            preexec_fn=ignore_pipe,
        )
    def probe_b10():
        env = dict(os.environ, PS1="__COSH_PS1_PROBE__ ")
        # The user PS1 reaching the inner bash IS the prompt marker (the
        # value-level contract renders it), so wait for the probe value.
        transcript = pty_session(
            [cosh],
            [("__COSH_PS1_PROBE__", "exit\n")],
            env=env,
        )
        ok = b"__COSH_PS1_PROBE__" in transcript
        report("B10 env PS1 reaches inner shell", ok, f"tail={transcript[-200:]!r}")

    guarded("B10", probe_b10)

    failures = sum(1 for _, ok in RESULTS if not ok)
    print(f"probes: {len(RESULTS)} run, {failures} failed")
    sys.exit(failures)


if __name__ == "__main__":
    main()
