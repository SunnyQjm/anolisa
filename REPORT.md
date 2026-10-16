# PR6808 audit startup PATH review verification

Final exact commit 5632512832600f5efef47f658d7e015ec732e48a verified; original RED and all intermediate receipts remain preserved.

ALinux4 aarch64 container `20261016T003944Z-838bf79c`, Rust 1.97.1, source bind read-only, independent cloned dependency cache. No auth mount or real provider use. Source/test baseline hashes: RED-SOURCE.json.

Original RED: exact `native::raw_cli_audit_commands_use_the_login_profile_path_once`, compiled successfully, 0 passed / 1 failed / 591 filtered. All three actual slash commands returned cannot start cosh-cli ENOENT. The profile-only fixture was unavailable through the inherited parent PATH.

Product patch belongs to Root. Test formatting changed only to rustfmt layout between original RED and initial GREEN; these are not identical test bytes. Original RED remains immutable. A final same-test-byte compiling mutation is required after final source synchronization.

Pre-rebase GREEN: new regression 1; existing startup/login positive and negative controls 10; existing audit raw controls 2; audit bin unit 6. `--lib slash::audit` selected zero tests and is excluded from pass counts. The actual unit target is `--bin cosh-shell`.

Native regression records status, trace, and export invocation and child PATH; inherits `/usr/bin:/bin`, installs cosh-cli only in profile-bin, confirms profile side effect runs exactly once.

Not run: workspace test, release build, real provider, installed RPM, dual architecture acceptance. Cleanup deferred until final source verification; environment is owned by this test task only.

Current verdict: focused tests, final standard preflight, commit metadata, and environment cleanup PASS. This is not a release result.

Final latest-main source readiness: FINAL-SOURCE-READY.json (base main 3a2452e71dfacc0df37532b079f6a01e3bce5e02, rebased head before fold 058e145ea161f61760dbdf8be77c36d3db411cdd). FINAL-SOURCE-SHA.json binds audit.rs, native.rs, and unchanged Cargo.lock.

Final compiling mutation: a private source copy under the owned container cache reverts only the audit command constructor and import. Final test SHA f5a92750be93fcd7a7385790e1b94ef35536ba3e7b308b72f6c2e87c0aa2eb9a is identical for mutation RED and restored GREEN. RED compiled and executed 1 actual test (0 PASS / 1 FAIL / 631 filtered), with three real ENOENT audit errors; restored GREEN executed 1 actual test (1 PASS / 0 FAIL / 631 filtered). Root worktree was never changed for mutation. See FINAL-COMPILING-MUTATION.json and immutable mutation logs.

Final-source standard preflight: fmt PASS; workspace all-target Clippy PASS (Rust1.97.1, 2m11s); shell layout PASS. Cargo test inventory remains in progress; this builds/lists tests and does not execute all tests. No Clippy allow, threshold, lock, .env, or dependency edits were introduced.

Final preflight completed PASS, including real Cargo inventory: 6582 stable source IDs, 22 necessity rules, 3 ignored tests at unchanged ceiling. Final-source adjacent tests: new raw 1 PASS; original audit raw 2 PASS; audit bin unit 6 PASS. See FINAL-VALIDATION-RECEIPT.json. No full workspace test or release build was claimed. All Cargo work is paused for Root final commit folding.

Exact final commit standard preflight completed PASS at HEAD5632512832600f5efef47f658d7e015ec732e48a / tree099224aa3d762306d613e87005959d7dae79277a, with unchanged verified source hashes and clean worktree. Commit subject length46 and Signed-off-by verified; commit_lint [] means no findings (not zero commits). Source tests remain separately scoped, not full workspace execution.

Own container down returned cleaned; independent cosh-lab env status then returned unavailable/exit1 with empty backend stdout, confirming no remaining owned runtime container. Mutation source and test process fixture lives were inside the removed environment; local independent cache was moved to Trash (LOCAL-CACHE-TRASH-RECEIPT.json). No ECS, production setting, push, or commit operation was performed by this test role.

Final test-scope verdict: PASS. Overall release/installed-RPM/provider/dualarch acceptance is outside this task and remains Root-governed No-Go. No screenshot claim: these are scripted PTY Rust tests, not canonical visual/manual acceptance.
