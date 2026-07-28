# FAIL baseline — issue #1882 fully readonly compound cannot auto-execute

- Issue: https://github.com/alibaba/anolisa/issues/1882
- Worktree: anolisa/.worktrees/cosh-1882-compound-readonly-route
- Branch: fix/cosh-1882-compound-readonly-route
- Base commit: 627681f950cf662827d28026d1d05815ad3286e3 (origin/main)
- Date: 2026-07-28

## Reproduction command (transient probe, per isolation-baseline.md)

Probe test `probe_issue_1882_fully_readonly_compound_auto_executes`
appended to
`src/cosh-ng/crates/cosh-shell/src/tools/command_risk_tests.rs`
(patch: probe-patch.diff), then:

```
cd anolisa/.worktrees/cosh-1882-compound-readonly-route/src/cosh-ng
cargo test -p cosh-shell --lib probe_issue_1882
```

## Result: FAILED (exit code 101)

```
assertion `left != right` failed: execution=AskUser auto_allow=None
reasons=["and-or-list-not-auto-executable", "bounded-readonly",
"unknown-command", "safe-diagnostic-family"]
  left: AskUser
 right: AskUser
```

`pwd && df -h` under `AutoExecutionPolicy::current_runtime()` routes to
`AskUser` with `auto_allow=None`, even though the per-segment reasons
(`bounded-readonly` for `pwd`, `safe-diagnostic-family` for `df -h`)
show every segment individually qualifies — segment evidence exists
(#1785 / PR #1905) but no execution route can consume it for compounds.

- Full output: probe-fail-output.txt (CARGO_TEST_EXIT_CODE=101 appended)
- Probe patch: probe-patch.diff (probe reverted afterwards; worktree
  restored clean at base commit — `git status --porcelain` empty)

## Notes

- Enhancement issue (type:enhancement): baseline is the quantified
  current behavior (unit-level route assertion), per skill S1 rule for
  non-defect issues.
- HEAD focused suite green before probing: `cargo test -p cosh-shell
  --lib command_risk` → 21 passed (current behavior is test-anchored;
  anchors at command_risk_tests.rs L222/L539 and route test L59 must be
  re-anchored in S5, not treated as accidental breakage).

## Real-PTY FAIL→PASS evidence (captured 2026-07-28, container cosh-lab-arm64-1882)

Canonical cases CARD-026 / CARD-027
(`specs/shell-e2e-validation/cases/interaction-cards.yaml`), real
cosh-core adapter + real dashscope provider, scripted PTY
(execution_evidence=scripted-pty; real-provider evidence class NOT
claimed — registry `auth_source=null` cannot complete the trusted
proof chain). PTY 100x30 per cast headers; auto approval mode.

- FAIL side (base 627681f9 binary sha `f1598437…`): run
  `20260728T061244Z-9e2d90a2`, CARD-026 runner failures
  `missing: Auto-approved / unexpected: Allow once / case timed out`;
  screenshot `fail-approval-card.png` (auto mode still shows
  `Approval req-1 · Bash · low risk · $ pwd && df -h`; frame extracted
  from truncated cast).
- PASS side (fix binary sha `1a1d2e08…`, final with newline gate):
  - CARD-026 run `20260728T083509Z-efbd1c89`, ok=true, evidence verify
    ok; `pass-auto-approved-card.png` (Auto-approved card) +
    `pass-compound-output.png` (compound executed, df output visible).
  - CARD-027 run `20260728T083537Z-c7c6c5f6`, ok=true, evidence verify
    ok; newline compound (`pwd\ndf -h`) fails closed to the approval
    card (`pass-newline-failclosed-card.png`) and Deny receipt
    (`pass-newline-deny-receipt.png`) — design R1 outcome.
- Casts: `pass-transcript.cast` / `fail-transcript.cast` /
  `newline-transcript.cast`; hashes in `pty-evidence.sha256`.
- Aggregate gate: `gate evaluate` → **Go** (acceptance, arm64,
  container, CARD-026 + CARD-027).
- R1 finding: intermediate binary `92027e10…` (before the newline
  gate) granted auto-approval to `pwd\ndf -h`, but
  `ShellHandoffRequest::validate` rejects multiline commands and
  `queue_approved_shell_handoff` drops the failure silently → provider
  turn hangs (4 reproductions). Fixed by the newline eligibility gate;
  the silent-drop defect itself is pre-existing (manual approval of
  multiline commands hits it today) and is tracked separately.
