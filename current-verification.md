# Current debug approval UI verification

Source HEAD: `2e7fc1720511479c25374246b0ff50a38596aee4`; tree: `da56e154adf7b3c953948580c84f49de62dbaed2`. Tracked source is clean; `.cosh-lab/` contains runtime metadata and is excluded from commits. Earlier evidence remains historical and retains its original HEAD.

## Changes and review closure

Presentation stays isolated from Host input, approval, audit and execution. Fresh geometry and capture generations gate publication. Physical display failure can preserve only an already approved bounded handoff through its existing timeout/settlement semantics. Clean worker startup failure keeps the viewport; acquired or partially written regions require repair. Existing direct panel retries use the same repair path. Successful managed publication retires the repair requirement while keeping geometry constraints.

Actual REDs preserved: missing-worker startup emitted full scrollout; partial acquisition accepted bytes without a repair indication; direct panel retry bypassed repair. The missing-worker RED stops before the unexecutable variant; the final GREEN executes both. No inferred errno is presented as observed. All 144 approval tests passed, and fmt/workspace all-targets Clippy/inventory/layout audits passed. The independent audit records the author/reviewer and component-model boundaries.

## Final source validation

ALinux4 arm64 containers, Rust 1.97.1, pinned image from final-owned.toml. Owned environment `20261013T184512Z-5a9038a5`; borrowed environment `20261009T032924Z-83fae118` retained.

- Empty dedicated target: actual Core build, no prebuilt Shell/worker, Cargo target inventory 19 and 19 actual tests passed. The clean-target binary hashes are recorded separately.
- Shell canonical units: 1608 library and 2289 binary passed; one existing ignored test; 696 exact lib/bin duplicate executions excluded.
- Logic 9, protocol 83 and UI raw-CLI 25 passed; UI includes three intentional negative-oracle controls.
- Formal raw-CLI test passed for committed handoff with persistent output failure, recovery and no input leak.
- Both canonical resize/CJK and worker-fault cases passed using actual Shell/Core/worker ELFs and a loopback model. Eight original-cast PNG/WebM points passed source/hash/viewport/last-PTS-at-or-before-point checks, with maximum pixel difference 2.
- Sidecars verify stable Bash, exactly one effect, two model requests including the Host tool result, three distinct killed workers in the fault case, resize propagation, restored termios and no remaining owned processes.
- Post-capture hashes equal the final matrix hashes. Owned environment deleted; temporary tools removed from the borrowed environment. Debug arm64/container/raw-cli aggregate gate:Go.

Normal final binary SHA256:

- cosh-shell:`790f049fc20f863dbf8c37de0d393d456cac020d9d1f5adb22cfa8f6c7488b36`
- cosh-core:`9c73f00310b66dea10302e101009edc6dfffa425fe36f3703c6f8d1b80cc2ee9`
- cosh-ui-worker:`cfe30b7de19165edd0883cd9f2aa1b9b993e8659f0a73d0c2bc7dac8c2127787`

## Native commands and artifacts

The JSON logs contain the complete native env-exec commands, source metadata and results. Unit selection invokes the in-tree `run_canonical_units cosh-shell cosh-shell 1`; clean validation uses `cargo build --locked -p cosh-core --bin cosh-core` before `cargo test --locked -p cosh-shell --test raw_cli ui_approval_slice -- --test-threads=1`. UI matrix uses `cargo test --locked -p cosh-shell --test raw_cli ui_ -- --test-threads=2`. Canonical execution uses `cosh_lab accept run` with the committed YAML and each case ID, followed by `evidence verify`, sidecar download, `env down`, and `gate evaluate --require test --require acceptance --require-scope raw-cli --require-backend container --require-arch arm64`.

The archive contains original casts, indices, provenance, eight PNG/WebM points, sidecars, independent visual review and counterexamples. Current-source proof and final matrix logs are separate immutable assets. Previous first-code FD mutation/canary and renderer RED/GREEN evidence remain available in this evidence branch; product process-isolation code and renderer ownership are recorded without adding a product dependency.

## Limits

This is a debug feature gate. No timing/performance Go, real-provider acceptance, dual-architecture installed RPM, default-Shell release, production deployment or merge is claimed. Unchanged Core/full-workspace/packaging historical checks remain in earlier evidence; the current PR required CI is recorded separately in current-final-pr-current-state.json.

## Current PR checks and review

All required checks on this exact HEAD passed, including Cosh fast, integration, release and prebuilt Action. Latest external full-diff review on this HEAD reports no blocking findings. GitHub reviewDecision remains REVIEW_REQUIRED; no merge or deployment is authorized.
