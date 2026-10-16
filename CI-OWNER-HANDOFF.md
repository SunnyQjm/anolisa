# #7766 CI owner handoff

Status: blocked CI, one automatic unchanged-head rerun used; no further reruns requested.
This owner changed no Rust/product source and does not extend the Python tool PR into Rust.
Root selects the existing Shell rawCLI/product-test owner for a scoped reproduction/fix decision.

## Exact execution/source

PR head e20a30f38cfd8bbd4232dfada4b7300a109e6609. Both actual CI checkouts were synthetic merge
8cd29f13c55c72eb3317adaad8e0197c5c73e6ad, verified from each checkout log and fetched Git object.
Parents are base3a2452e71dfacc0df37532b079f6a01e3bce5e02 plus e20. Merge tree equals e20
78f1a08926b02a0c4ba171d7ad8eb018b5c4aa03. Base/head/merge Rust crates tree all
c982ad92ae8bd3a1ae88c38677e7c3e193072069; Cargo.lock/workflow/testgate blobs also identical.
Only added script+test Python files differ. CI-SYNTHETIC-SOURCE-BINDING.json contains full objects.

## Actual failures, no inferred recurrence

Run38830697225 attempt1/job116748769414: 618 pass,2 fail,1 ignored.
- agent_input::raw_cli_zsh_routes_space_prefixed_path_prompt_before_zle, agent_input.rs174:5.
- agent_input::raw_cli_routes_slash_bearing_han_prompt_before_shell_execution, line46:9.
Both show zsh execution/no-such-file instead of fake adapter's expected routed-prompt notice.

Attempt2/job116754457726: 619 pass,1 fail,1 ignored.
- agent_input::raw_cli_zsh_routes_fragmented_slash_leading_path_prompt, line276:64.
The first two cases are explicitly ok in attempt2. This third case was explicitly ok in attempt1.
Output shows user private binding, ordinary first command, then path user-widget/history hooks
and no-such-file/history leak. It is not a timeout. Aggregate check also fails.
Both complete logs and SHA/proof comparisons are preserved in CI-FAILURE-MATRIX-HANDOFF.json.

## Minimum attribution and remaining uncertainty

Functional Rust diff in this PR is absent, including actual synthetic checkout. The failures are
existing zsh path-routing lifecycle tests, not execution of the new Python classifier. Exact same
source-file main precedents exist for the first two cases (CI-BOTH-EXACT-MAIN-PRECEDENTS.json).
This does not establish root cause, permit a flaky waiver or turn current CI green. The repeat did
not pass; suspected-flaky classification is not satisfied. No cross-PR same-window evidence was
established for upstream-suspect classification either.

Read-only lead: tests/raw_cli/agent_input.rs calls support/raw_cli.rs delayed-input helper with
session_ready=None/ready_marker=None and fixed waits; input-readiness helpers already exist.
However attempt2 had visible prior prompt/command, so first-input startup delay alone is not a
complete explanation. Inspect routing readiness/state with a controlled original-case RED/GREEN;
do not blindly add sleep, weaken notices/history/private-widget oracles, or change thresholds.
Only tests that actually fail need base-side targeted reproduction; avoid a broad unrelated suite.

## Ownership and completion boundary

Root owns tracking/assignment and any isolated Rust repair outside7766. Suggested first ownership:
crates/cosh-shell/tests/raw_cli/agent_input.rs plus tests/support/raw_cli.rs for reproduction;
production path-routing owner only after mechanism attribution. Preserve all original failures.
No new source modification, PR, merge, deploy or resource purchase by this owner.

The c89 Python helper,25 tests,83 old runner tests(1skip),5 wiring tests,local mandatory preflight
and dual-native real whitespace sibling controls remain separately verified; current-head CI and
formal APPROVED are still merge gates. Root6808 production repair/new candidate RPM and formal
8h requirements remain separate. Old original8h Blocked and oldv6 partials stay unchanged.
