# Issue 7891 validation index

Status: native clean commit b353d618; measured arm64 local aggregate Go; exact commit preflight and cleanup verified. PR pending. Formal integrated dual-architecture/provider acceptance remains separate.

Candidate base: `2b4af68af60880790092011b96d204b33adb0c0b`.
Candidate tree: `ec6349fd690403b2e4003e846e3f8234daf1f6d0`.
Cosh subtree: `f1dbd5bd1cee77ee311a9a104aa539dcdd692afc`.
Exact per-file binding: [CANDIDATE-TREE.json](CANDIDATE-TREE.json).

| Evidence | Scope and limit |
| --- | --- |
| [Native prompt audit](u02-persistent-tty-audit.md) | Actual original failure, second physical EIO and R4 cursor regression are retained; R5 restores native PS1 before input. |
| [R5 minimal results](local-linux/r5-minimal-green.json) | Real release Shell/Core/worker identities, prompt-refault, original three physical faults and closed loop. |
| [Production matrix](local-linux/r5-production-matrix-results.json) | 23 actual named tests; deny inline-reference leg classified separately. |
| [Debug matrix](local-linux/r5-debug-matrix-results.json) | 34 actual named tests; six Core protocol/lifecycle fixtures are not actual release Core evidence. |
| [Compiled mutation controls](local-linux/compiled-controls.json) | Heartbeat and prompt-debt mutations compile, fail the behavioral assertions, and have fixed-binary positive controls. |
| [Trust controls](local-linux/trust-r5-controls.json) | Actual wrong-owner, writable-ancestor and symlink refusals with before/after positive controls. |
| [Complete raw rerun](local-linux/candidate-full-raw-repaired-audit.json) | Actual626PASS/0FAIL/1originalignored, all627 names checked; first610PASS/16FAIL/1ignored retained with missing Zsh/physical targetdir preconditions and exact environment delta. |
| [Preflight audit](local-linux/candidate-preflight-audit.json) | Rust1.97.1 fmt, workspace all-targets Clippy, Shell layout and four actual nonempty test inventories; source-layout separately runs on Linux Bash5.2.15. Earlier Bash3/concurrency tooling failures retained. Empty commit-lint range is not final-commit validation. |
| [Behavior and L3 review](review-r5-behavior.md) | Complete reviewed source and final doc; zero new P0/P1/P2 findings; not release Go. |
| [Rules review](review-r5-rules.md) | Complete reviewed diff; existing mirror drift recorded without shared mirror edits or new waiver. |
| [Production interfaces](PRODUCTION-INTERFACES.json) | U02a/b/c remain open for explicit missing witnesses/interfaces. |

The approved repair is bounded display survival and existing command settlement. It does not add general terminal takeback, replay an approved effect, synthesize command success or claim final dual-architecture installed/provider acceptance. ParentRoot owns final integrated source/RPM freeze and that acceptance.
