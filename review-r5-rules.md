# Issue 7891 R5 rules alignment review

结论：本轮只读规则审查未发现需修改的 P0/P1/P2。此结论仅覆盖以下 dirty snapshot 的组织、授权范围、测试布局和文档规则，不代表行为验收、TTY/真实 provider 或 production Go。

## Snapshot

- 时间：2026-10-16T10:30:14.322869+00:00。
- Worktree：`/Users/quejianming/vscode/cosh-shell-dev/anolisa/.worktrees/cosh-7891-ui-worker-production`。
- HEAD：`fd31f09b29e3a9a9fb617c9e404a7fa81c2e39bb`。
- HEAD tree：`a1ad327ce78bccf62021adb2c962ab9fcac433ff`（不包含 dirty 修改）。
- tracked binary diff SHA256：`f010be7b3827d43a3df038e5f911f469683e7ad1df774f9006b91a61d6935f42`。
- 实际列表18个 tracked 修改与1个 untracked design doc；无 staged 修改。完整 diff 与新增文档均已阅读，绑定下面内容SHA，而不是把HEAD当作包含dirty修改的commit。
- 授权：release worker admission/package wiring，以及用户已批准的局部 persistent TTY bounded postcommit handoff/prompt recovery。组织SDD自身迁移阶段的历史scope fence不解释为禁止本次明确授权的RPM/fixture修改。
- 未改源码/index/规则镜像，未执行cargo、容器/环境操作或行为测试。只读取Git/文件、计算SHA/行数并运行 `git diff --check`（exit 0）。

## 对齐结果

| 规则 | 当前事实及判断 |
| --- | --- |
| owner/dependency | admission和固定policy在既有runtime/approval_ui；bootstrap编排、logging沿原owner；shell_host仅持capture/display lease与relay恢复，runtime消费窄状态接口。无新增shell_host到runtime/approval/UI反向边。 |
| root/API | 无新crate、root implementation、lib.rs/export、Cargo manifest或self-crate path；新增方法限pub(crate)/pub(super)，未为测试开放public API。 |
| production行数 | 本轮最大bootstrap 672（原676），pty_emit 563、logging 552、controller 484，其余更小。无新增≥700文件或向>1000 production文件追加；无需新waiver。 |
| source tests | approval_ui_tests新增policy/权限/symlink/ancestor检查仅用临时文件；degraded_tests新增Hold断言。均private轻量component，无新增spawn/PTY/mock provider。 |
| integration层 | worker kill/hang/idle/missing/injection及prompt refault在既有raw_cli子模块；真实Core/PTY、C interposer、/proc取证在tests/support。无新target、聚合器test或src/logic/protocol heavy helper。 |
| inventory | source-heavy inventory、D22两条test DTO登记、check-layout均未改；无新例外、阈值提升或注册债务扩额。 |
| 范围/依赖 | RPM两处worker payload与既有anchor test，canonical fixture只加production去测试注入。无依赖、lock、.env改动和相邻整理。 |
| 文档 | 英文无后缀component docs/design文档记录release/debug、可信sibling、bounds、Host权责及新PS1 lease/再故障/provider-final后repaint/非物理strict/非通用takeback。新增的是架构设计和父测试开关，未加用户CLI/TOML或安装方法，不触发用户配置清单/QUICKSTART同步。 |

既有 `tests/support/ui_approval_slice.rs` 从2315到2416行，是integration harness，不能误用production 700/1000阈值。新增取证/故障oracle仍复用既有支持层。当前checkout没有独立shell-test standard/review正文，不凭空声称已核对未知测试文件行数上限；已核对scoped AGENTS完整测试策略、source-heavy inventory及实际check-layout测试布局规则。

文档明确旧debug/package证据不能替代新freeze双架构installed-RPM/provider验收。父任务告知的release prompt-refault首GREEN `102516-af9e0160` 属于另owner行为证据，本审查未重跑或提升其为整体Go。

## 规则来源与 baseline drift

实际镜像 `/Users/quejianming/vscode/anolisa-auto-review/rules/cosh-ng-code-organization/`；未使用不存在的cosh-shell-dev/anolisa-auto-review。读取root/scoped AGENTS、documentation-standard、仓库decisions/organization inventories、source-heavy inventory和镜像standard/review/decisions/large-file-inventory。

以下差异已存在于HEAD，且本轮不改specs；不是新例外或本轮finding，不修改镜像：

- 仓库decisions含D18 interactive-sentinel、D19 slash-bearing prompt routing、D20 Gateway composition、D21 Task presentation；镜像缺这四节。两侧均有D22，其余decisions文本一致。
- runtime/state inventory仓库1003、镜像1000；仓库另含/bug shell_identity、Task lifecycle/D21说明，镜像保留旧slice candidate说明。本轮不改state.rs。
- shell_host/osc inventory仓库987并记录alt_screen/marker_sequence拆分，镜像805旧说明。本轮不改osc.rs。
- 镜像另有shell_host/marker/bash.rs 934行登记，仓库没有该行。本轮不改该文件，未借镜像放宽增量。
- 仓库organization目录仅decisions/large-file/forbidden-dependency inventory，没有standard/review，规范正文按指定镜像读取。仓库shell-test目录仅source-heavy inventory，镜像无shell-test目录；测试布局以可见scoped AGENTS/脚本核对，不假称缺失正文已读。

## 文件内容绑定

LF行数对应wc -l口径；路径相对上述worktree。

| 文件 | HEAD→当前行数 | 当前SHA256 |
| --- | ---: | --- |
| `src/cosh-ng/cosh-ng.spec.in` | 467→469 | `f6c01cd24225669c11c4eee5583e364b7e567a63c78f8d8fc52d81622042f1f5` |
| `src/cosh-ng/crates/cosh-shell/src/approval/slice.rs` | 282→282 | `2db9b773f4a83af466afa4e2c967667e3ad1d595fb6e0785a7090e83a0525c52` |
| `src/cosh-ng/crates/cosh-shell/src/runtime/approval_ui.rs` | 236→294 | `64fcfde0375d6c418e896bf9fa10f41ffb72eec524e405676dfb7ceacd5f6d62` |
| `src/cosh-ng/crates/cosh-shell/src/runtime/approval_ui_tests.rs` | 261→377 | `b6c1d0436a2a04a7936d59741e4106545b1147a06f98208b0c5cb9e222bbd1c7` |
| `src/cosh-ng/crates/cosh-shell/src/runtime/controller.rs` | 468→484 | `0056f713eff19dda90d30d6f452c133245960ae0f7f3a654db0e9e40b0a88c1b` |
| `src/cosh-ng/crates/cosh-shell/src/runtime/controller/bootstrap.rs` | 676→672 | `7e96895a25a375ad5d87df3859e7246365ccb1536862afedbb40289affcf0203` |
| `src/cosh-ng/crates/cosh-shell/src/runtime/logging.rs` | 555→552 | `53ed80325ea3636eabb2f9f3c2c390cf923e93688745f8c4851b1300624bd157` |
| `src/cosh-ng/crates/cosh-shell/src/shell_host/model.rs` | 459→460 | `8a19731e3fb1445f2db8c32e9c1eb9db308227f65d396fcb451b02eb50ff87ed` |
| `src/cosh-ng/crates/cosh-shell/src/shell_host/raw_relay/degraded.rs` | 151→160 | `baeceb73a7a5a76b345bab2e68e62cf79508065091daeb2547db80173e5eefe0` |
| `src/cosh-ng/crates/cosh-shell/src/shell_host/raw_relay/degraded_tests.rs` | 186→197 | `a36a97f9af4df934b8bec5be09b138cf4540b2007ee4c2d5afd3a3972a6ebf20` |
| `src/cosh-ng/crates/cosh-shell/src/shell_host/raw_relay/observer.rs` | 143→143 | `050e9b928d321dc950771c6063317ab5398522ba14d24ea5c83b81cb81ac0243` |
| `src/cosh-ng/crates/cosh-shell/src/shell_host/raw_relay/pty_emit.rs` | 541→563 | `e50bab3706cfb85fd092f31f7837c0219104923cc728e01a446ec6b4013965a1` |
| `src/cosh-ng/crates/cosh-shell/tests/raw_cli/ui_approval_slice.rs` | 539→626 | `e75cff4e8a5fb63a9f8bc24c42a0c597500077dc147363c64be66586654cbb10` |
| `src/cosh-ng/crates/cosh-shell/tests/raw_cli/ui_output_fault.rs` | 74→97 | `e8a5842249d4094f09c54a0834ddeb9df05867f7553a6f33f7d4ce7825b61594` |
| `src/cosh-ng/crates/cosh-shell/tests/support/ui_approval_slice.rs` | 2315→2416 | `462c80a24c948d6fcf2c0dbf9e549c9aafa85827c17201c80f7557dae0d0f662` |
| `src/cosh-ng/crates/cosh-shell/tests/support/ui_output_fault.rs` | 123→163 | `c5dfa1f0d5a89be6b188c8e9d8ce82207d3ff85e490721ee4b0cd17e21094230` |
| `src/cosh-ng/e2e/fixtures/ui_worker.py` | 224→229 | `8b50259f1262a9cfc16b588e1164499310663a1e3f8fedc6580635683e47ec99` |
| `src/cosh-ng/tests/test-package-rpm.sh` | 950→954 | `5797b4b25e371bd8aaaca5032f5016a671325e2a524503bcaf37d44ac5efd441` |
| `src/cosh-ng/docs/design/approval-worker-production.md` | new→52 | `b594d42b5fb4e1a06ca6acc9afe27ed92bd53b476d3d9c46d12aded87c50aab6` |

## 规则输入绑定

| 文件 | SHA256 |
| --- | --- |
| `AGENTS.md` | `a02720bdbbeb5c84df565545411d0fe5d8612be2ed2cd5b3b1f4589674100479` |
| `src/cosh-ng/AGENTS.md` | `438f587280a675230f2bbd4f3413753f0de1a38b519519f9bd1c115bf15d53f2` |
| `specs/documentation-standard.md` | `01cd0a6bf0e454d61c0ec7d3353d8d7979f7da272459dc67a91ac1cb7a407a3e` |
| `specs/cosh-ng-code-organization/decisions.md` | `10e6e7b6af9dc8e29769809d4486920e2bc92a2825e5c0ab700b6b9edaea85ee` |
| `specs/cosh-ng-code-organization/large-file-inventory.md` | `08db78a574d91585e8f3a861773e1b83f56ab6ddc9a9f9768fb214f44efa1659` |
| `specs/cosh-ng-code-organization/forbidden-dependency-inventory.md` | `ea51d6c5631f49a4ecb589b8c0973270eeb53430a22f26f2b6f4e4662c81f407` |
| `specs/shell-test-organization/source-heavy-test-inventory.md` | `5834dd2aa403283d4945e68d7fa85254aa434b4cd252c9656d0617bbb2644b40` |
| `src/cosh-ng/crates/cosh-shell/scripts/check-layout.sh` | `72370ec601f31e731ec33a6758bcc0cc88b70ee2b978ced6fea2d2a5b5def247` |
| `/Users/quejianming/vscode/anolisa-auto-review/rules/cosh-ng-code-organization/standard.md` | `80506e5e038cbccebf624a10a526d2ff0fb6f05095cfe09823f9a0f7f1844a76` |
| `/Users/quejianming/vscode/anolisa-auto-review/rules/cosh-ng-code-organization/review.md` | `1717bf588e8a05cfe7b86e9890011c0e0289e67838b2c442cf161191b93837a1` |
| `/Users/quejianming/vscode/anolisa-auto-review/rules/cosh-ng-code-organization/decisions.md` | `f696e7aa766748f4eedc3b68efa84c0d9e9c331d222752286a98c4d3145627ce` |
| `/Users/quejianming/vscode/anolisa-auto-review/rules/cosh-ng-code-organization/large-file-inventory.md` | `27b0cf73e287fea216c21fbd8b1bce0565ce5b198a86496d97fbfa1d35b5c493` |

## 验证边界

未运行完整check-layout；这是完整增量/规则静态审查。其他owner负责运行/行为验收。简单kill-loopback不能证明descendant持IPC、旧generation迟到失权或公开终端takeback合同关闭。既有debt和镜像漂移不因本报告而清零。
