# Issue 9840 review evidence

These assets support code review and preserve the verification limits. Both the final-candidate manual ECS default-answer check and the original activation/persistence/reload path passed; these assets do not establish release acceptance.

- `baseline-project-model.png`: actual pre-fix ECS PTY, Core 0.29.0 on the earlier `ef2b7945` baseline. Selecting ECS access saved the project's synthetic model in both user model fields and retained it across directories. This is historical failure evidence, not a screenshot of final PR binaries.
- `scoped-local-validation.json`: final reviewed client source, macOS arm64, Rust/Cargo 1.96.0. Four exact Core regressions and 27 additional synthetic provider-environment scenarios passed, along with format and scoped Core Clippy. Environment restoration is checked, including absent, empty and invalid-UTF-8 values. No live model inference was sent by these checks.
- `submission-preflight-summary.json`: submission-base preflight facts. Overall status is false: a pre-existing macOS platform-test compile error blocks workspace Clippy and host Bash 3.2 cannot execute the Gateway layout script. Selected headless trial tests, format, shell layout and test inventory passed.
- `ci-review-validation.json`: later verification of submitted head `328a9fdd7b96e9592f9172f822fe6d7bdd9e13dd`. Linux x86_64 CI fast checks, strict workspace Clippy, process/Shell Host integration and the release workspace build passed. The first raw CLI shard failed; its unchanged-head retry passed. The exact initial cause is unproven. The separate maintainer review corrected its own scoped environment to Linux aarch64 and approved the head without an actionable code finding. Local main/candidate macOS failures are recorded separately and do not prove the Linux failure's cause.

The reviewed source patch SHA256 is `f3b748ab3e332b167bd08a4a60b44cec0a9a389426998e6334f0270368f01c7d`, based on `f08f10ac4d2ef1aee4d665b78650e4e651d94e79`.

On November 11, the final PR head was built on a new ALinux 4.0.7 x86_64 ECS. Fresh HOME and neutral directory, absent user/project/system provider configuration and absent provider/model/endpoint/credential environment overrides were checked. Without `/auth`, one real question used `aliyun` / `auto` and returned the exact new nonce in both the Agent terminal card and persisted assistant content. The provider audit recorded success in 1956 ms, with 3264 input and 18 output tokens. Frozen binary hashes, loaded process inodes and end-of-session hashes match. The temporary instance was deleted and independently confirmed absent.

- `ecs-auto-real-validation.json`: sanitized final-candidate provenance, request/response, collector limitations and cleanup summary.
- `ecs-auto-answer.png`: full terminal screenshot derived by the CLI from the actual sanitized cast, visually checked for complete content.
- `ecs-auto-answer.cast` and `ecs-auto-answer.webm`: original terminal replay and its CLI-rendered video.

The user authorized Cloud Assistant to schedule the real ECS-local PTY. The original collector missed the live `.jsonl.active` audit file, so it later reached its watchdog with wait status 15 and `request_terminal=false`. A read-only supplementary collection proved that the single provider request had already completed successfully; no question was replayed and the original collector result was preserved. The native canonical acceptance aggregate remains Blocked because this flow lacks a canonical case/registry proof. The visual wrapper is render-only, not a native acceptance run.

Earlier real registry checks and the other-provider PTY answer belong to an older candidate. The earlier default no-auth `auto` attempt returned no assistant text; its precise cause remains unproven. The later success after the gray deployment update does not establish exact request-to-Pod attribution or retroactively change that result.

The final PR head was then rebuilt on a separate temporary ALinux 4.0.7 x86_64 ECS to verify the original issue path. The original project's `qwen3.9-probe` marker and ignored Provider fields, a neutral control, and a project-model-only case each ran three times with fresh HOME directories. All nine chains passed on the first run: activation returned `auto`, both user model fields contained `auto`, a new registry process loaded the provider from the user file, and a further real Core engine initialized as `auto` after leaving the project. The user configuration stayed byte-identical across both reload processes. All 27 loaded Core processes matched the frozen inode/device/size/hash. Original project Provider warnings confirmed that the project file was actually read. There were zero model inference requests, and cleanup was independently confirmed absent with zero remaining instances.

- `ecs-original-path-validation.json`: nine reduced per-case facts, original activation payloads, actual saved TOML, five model observations, stdout hashes, binary provenance and cleanup.
- `ecs-original-path-driver.py`: the external verification driver, with the original issue's synthetic marker. It is outside the product source patch.
- `ecs-original-path.png`, `ecs-original-path.cast`, and `ecs-original-path.webm`: actual real-PTY registry summary and CLI-rendered visual evidence. This is a registry protocol test, not an `/auth` TUI test.

The independent engine initialization avoids treating the registry menu's fixed `auto` projection as sufficient runtime proof. The original issue's project-to-user model-persistence defect no longer reproduced in this matrix. Ordinary project model preferences and model-source warning policy were not changed. Native canonical aggregate is not claimed for this manual path.

The later CI report supplies the Linux CI build/gate results that were unavailable at initial submission. The two ECS checks above cover the scoped manual default answer and original configuration path, not RPM qualification, complete ARM64 qualification, a current-candidate other-provider rerun or release acceptance. No source change was needed; the one-off YAML driver remains outside the PR, and the 18 retained source/test/doc files are unchanged.

No credentials, instance identifiers, private backend code or cloud account details are included.
