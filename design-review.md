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
