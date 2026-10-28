# #9103 approval exposure P1 validation (2026-10-28)

Current candidate: c6805699206460be3622897e766cc37db653f39c. Source snapshot:9103-exposure-green-v3,1449files,manifest SHA25601ac3f5266325d017f44e954ea8b1679f52e56aaaf78cd29abd8b1c0b98d5d26. Based on main8aff including externally merged #9106. No merge/auto-merge was executed by this task.

## Problem and necessary change

Review4396237580 exposed missing durable protection when ReadOnly/Other PreToolUse Ask or Prompt approval receives an execution-bearing unconfirmed Host completion. Four old-production real-effect RED cases reproduced unapproved file overwrite, including two persist/resume cases. Independent review additionally reproduced a production list_directory bypass success wrongly clearing prior uncertainty (one actual-effect RED).

All three approval handoffs now arm the existing durable checkpoint before handing control to Host, retaining separate prior memory/durable states. Plain known-unexecuted decisions restore only their new exposure; unknown execution is monotonic through bypass. Approval requirements are calculated from the old state. Only an explicitly approved real side effect or validated Host execution success can certify success; a readonly local retry cannot. No change to no-approval readonly operations, public schema, shared auth/question decoding, dependencies, lock files or linked consent.

## Current execution evidence

- Final Core complete:17targets as nobody UID65534,1508top-levelpasses,0failures,2existingignored. Nested child summaries excluded. Evidence:exposure-v3-full-core.json and exposure-v3-counts.json.
- New behavior coverage:9component tests, including12internal normal allow/deny/baseline combinations, old memory/durable split, arm-failure zero handoff and paired plain/uncertain production readonly bypass success. Two additional real-process KILL-before-response/resume tests passed, including Prompt and ReadOnly Host handoffs. Counts are included in full Core, not added to1508.
- v2 focused component42,checkpoint5,live4 and existing recovery5 passed. Same-product remaining Gateway/Shell/provider/response focused20 and docs passed. Final v3 changes only the KILL test fixture, with complete source proof. Final fmt/strict Linux all-target Clippy/layout/inventory:passed on finalv3 source.
- Gateway/contracts and full Shell retained results are historical source-identical evidence from earlier rounds, not new full runtime reruns. Latest GitHub CI must be read at c6805699206460be3622897e766cc37db653f39c.
- Independent complete lifecycle and final fixture review found no remaining blocker. Report:approval-exposure-final-review.md.

## First failures and classification

exposure-red.json:4 genuine behavior RED failures on old production, Host files overwritten. exposure-bypass-red.json:1 genuine behavior RED on initial implementation with real list_directory. Both drove product fixes.

exposure-green-focused-static.json:initial implementation39pass/1fixture failure (missing Prompt mock response); internal readonly-bypass-success P1 also meant this candidate was rejected. The fixture gained MessageEnd, preserving all12state assertions.

exposure-v2-focused-static.json:42+5+4pass; recovery5pass/2failed before reaching Host. PartialHooksConfig requires PascalCase hook keys; the fixture used snake_case. v3 corrected only this fixture and added bounded child diagnostics/RAII cleanup without weakening behavior assertions. exposure-v3-kill.json then ran both real Host-handoff/KILL/resume cases successfully, followed by complete Core1508pass. Earlier failed receipts remain intact and are not called successful execution or flakiness.

One upload attempt was rejected by the CLI's active-command lock before execution; it was repeated after the active command completed, without removing any lock. An initial doctor call from the evidence directory failed source_root validation; the corrected worktree doctor passed. Neither is product behavior evidence.

## Environment, commands and limits

Bundled cosh-lab0.8.0 only; isolated ALinux3 aarch64 Apple container,4CPU/8G,Rust1.97.1. Profile:container-profile.toml. Environment RUN20261028T021546Z-6f53d1e7. Source manifests verify each uploaded file hash and refresh Rust mtimes to prevent stale build artifacts. Full argv/stdout/stderr are stored in command/result JSON.

Native scopes:cargo test --locked -p cosh-core --tests --no-run --message-format=json, then each emitted executable as nobody --test-threads=4; precise cargo test --locked -p cosh-core --test session_recovery approval_exposure:: -- --test-threads=1; cargo fmt --all -- --check; cargo clippy --locked --workspace --all-targets -- -D warnings; layout/inventory scripts; cargo doc --locked --workspace --no-deps. Doc emits one existing private-link warning. Existing unrelated macOS Clippy baseline is separate from successful Linux evidence.

No real provider, installed ALinux4 RPM/PAM/SSH/default-login, dual-architecture, performance or release acceptance is claimed. No screenshots/media are required or claimed for these component scopes. Cleanup:cleaned; exposure-cleanup.json. Evidence verification:30 execution/doctor/upload/cleanup receipts verified,0failed; exposure-evidence-verification.json. Decision:eligible for formal source review after current CI readback; no merge authorization.
