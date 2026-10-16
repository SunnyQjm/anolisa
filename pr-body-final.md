Restoring an idle native prompt is an internal notification, and deferred timeout notices must finish by restoring the editable Shell line. Previously the notification could suppress a failed-command Insight, or a timeout notice arriving after Bash PS1 could leave the cursor on a blank line. Marker-input test drivers also reused PID/wall-clock request identities, allowing concurrent drivers to overwrite each other’s readiness requests.

## Changes

- Exclude only `shell_prompt_ready:painted` from followup input; keep occupied prompts, real writes, card actions and later commands suppressing intervention.
- Gate the existing Bash/zsh failure fixture on its original startup prompt, actual Insight/result and restored native prompt before followup input.
- Return the existing relay `RestorePrompt` action after the deferred handoff timeout notice at the idle/no-pending-handoff boundary. Keep bounded interrupt, approval and HostResult settlement unchanged.
- Restore the caret in the existing healthy physical recovery sequence (`ESC[?25h`). A failed Gate withdrawal clears its rectangle before session Drop can show the cursor hidden by the worker. Strengthen the existing native-prompt checkpoint to require a visible caret before any next input.
- Give each marker-input test driver an exclusive temporary request directory with a lifetime spanning the driver. Add path/content/cleanup isolation coverage in the existing auth test target.

Ten files, five commits. No CPR or shared-slot introduction, prompt renderer replacement, timeout increase, added sleep, removed test, weakened display/approval assertion, dependency or lockfile change.

## Verification

Frozen HEAD `60b68369eb0d573b0c9ba61106e04cab7ba56f0f`, tree `0f29bc0fbe6d068dc99d53bb955b788bdbb05277`, base `b75eff716d8c42ba17b8355b47373430d25d2505`; Cosh subtree `6a25f82f406beb0ce72af9c6f38a63dc44a43e97`.

ALinux4 arm64, Rust1.97.1, owned isolated2CPU/6GiB container and target. Precursor mechanism validation passed controller11, request-identity normal/equal-clock controls, scoped equal-clock three-auth ESC cases, and four concurrent rounds of the three real output-fault cases. These precursor rounds checked PS1 color/geometry but omitted visible-caret coverage, and therefore do not establish final native-edit acceptance. The exact60b verification below includes the strengthened visible-caret assertions.

Valid RED and compiled mutations: omitting timeout restoration yields None versus required RestorePrompt; old readiness allocation under equal driver-clock values yields one path for four writers. Compiling both old mechanisms with the new tests rejects them with exit101; the original auth focus case reproduces request2 timeout with future request4. The earliest whole-process fixed-clock positive failed another edit-form marker; it remains preserved and is excluded from GREEN because it also changed child clock behavior.

The new caret correction passed fmt, all-targets Clippy, layout, inventory, controller11 tests and the three real fault cases with visible-caret assertions. Omitting only ShowCursor in a compiled mutation makes the existing physical-recovery test fail101. Formal exact-HEAD preflight passed: fmt, workspace all-targets Clippy, layout, inventory, commit lint and no upstream drift. All1,188 Rust/Cargo files matched. Controller11 tests and three concurrent real Core/Bash/PTY cases passed on60b with color, geometry and visible-caret assertions before input. Original PTY bytes confirm ShowCursor at all three checkpoints. Final exact-source four-thread raw_cli on60b passed **621 tests,0 failures,1 ignored** (622 total,709.66s; exit0). The original auth request2 case, recommendation case, all Bash/zsh prompt fixtures, native edit/history and focus cases, and all three output-fault cases with visible-caret assertions passed. The owned container was removed and independent container inventory confirmed absence.

## Preserved failures and open gate

The original e315 four-thread run remains **618 passed,2 failed,1 ignored**, exit101. It is not overwritten by targeted repeats or CI success.

- Timeout PS1 failure: reproduced concurrently, terminal bytes show native PS1 followed by the delayed timeout notice and an empty editable cursor row. The missing relay restoration action is directly corrected.
- Auth request2: same-token future requests cannot be written by the blocked driver. The alias mechanism is reproduced under equal test-driver clock values and removed by exclusive ownership. Exact historical clock calls were not captured; the equal-time origin is inferred from the alias signature and demonstrated mechanism.
- The12ee full run passed621/0/1, but original bytes at the Gate-withdraw before-input checkpoint showed the caret hidden. The strengthened real PTY assertion rejects that case2/1; this is corrected by the existing physical recovery ShowCursor sequence. The old full pass is retained and cannot prove the stronger native-edit contract.
- Historical recommendation request4 timeout remains unattributed. Earlier bounded32-round observations and suppressed-request negative control remain recorded; this repair does not relabel those historical results.

CI on12ee also exposed unmodified cosh-platform checkpoint peer-test spawn ETXTBSY (source blob unchanged). Preserve its raw failure; do not label it flaky or change that Platform owner in this Shell patch. All current60b CI checks have completed successfully; formal human review remains required. This does not attribute or erase the preceding ETXTBSY incident.

Keep this PR draft. Full-workspace, real-provider, dual-architecture installed-RPM and release/product acceptance remain excluded. No merge or deployment is authorized by this PR.

## Evidence

Immutable new execution links will be added after the final run. The [original concurrent full failure](https://raw.githubusercontent.com/SunnyQjm/anolisa/58531312af178d501d141310fb8b032dba308580/final-frozen-four-thread-raw-cli.json) remains available.

Refs #7484; this PR does not auto-close the tracking issue.
