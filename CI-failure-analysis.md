# R11 narrow Shell CI failure analysis

Candidate HEAD4cf6aeb8ed47bc0137db3bcb256deb74b291854b; CI38475379875 attempt1 main job failed, fast/release reported passing by the coordinator. This reviewer read source/Git objects and raw failure only; no source/test/environment changes, Cargo/native execution or Git edits. Only this report is written.

## Verified failure and C boundary

CI-main-failed.log:1495-1505 records native::raw_cli_login_probe_preserves_login_argv0 failing at native.rs:152:57: read_to_string(logout-log) receives ENOENT. The group result is **579 passed;1 failed;1 ignored**, exit101. This failure occurs before checking the captured __R2_LOGIN__yes|-bash|off text and before checking exactly session\n logout content; it does not itself demonstrate wrong argv0, duplicate capability-probe logout, or an accepted login contract. The failing assertion does not print the already-captured raw output, so the log lacks that diagnostic context.

Direct full Shell diff against base69ae39dc5b97e47a399ed6c42d841d421e29c6dd is empty. Native test Git object is **ef7cb52abc4c3d8b96cb2e0485dc8a69f160b1ad** in both base/candidate; support helper object is **3e3ea1de7dbe06b7752e901abb04d610e9f94667** in both. All fifteen C-owned changes remain in cosh-core. The test invokes cosh-shell raw fake; AdapterKind::parse/adapter_for_kind select the built-in FakeAgentAdapter, separately from CoshCoreAdapter. It does not execute a Core session-budget process. No direct C source/dependency change causing this logout failure is established.

## Wait and shutdown boundaries

native.rs:123-151 creates a unique temporary HOME, writes .bash_profile and .bash_logout, sets real-login identity/enhanced Bash, then asks the helper to run printf plus exit. support/raw_cli.rs:65-100 starts the child, writes **all scripted input immediately**, closes stdin at block exit and waits for the outer Shell process. There is no startup/login-output/logout readiness barrier. The temp HOME is removed only after reading the log, so this test's own cleanup does not explain its absence.

support/raw_cli.rs:988-1030 waits at most30seconds, captures stdout/stderr through reader threads and enforces successful outer status. On normal completion it also sends TERM then KILL to remaining process-group members after50ms. The actual failure is not the helper's timeout/status assertion; those had returned. Their success establishes outer process completion and collected pipes, not independent proof that the inner Bash took a normal exit path and completed its logout hook.

There is a concrete relevant shutdown boundary in unchanged production Shell code: raw_relay.rs:119-128 converts input-event EOF into request_eof_shutdown. raw_relay/eof_shutdown.rs:25-49 immediately sends SIGHUP to foreground and shell process groups, then allows250ms before SIGKILL (:53-76). raw_runner.rs:460-496 subsequently waits for inner status and emits exit output. Because the fixture closes stdin immediately after queued exit text, scheduling can expose EOF shutdown before normal scripted exit/logout finishes. This is a plausible source/test lifecycle interaction, **not a proven cause of this CI instance**. The captured failure lacks inner-shell output/event ordering and does not identify a logout path, startup fallback, signal or filesystem error.

## Decision and limits

Unchanged-assertion exact/native-group repetition and a same-SHA failed-job rerun are justified to check recurrence and retain the original failure. Native evidence was not yet supplied at this checkpoint; no reproduction success, root-cause resolution, CI success or cleanup is claimed. Even a later green repeat cannot by itself eliminate the EOF/logout lifecycle boundary or prove a blanket environment-only cause. Keep C frozen-source findings_count0 separate from this main CI failure, and bind any later passing CI to the exact candidate SHA before delivery closure.

Native reproduction at frozen4cf retains the exact assertion and default scheduling. Exact login probe1/1 passes; native group28 pass/1 existing ignored/0 fail. Cargo resolves the recorded raw_cli executable and its SHA is saved in CI-shell-artifact-binding.json. This is not the entire581-case integration suite, does not establish the observed CI path, and is not a Shell fix.
