# R10 narrow CI failure analysis

Frozen C candidate: `60d3498bb37fe17881f2c97820cb73d799c241a0`. CI run `38469765011`, attempt1 fast job `115545801239`. Only this report was written; no source/test/Git/environment edits, Cargo, native or container execution by this reviewer.

## Actual CI failure boundary

`CI-fast-failed.log:1939-1951` records checkpoint::tests::an_untrusted_peer_is_rejected_as_known_no_effect panicking at `crates/cosh-platform/src/checkpoint.rs:1897:42`: command.spawn().unwrap receives error26 ExecutableFileBusy/Text file busy. Platform result is **334 passed;1 failed**, exit101. The helper executable did not start successfully, so this execution never reaches the assertions that the untrusted peer is rejected as KnownNoEffect/PermissionDenied (`checkpoint.rs:1921-1923`). This is an actual fixture process-launch failure, not a failed peer-authentication assertion, and it is not a successful negative-security test.

The fixture (`:1874-1897`) creates a unique temp directory, copies the current test executable to untrusted-peer-helper, chmods it executable, then starts that copy as a one-test daemon helper. When running as root it chooses UID65534 for the helper. Linux documents ETXTBSY at exec as an executable being open for writing by a process. The log does not identify which process/descriptor retained writable access, and source inspection alone does not prove a persistent-descriptor leak, concurrent fork race, or filesystem-specific cause. See [Linux execve error contract](https://man7.org/linux/man-pages/man2/execve.2.html).

## C ownership and dependency boundary

Direct Git object comparison against base `69ae39dc5b97e47a399ed6c42d841d421e29c6dd` confirms checkpoint.rs is identical: both objects **27e343bf11403aa6bd849c81acbb5e1a44d6b62a**; the file diff is empty. The complete frozen candidate diff contains only the fifteen audited cosh-core source/tests, including compaction/session changes. It contains no cosh-platform, shared manifest or dependency-lock change. This checkpoint test executes a copied cosh-platform test binary, not a Core session-budget process. No causal link to C changes is established by this failure. Shared CI scheduling/runtime can still affect launch behavior; unchanged source does not by itself prove environment-only root cause.

## Native readback: precise passing and failing evidence

Read `CI-platform-native-reproduction.json` and its reproduction driver. The actual Cargo-JSON selected platform test executable is cosh_platform-d8b823ad283b4d54, SHA **fc54a48cd03489c3c609919199f81cc2ff552ee172995871426249bdf3b78fc3**. Its checkpoint source SHA **e19c951b49ad5bf5c8534d2c3a558b61a185d9f980b1cbc0b441d9b8bdc53cf0** independently matches the frozen Git object's SHA256.

The unchanged exact test runs as UID65534 with private HOME and passes **1/1**. The same executable's default-parallel full platform group also passes this checkpoint case, but ends **333 passed;2 failed**, so the wrapper's actual exit is **1**. Both remaining failures are pkg::tests::test_pkg_install_dry_run and test_pkg_install_dry_run_nonexistent: the native dnf backend requires superuser privileges under UID65534, returning PkgBackendError rather than expected success/PkgNotFound. Preserve this diagnostic rather than claiming the platform group passed or treating those package failures as the CI ETXTBSY reproduction. No test changes, assertion relaxation or timeout extension are used by the driver.

## Classification and remaining limits

The candidate's CI failure is confined by evidence to unchanged platform fixture exec setup, before the product assertion. Native exact and parallel readback **did not reproduce ETXTBSY**, which supports an unchanged-assertion CI rerun to check recurrence. It does not identify or eliminate the cause, certify full platform GREEN, or retroactively pass attempt1. A later exact-HEAD CI result must be read independently; resource cleanup remains a separate gate. Current C fifteen-file source/manual audit findings_count remains0 and is not replaced by a blanket environment-only completion claim.

Root-native follow-up uses the same Cargo-resolved executable, unchanged assertion and default parallel scheduling. Exact checkpoint1/1 and platform335/335 pass (CI-platform-root-reproduction.json). The two nonroot pkg failures remain preserved and are not counted as GREEN. This does not establish the ETXTBSY root cause or a source fix.
