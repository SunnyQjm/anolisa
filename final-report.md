# #7545 最终独立 test-only 验收

结论：**source/test/owned cleanup Go**。本结论覆盖批准的单文件测试 fixture 修复；不等于 PR 合入、release、RPM 或 real-provider 验收。

最终准确 HEAD 为 `52745f8b3f5eb79ec75b70493f860417accf7a0e`，tree 为 `6cb94baf9b89b28e7c79f0a300cdbe8037ee3d63`，base 为 `b75eff716d8c42ba17b8355b47373430d25d2505`。唯一源码差异为 `termios.rs` 16+/9-，SHA256 `8522f486157117ddae6d16d00dcc5b1f649de8731f067aac89b27feb8aa25f83`。提交前、最终 host before/after 和最终 guest 的 1,294 文件 manifest 逐项一致；host WT clean，guest Cosh scoped status clean。私有 Git 元数据快照只用于读取正确 HEAD/index，未改 WT 的真实 Git 元数据。guest 全 monorepo 额外 symlink 类型投影发生于 Cosh 之外，原始 status 已保留。

环境为独占 `cosh-7545-shell-host-20261015` 容器，ALinux4 / aarch64，ENV RUN_ID `20261014T201027Z-0e0298e5`，Rust `1.97.1 (8bab26f4f 2026-07-14)`。独占 cache/target `297f7061fc679d973bb7`；未使用或删除 Root cache/容器。profile 声明 2 CPU / 6G，guest 实际 nproc=3。宿主 doctor 的竞争记录保留；本次为隔离环境的功能与既有固定断言验证，运行时长不作为性能对比结论。

最终 S6 使用 cosh-issue-fix 自带 CLI、显式 base b75 的 `pr preflight --cargo-root src/cosh-ng --gate crates/cosh-shell/scripts/check-layout.sh --gate scripts/check-test-inventory.sh`，run `20261014T203632Z-341b4aef`。内层 `data.ok=true`：fmt、workspace/all-targets Clippy `-D warnings`、layout、inventory、drift 通过，commitlint findings=0，实际提交范围只有最终 commit。preflight 的 `tests` 明确为 not-run；下面的独立 tests 才构成测试证据。完整原生 Cargo argv/stdout/stderr 在 `evidence/cargo-native/`，成功日志也保留。 外层 envexec envelope 的 host cwd 为非 Git 工作区，因此 outer commit=null；准确来源由实际 guest private Git 的 HEAD/tree stamp、显式 GIT_DIR/GIT_WORK_TREE 和对应源码 manifest 绑定，不将该空字段说成 exactHEAD。最终四 exact/full 的标准 run 元数据均直接记载52745f8b、dirty=false。

最终原四个 exact 路径均实际 running 1 / 1 passed / 219 filtered，未零匹配：

| 路径 | 最终 run |
| --- | --- |
| `termios::parent_lifecycle::direct_children_scans_every_wrapper_thread` | `20261014T203903Z-d08176b2` |
| `termios::parent_lifecycle::raw_cli_restores_parent_termios_after_child_shell_signal` | `20261014T203934Z-a098a378` |
| `termios::parent_lifecycle::raw_cli_restores_parent_termios_after_foreground_group_signal` | `20261014T203934Z-6a14b053` |
| `termios::scripted_shell_exit_timeout_kills_foreground_group` | `20261014T203935Z-5c031d5f` |

原生命令形态为 `cargo test --locked --package cosh-shell --test shell_host <完整路径> -- --exact --test-threads=1`。timeout 原 8 秒断言保留，最终 exact 实际 5.38 秒通过。没有修改原 sleep/断言。

完整 target 最终 run `20261014T203942Z-88fa0b6a`，原生命令 `cargo test --locked --package cosh-shell --test shell_host -- --test-threads=4`：**running 220，219 passed / 0 failed / 1 ignored / 0 filtered，206.01 秒**。唯一 ignored 是原默认排除的 `heavy::raw_relay_host_runs_fullscreen_programs_and_keeps_shell_usable`，没有将 ignored 算为 passed。提交前另有独立 219/0/1 全 target GREEN，最终 HEAD 结果单独归档，没有用前序结果替代最终 run。

两个负控仅在 owned `/tmp/cosh-7545-mutant-source` 源副本编译，未写 bind `/work/repo`。所有 1,294 文件实际 manifest 与对应预期一致，编译成功后才运行原 case：

| 变体 | source SHA | 编译 test ELF SHA | 真实行为 |
| --- | --- | --- | --- |
| oldchildren + oldtimer | `d82aa6ebad29cb4f16d77d5fb5d3a425923bf1d5fa4f0d8cb7986f911c1b7abc` | `bb1dfe4467c5e5e97d1e2819fdc30c41f8d8bc0b8dcf0ca7ba9034af686f956f` | 原 2 case / 2线程，0 passed / 2 failed；child Bash 未发现及原 elapsed<8s 均触发 |
| oldchildren + newtimer | `afb8e8d6d24a914cf647cbebfc4f345ff642dd73035fd2bab9f156fee6a0855a` | `7ca46792acdc20b030910c19a11e7d7f4feaf585ec6bae366ad4d8e777a6607b` | 同原 pair 1 passed / 1 failed：timer PASS、child discovery FAIL；原 thread-child exact running1/FAIL |

负控 run `20261014T203142Z-32f75da7`。两个 pair 只有 timer 段差异，同原约10秒 held-lock driver，没有新增测试或 sleep。源码副本最后恢复固定 SHA8522。证据见 `compiled-controls-result.json` 与 `evidence/controls/`（全 stdout/stderr、argv、manifest、ELF SHA）。

恢复阶段第一次最终 exact **真实 FAIL**，run `20261014T203532Z-5f605715`，完整日志保留。实际 test ELF SHA 精确等于最后 mutant `7ca46792...`，Cargo 日志没有 Compiling，host/guest 固定源仍8522。这是共享本任务 target 的执行产物 cache mask，不是 flake，也没有作为产品源码失败。仅对 owned target 执行 `cargo clean --package cosh-shell`（Removed 1644 files / 3.2GiB），随后准确 HEAD 真实重新 Checking/Compiling、重跑完整 final preflight/4exact/full，全 GREEN。详见 `final-restoration-cache-mask.json` 与原 failed run；失败没有删除或改写。

最终 after readback run `20261014T204344Z-96117403`：HEAD/tree/source manifest 精确匹配，Cosh/cargo/rustc/test 进程为0。最终实际产品/测试 SHA：

- Shell：`466bcade8c0461096497eec9b7528f76907800e1d8675b3b69f3585c1b16d089`
- worker：`a54fe36068760758acbf9370461ea5276dce70feddf31c3add6f41a33787e046`
- shell_host test：`269ae37ba9ea05c4ccf07313412c444298930918728500c99ab0212ab8d88f3e`，区别于两个 mutant。

本 scope 未预建 normal `cosh-core` executable；preflight 已列出 Core lib/bin inventory，但它们不是 Core 行为验收。没有把不存在的 normal Core 填为通过。

标准 `env down` run `20261014T204412Z-e3e22b85` 返回 cleaned。独立 `env status` run `20261014T204434Z-05eec90e` 返回 completed/cleaned，实际 backend 已不存在（exit1/environment-unavailable）。另只读实际 `container list --format json` inventory 中 exact owned name **present=false**；这与 ledger 清理状态独立核对。`final-container-inventory.json`、`final-cleanup-readback.json` 保留事实。owned cache/evidence 保留，Root 容器未动。

未运行范围：被默认忽略 fullscreen TUI smoke、完整 crate tests、workspace tests、real-provider、canonical accept PNG/WebM、x86_64、release/RPM。没有截图索引，因为本次原 Rust shell_host scope 没有 canonical 录制合同；不把 scripted PTY tests 升级为 real-provider 或发布验收。

结构化汇总为 `final-acceptance.json`；最终原生测试完整结果为 `final-head-test-results.json`；完整可移交证据位于 `evidence/`、标准 CLI 结果/checksums 位于 `runs/`；关键文件完整性索引为 `final-evidence-sha256.txt`。初始化工具链/Git/tool setup 的失败 run 原样保留，分类为环境准备失败，与产品测试和恢复产物失败分别记录。
