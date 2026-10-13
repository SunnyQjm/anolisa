# Narrow CI failure analysis

Candidate: `8e13db4be2dfc29acb0b53a3a9e18d62bfe4d072`; CI run `38460682517`. Read-only analysis; no tests, environment actions, timeout changes, or source edits performed.

## Conclusion

The failed test does not execute cosh-core or the C session-budget changes. However, source inspection exposes a concrete pre-existing Shell routing mismatch that matches the failure. A repeat with unchanged assertions is useful to establish frequency, but a green repeat alone does not justify classifying this as purely environmental.

## Evidence and call chain

- `crates/cosh-shell/tests/raw_cli/native.rs:576-618` selects adapter `fake`, changes enhanced routing to shell-only, sends `hello there`, then sends `/mode routing assisted`. Input delays are fixed 500/300/300/300/500 ms. The failure is the assisted-mode notice assertion at line 605.
- `tests/support/raw_cli.rs:481-498` selects Shared execution and passes neither a readiness sender nor a marker. Its inner helper at lines 716-726 starts `cosh-shell raw fake`; lines 761-768 sleep and write each chunk without synchronizing with each completed command or prompt. Configuration at lines 927-950 selects isolated enhanced Bash with a temporary HOME.
- `src/adapter/mod.rs:330-335,480-485` selects `FakeAgentAdapter`, separate from `CoshCoreAdapter`. `src/adapter/fake.rs:52-75` implements the fake provider within Shell. Shell Cargo.toml has no cosh-core crate dependency. The complete candidate diff against base `69ae39dc5b97e47a399ed6c42d841d421e29c6dd` contains only 12 cosh-core source/test files; no Shell routing, helper, marker, manifest, or lockfile change.
- `CI-failed.log:987-1009` shows the first `Routing mode set to shell-only.` notice, one Bash `hello: command not found`, then Bash `/mode: No such file or directory` and a second Bash `hello` error. The process exited normally. This is an actual missing routing transition, not a timeout assertion. Lines 1012-1015 preserve the sole failed test and `579 passed; 1 failed; 1 ignored` result.

## Concrete Shell mismatch

`src/input/mod.rs:42-58` disables assistance by removing its state file. Its classifier deliberately still intercepts `/mode routing ...` while disabled (`:207-217`), allowing routing to be restored.

But `src/raw_input/relay/candidate.rs:191-209` subsequently submits an intercepted exact slash command through Bash when `slash_route_enabled` and `main_prompt_gate.is_at_prompt()` are true. That branch does not require assistance to be enabled. `src/shell_host/raw_runner.rs:412-416` sets the route capability independently of the assistance toggle. Bash's corresponding guard (`src/shell_host/marker/bash.sh:506-509`) returns without intercepting when assistance is disabled; the unknown-command fallback likewise requires enabled assistance (`:453-455`). Consequently `/mode routing assisted` can reach Bash as an ordinary path, exactly as recorded in CI.

Timing is relevant: the prompt gate can select Bash routing versus the Rust intercept fallback. Fixed input sleeps do not establish which state was reached. A load-dependent failure is therefore plausible, but the source provides a concrete routing defect rather than evidence of a harmless scheduler-only failure. This is outside the C-owned diff; no causal link to global budget/legacy cleanup is established by this failure. Keep CI failed until a subsequent run/readback proves its status, and track the Shell risk separately rather than weakening this test.
