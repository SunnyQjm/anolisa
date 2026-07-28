# PR evidence assets — alibaba/anolisa#1940

Real-machine acceptance for `fix/cosh-1940-approval-terminal-state`
(2 commits: shell approval lifecycle ledger + core last-resort approval
timeout).

Environment: cosh-lab-arm64-1940 container (Alibaba Cloud Linux 3, arm64),
real LLM (DashScope/qwen), real PTY (`repro_driver.py`, pty.fork driving
`cosh-shell raw cosh-core`, trust approval mode), production
`sandbox-failure-handler` PostToolUseFailure hook installed as a
`sandbox-failure-probe` extension.

## Scenarios (single clean batch)

| cast | scenario | result |
| --- | --- | --- |
| `p1-trust-sandbox-bypass-approved.cast` | #1920 regression: sandbox_bypass approval card surfaces, Enter approves, command retried | PASS — `bypass-probe-1920` printed, turn completed |
| `w1-trust-card-wait-60s.cast` | legitimate wait: card left untouched 60s before approving | PASS — no deny/timeout during the wait; audit shows 92.6s card lifetime |
| `c1-trust-control-greeting.cast` | control greeting | PASS |

Play with `asciinema play <file>.cast`. `key-frames.txt` holds the
ANSI-stripped card/approval frames for quick review.

## Audit segments (cosh-core)

- `cosh-core-1785250555058-*.jsonl` — p1: `approval.requested
  (assessment=sandbox_bypass)` 14:55:59.237 → `tool.completed` 14:56:30.008
  → `turn.completed`. (`approval.resolved` is absent for the
  host-executed-shell path; pre-existing core behavior.)
- `cosh-core-1785250659190-*.jsonl` — w1: `approval.requested`
  14:57:43.629 → `tool.completed duration_ms=92558` — the card survived a
  92.6s legitimate wait; neither the shell batch drain nor the core
  residual timeout fired.
- `cosh-core-1785250810300-*.jsonl` — c1 control.

`repro_driver.py` is the acceptance driver (signal detection matches on
ANSI-stripped text).
