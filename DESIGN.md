# R10 independent design review

Design-only review of the four proposed corrections following review `5509556209`. Existing C source was read for interfaces and lock behavior; concurrently edited source is not certified as a final implementation. No source/test/environment edits or test/container executions by this reviewer. Only this report is written.

## Decision

The proposed boundaries address the reported failures without changing configurable data roots or adding a state ledger. No design-level blocking issue is established **provided the constraints below are implemented**. This is not implementation approval or a zero-findings final-source audit.

## Legacy accounting and deletion proof

Separating directory identity from deletion authority is necessary. A registered directory with the same recorded dev/ino still contains real user bytes when its owner marker is removed, changed, or unsafe. Those bytes must remain charged. Otherwise marker loss can bypass the global 100 MiB cap even while data remains intact.

Scope discovery should use a pinned NOFOLLOW directory and compare recorded dev/ino; it must retain the original generation in BudgetScope. Only array eviction requires the full original token/current-UID/mode proof, rechecked against the reopened pinned directory immediately before unlink. No missing/invalid marker should be minted, repaired, or upgraded during historical discovery or candidate eviction. The existing split at `store.rs:1296-1340` is the natural place to retain accounting while refusing deletion. Broken directory identity remains skipped and registration must preserve the original proof rather than renewing ownership for a recreated directory.

Do not turn unknown identity into zero bytes: ordinary permission/read/stat errors should refuse optional persistence, while a definite missing directory or a positively established replacement identity can be skipped. Once the identity is accepted, marker read failure must not omit that directory from accounting. Unsafe-marker arrays must survive both age and capacity attempts, and repeated refused commits must leave actual bytes at or below the pre-existing cap rather than writing another envelope. Existing malformed/unknown envelopes remain counted/non-evictable.

An empty legacy candidate set should return before opening/canonicalizing the old workspace. This preserves the absolute-custom configuration contract: absent/unreadable historic workspace must not obstruct a configuration that has no legacy authority there. Do not use this early return to skip modern scope enumeration or registered identity-based accounting.

## Compactor lease

An independent `.id.compact` exclusive lease is appropriate: a compactor can operate while the runtime holds `.id.live`; using live for both would reject the intended same-session automatic compaction. Two compactors must conflict before either snapshot/provider call. Claim must happen under raw global lock after proving actual eligible data exists, followed by registration and lease acquisition in that same serialized section. Hold the lease through snapshot, provider await, reload, generation/digest checks, persist, and all returns. Release global before provider work.

Every budget activity association must try live, compact, and generation locks nonblocking, including every registered scoped alias protecting the same legacy directory. Hold all successfully acquired guards through unlink. Global-to-candidate waits are forbidden: persist's generation-to-global order would otherwise form a cycle. A compactor can hold compact while persist holds generation then global; a sweeper holding global must simply skip that compact candidate. Same-UUID records in different scopes remain charged, and a compact lease in one alias must protect the shared legacy source through the locator union.

Guard ownership must begin immediately after successful exclusive claim, before any fallible registration/follow-up work; alternatively register first, then claim, under the same global lock. Do not leave a newly-created compact control behind on registration failure. RAII drop/cancellation must clean only created, matching-inode controls while the original lease is still held and cleanup is serialized by raw global lock. Never drop the old guard and later retry unlink using its inode. Pre-existing or replaced controls survive. If cleanup cannot obtain global proof or unlink fails, warn and release the descriptor; preserve the original error/result. Explicit clear may invalidate the snapshot, but revalidation must produce Conflict and cannot resurrect cleared generation-zero legacy state.

Avoid holding the blocking global lock across async provider work or awaiting cleanup. A cancellation drops a local guard; descriptor/flock release must occur even if cleanup fails. A process crash may leave an unlocked compact filename; that is not evidence of active work and later probes may acquire it. This design does not promise filesystem deletion when permissions make it impossible.

## Missing resume

Use raw global locking without registration for the initial existence decision. If the scope exists, check its live conflict and actual scoped/qualified legacy data before deciding missing; do not bypass an active existing lease merely because its envelope is not yet published. Any provisional created control must be removed under the same serialization while its descriptor remains held. If scope is absent, prove qualified legacy data exists before creating scope or registering the locator. A missing source must produce the original Missing error without new scope, live/generation files, or index location. Global-namespace lock initialization itself should be described separately from per-session/index mutations.

Existence is not permission-success: unreadable/unsafe data is Unknown/Io, not Missing. Keep the original error and do not silently fresh-start. Legacy qualification must use the existing configuration predicate, with no fallback to arbitrary workspace/sessions. A legitimate legacy resume may enroll/register and then acquire live before load/restamp; all error cleanup retains the actual-data and created-inode protections introduced in R7.

## Required evidence before closure

- Marker removal/change/symlink/unsafe mode: unchanged directory remains charged after switching to another root; full-cap incoming commit is BudgetExhausted; arrays preserved. Recreated directory identity remains unowned and is never reenrolled automatically.
- Absolute configuration with no legacy candidates and inaccessible/missing old workspace: scoped persistence/accounting works; unrelated legacy is not opened or mutated.
- Real HTTP-blocked compactor: runtime live already held, compaction proceeds; another process's age/cap sweep cannot delete its JSON or shared legacy source; a second compactor conflicts before provider execution. After cancellation, created compact control disappears and original/replaced controls remain.
- Writer waiting for global while sweeper encounters its live/compact/generation: sweeper skips promptly; no reciprocal blocking. Verify candidate controls remain held through unlink rather than merely probed.
- Missing scoped and qualified-legacy resume: repeated process attempts leave no new per-session controls, scope, or locator registration. Existing live-before-first-envelope case conflicts; unreadable source returns Io. Existing valid modern/legacy resume still works.

Use the real integration target/process cases for lifecycle and global-cap claims. Unit helper tests alone cannot establish cross-process lease exclusion, cancellation, or HOME/global namespace preservation. Do not weaken current error codes, timeouts, data-preservation assertions, or inode/flock checks to obtain GREEN.

## Follow-up: inode reuse and birth-time identity

The first R10 GREEN attempt exposed an important limit of the dev/ino-only accounting identity: remove/recreate can reuse an inode. Marker/token rejection protects deletion, but cannot by itself establish whether the bytes still belong to the originally registered directory. The reproduced historical-array test must retain its original successful-commit and preserved-array assertions; accepting BudgetExhausted would hide that compatibility regression.

Adding a persisted birth-time fingerprint from **the same pinned directory descriptor's metadata** is a small, appropriate strengthening. Compare dev/ino plus the available full birth timestamp; known unequal birth timestamps prove replacement and can skip the unrelated directory. Include it in both registration/full-generation equality and reopened deletion validation. Do not substitute directory mtime or ctime: normal marker/control creation/removal changes them within the same directory generation. Prefer an exact representable seconds/nanoseconds or lossless nanosecond representation, without millisecond truncation or zero sentinel. Conversion failures must be Unknown rather than invented timestamps.

`Metadata::created()` returns filesystem creation time and may be unavailable. On Linux its documented source is statx btime; Linux separately exposes a returned-validity mask. Neither the Rust API nor the Linux contract promises a globally unique generation identifier. This adds evidence against observed inode reuse, not a mathematical never-reuse guarantee. See [Rust Metadata::created](https://doc.rust-lang.org/std/fs/struct.Metadata.html#method.created) and [Linux statx](https://man7.org/linux/man-pages/man2/statx.2.html).

Fallback must distinguish **known mismatch** from **unknown birth**. If either recorded/current birth is unavailable, unchanged dev/ino remains conservatively charged; it must not be omitted merely because Option values differ. Disable automatic array eviction when birth continuity is unknown, even if an owner marker is present, and preserve broken historical proofs without automatic enrollment/upgrade. This may conservatively charge a recreated directory on filesystems lacking birth-time support, which is the explicit portability limitation. Unsupported `created()` alone need not become typed Io: protected accounting already prevents the capacity bypass and preserves readonly/unavailable-filesystem operation when the remaining bytes fit. Actual pinned metadata or file enumeration/read errors still fail optional persistence with Io. Typed Io for all unavailable birth values would unnecessarily make otherwise measurable legacy configurations unusable; it does not solve the identity ambiguity.

Private index schema **3** refusing schema 2 is appropriate for this unpublished PR: older records have no birth proof and must not be silently promoted. Keep refusal data-preserving, without deleting/rebuilding the index, normalizing markers, or inheriting future path authority. Test old-2 and unsupported-version refusal explicitly. Add a deterministic unit fingerprint test for same dev/ino with changed known birth, and Unknown birth accounting/non-eviction; retain the real remove/recreate process negative as an OS-level regression. Directory birth-time precision/support remains filesystem dependent, so do not make a test claim it forced inode reuse unless the raw identity evidence proves it.

The old repeated-missing-resume fixture should now assert that the data root/scope does not exist, instead of calling a helper that unconditionally reads a directory expected to be absent. Then retain the independent locator/index and zero-control assertions. A vacuously empty read_dir fallback would weaken the new no-creation guarantee; an explicit absence check strengthens it.

# R11 independent design review

Design review for external finding `5510277629` against R10 candidate `60d3498bb37fe17881f2c97820cb73d799c241a0`. Read existing scoped/store/test interfaces only. No source/test/environment writes, Cargo/native runs, resource cleanup or Git changes; only this report was written.

## Suitability

The proposed activity-directory entry point is a surgical correction. In `store.rs:1421-1422`, each candidate/activity association constructs a fresh ScopedStorage and calls directory(true). Each new instance starts pinned.swept=false (`scoped.rs:46-55`); directory(true) then calls the full-directory stale-temporary sweep (`:80-93`). For N entries in one populated activity scope this causes repeated full directory enumeration while the user-global lock is held, even though the caller only needs pinned access to acquire three fixed-name activity/generation controls. A no-sweep probe removes that extra quadratic enumeration without changing ordinary persistence or deletion eligibility.

Factor the current implementation into private directory_with_sweep(create, sweep_enabled). Preserve ordinary directory(create) as sweep_enabled=true; add activity_directory() as create=true/sweep_enabled=false, used only by locked_clock_and_evict. Keep existing descriptor pin/path-identity revalidation, safe component creation, 0700 permissions and descriptor-clone/error behavior identical. All NOFOLLOW/exclusive/nonblocking fixed-control operations must remain unchanged. No root caches, broad cleanup rewrite, new budget ledger or dependencies are needed.

## Risks and invariants

- No-sweep opens must **not set pinned.swept=true**. A later ordinary create/write open on the same instance must still perform its first stale-temp sweep. Skipping scanning is not proof cleanup happened.
- create=true remains necessary when registered legacy activity points to a scoped runtime directory not yet present. Do not change it to false or silently omit that association; every legacy alias still needs live+compact+generation guards held through unlink.
- Do not change permission hardening or path-replacement recovery while factoring. An error must still skip/refuse the same operation as before; the new method must not return an unvalidated old descriptor or grant deletion merely because no sweep ran.
- Only the candidate inactivity loop should use this API. Runtime fresh/resume/compaction claims, generation/persistence, normal data access and budget/index directories retain their existing sweep behavior. Existing writer stale-temp cleanup remains a product behavior, not merely a performance-test fixture.
- This fixes repeated temporary-file enumeration, not all budget complexity: accounting still enumerates actual data, capacity ordering remains sorting, and each candidate still opens controls across aliases. Describe the bounded correction precisely rather than claiming the entire budget operation is O(N) or asserting an unmeasured latency/SLO.
- Test-only instrumentation should count sweep function invocation at entry, including best-effort read failure, and compile out of production. A thread-local counter is suitable for synchronous focused tests; reset after seeding and immediately before the measured inactivity operation. Do not measure across spawned threads without collecting their counters, or accidentally count setup writer scans as probe scans.

## Direct regression requirements

1. Separate many-candidate age and capacity paths. Use real valid envelopes in a populated scope, reset instrumentation after fixture persistence, run budget eviction, and require **zero temporary sweep invocations from the inactivity loop**. Assert actual intended envelopes were removed and retained envelopes/bytes/order are correct. Zero calls alone can pass if no candidates were visited or eviction was disabled.
2. Include a retained old .tmp sentinel in the candidate activity directory so the no-sweep path's behavior is visible; a subsequent ordinary writer open must remove the stale temp. Include a fresh temp that survives and retain the existing private-permission/NOFOLLOW checks. Alternatively a direct ScopedStorage same-instance sequence activity_directory→directory(true) with one actual sweep and old-temp deletion proves the swept-state invariant.
3. Keep the existing stale_temporary_files_are_swept_before_first_write positive unchanged and passing. Its deliberately backdated stale temp and second store are meaningful; do not replace it with only a counter assertion.
4. Existing live/compact/generation lock and alias protection tests must still pass, especially production HTTP-blocked compaction/sweep, held runtime eviction, partial-probe-created-control cleanup and unlink-time lease retention. No timeout relaxation or missing-lock fallback.
5. Mutate the inactivity call back to ordinary directory(true): the new many-candidate test should compile and fail specifically on nonzero sweep count while its candidate setup is intact. A second narrow mutant that marks a no-sweep open as swept should fail the same-instance subsequent-writer positive if that invariant is added.

No design-level blocking issue found with these boundaries. Implementation/source/artifact-bound GREEN, mutation proof and final review/CI remain required; this report is not acceptance of code not yet read.
