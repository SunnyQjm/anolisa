# #7350 Readline recovery: independent review R2

结论：本轮限定源码审查未发现 actionable 阻断项。只读评审，不代表尚在进行中的真实 Core/PTY matrix、变异、preflight、CI 或 RPM 验收通过。

## Reviewed boundary

工作树 `/Users/quejianming/vscode/cosh-shell-dev/anolisa/.worktrees/cosh-7345-mode-routing-audit`，本轮基于已提交 `989dc4c6b7af5fe6a798bead09d0721e1f342138`。已审全部新增 diff：Bash marker guard、raw_cli mode 子模块注册、未跟踪 routing_recovery.rs 四个测试；读取 plan.md、既有 relay guard/ownership、marker commit/history、TerminalSession 等相邻实现。沿用首轮已读取的根/组件 AGENTS、review 与布局规则；未构建、未运行测试、未操作环境、未修改产品或其他 owner 树。

## Behavior and ownership

- 新 guard 的权威来源是 Bash `READLINE_LINE`，能看到历史召回及 Ctrl-A/Ctrl-E 编辑后的最终提交内容，不依赖 Rust 可能过期的输入镜像。未加入 eval 或 shell expansion 来识别控制命令。
- off 仍要求精确 first_word 命中现有 slash registry，且字符串必须以 `/mode`、至少一个 whitespace、`routing`、结尾或 whitespace 开始。`/mode routing-extra`、`/mode routing; true`、其他 `/mode` 子命令和 `/help` 不因此放行至本地 handler。leading space/tab 的既有归一化保持。query、invalid 参数和 assisted 都留给原有本地 handler 判断；非法参数没有新增隐式开启逻辑。
- 既有 Rust direct candidate 路径不受此变更影响；Readline 路径通过已有私有 guard 序列在主提示符 accept 边界注入，本次只改 widget 的 admission 条件，不扩大序列注入位置。read/PS2/foreground/pending/batch 的 ownership 决策保持在原 relay，未由本 guard 抢夺。
- enabled 状态下逻辑仍为 registry exact-first-word guard，新增 off 特例不改变其历史/editor 路径。命中后仍用原静态 no-op 避免执行原始 slash，再由 `_cosh_commit_pending_slash` 删除 guard history、按原敏感信息策略恢复历史并发出一次 marker。没有新增命令执行权限、provider 请求或审批操作。
- source 不修改 PS1，也不加 synthetic prompt。新测试直接要求终端当前 cursor 行等于原 prompt、列数正确且首字符保留绿色，并读回 PS1 精确原值；这比在 scrollback 中搜索 prompt 更能约束恢复位置。

## Tests and evidence readback

- 四个新增测试分别覆盖 off history、off editor、off 其他 slash/前后缀不接管，以及 enabled slash/普通 Bash history/editor。前两者同时覆盖经编辑的 query/invalid 和恰好一次 assisted notice；PS1 断言在发送新命令前由 command() 完成，另有文件值验证。
- TerminalSession 使用真实 PTY 与 vt100 screen；wait_screen 要求本次 send 后收到输出并 quiet，再检查当前 cursor 行。因此不是仅在旧输出中查到 prompt 就判断完成。通用 command 的 expected 文案允许留在旧屏幕中，个别无新唯一文本命令依赖当前 idle prompt 和后续行为；测试结论应与真实 Core driver 的逐阶段同步合看，不能把它当逐事件次数审计。
- TerminalSession 的 adapter 是 fake；上述四测属于 raw_cli 回归，不冒充真实 Core/provider 验收。raw 现有 RED 文件实际运行 2 tests 并 2 failed；对应 GREEN 实际 2 tests/2 passed，非零匹配误报。新增另两项及 matrix 完成状态由父任务继续核对。
- 保留有效真实 RED history `20261014T005649Z-bc61c88e`、Ctrl-A/Ctrl-E edit `20261014T005919Z-75987605`；旧 CSI 编辑尝试 `250615fd` 不用作最终有效编辑证据。只读回读 history dirty GREEN `20261014T010055Z-0acd7362` 为 ok=true，不据此宣布全部 fresh GREEN 或有效变异完成。
- 本轮没有独立看完最终 cast/fullsize PNG；driver 当前通过 notice 后等待原 prompt、无新输入记录 idle phase，再请求第二次模型响应。最终颜色、currentcursorline 和整屏证据必须由父任务按最终源码/ELF绑定核验，不能仅靠 driver 去 ANSI 后的 tail 字符串宣称视觉验收通过。
- 原 R9 isolated CI 归因仍不在本修复已证实范围内；没有扩大为 flaky、平台级 slash 修复或生产 Go。

## Snapshot SHA256

| File | SHA256 |
| --- | --- |
| shell_host/marker/bash.sh | f3fa6ca1221bacb901790fbaf3b44b32c3d7d5f73652649786b9c44361b270da |
| tests/raw_cli/mode.rs | b2dd7b7befa7be264810d4feaf14265261b4b9955afb7c0def4140203788de51 |
| tests/raw_cli/mode/routing_recovery.rs | 7f9330b9562847c8fa295cc3f47ac9ff5efdf810f49124cab66379658923413a |

此次无产品编辑、无构建或环境操作。后续最终 SHA 若变化，应限定增量复核；本报告不替代 kongche 正式审批或 root RPM 验收。

## Final local delta and mutation readback

再次只读回读三文件 SHA256，均与上表完全一致：guard `f3fa6ca1…`、注册 `b2dd7b7b…`、测试 `7f9330b9…`。cargo fmt 后测试逻辑仍为上述四测，没有断言削弱、门限抬高、额外 product diff。guard 已从 mutant 精确恢复；`mutation-restored.json` 的完整 source_sha256 与当前实际 hash 相符，exact_hunk_restore=true。

已实际读取有效变异记录：`mutant-build.json` 的命令先运行四项 raw_cli 回归，要求真实测试退出 101，再编译 Shell ELF 并输出其 hash；因此外层 ok=true 表示变异脚本完成，不表示 mutant 测试通过。stdout 明确为 **3 failed / 1 passed**：off 的三项失败，enabled history/editor 正向控制通过，随后 locked Shell build 成功。与源码 guard 相比，该变异能够针对新增 off admission 的可观测行为产生有效区分。

真实 Core/PTY 两条 mutant 记录 `mutant-history.json`（`d9a761d8`）及 `mutant-edit.json`（`8e3df3e5`）均 ok=false；其实际失败断言同时包含缺失 restored=1/requests=2 完成标记，以及 `/mode: No such file or directory` 意外输出。未把它们改记为 Go，也未将外层成功的 build 脚本误称产品通过。四项原行为 GREEN 的最终汇总由父任务维护；本轮没有运行它们。

本次限定增量结论仍无阻断项。最终 amend commit 的确切 HEAD、fresh ELF/cast/fullsize 原色 PS1 currentcursorline 截图与正在运行的 workspace Clippy/layout/inventory/focused 尚不由本轮只读核查认证；需按实际结果分别收口。未改源码、未执行 cargo 或环境命令。

## Final rebase review: 0f8a763d

已只读核对最终 HEAD `0f8a763dd9db8916c2780b6eb45d340579d93e9f`，tree `dc6e3a0c61b5481c8a3315da7af63bb9809ec479`。`HEAD:src/cosh-ng` 和先前 `f8a0a231:src/cosh-ng` 均为 `3378673de0968440002ed67a0601f3faf795a658`，整个 Cosh 子树相同。

662c5c45→8cabc9eca 的上游增量实际仅 `src/aw/crates/aw-service/src/audit.rs` 与 `src/aw/crates/aw-service/tests/service.rs`；f8a0a231→最终 HEAD 的变化同样只有这两文件。它们在独立 AW 组件，不触及本次已审 routing 邻接或 Shell/Core 所有权协议；本轮不评审 AW 实现本身。

最终 HEAD 相对基线 8cabc9eca 的提交 diff 仍恰为七个已审文件（252 insertions / 1 deletion）。实际 SHA256 再次核对：candidate `48219035…`、relay_tests 注册 `3a197375…`、relay recovery `19f67179…`、mode_tests `cabddee8…` 与首轮表一致；Bash marker `f3fa6ca1…`、raw_cli mode 注册 `b2dd7b7b…`、raw_cli recovery `7f9330b9…` 与 R2 表一致。无额外 product 修改，未跟踪的 .cosh-lab 和两项诊断 YAML 仍未进入提交。

本轮增量无阻断项，无额外 scope 变化。没有运行 cargo、环境操作或改产品。父任务已查看的 f8a0a231 图像不在本轮独立视觉验证范围内；最终 0f8a763d 正在重跑的门禁与三例捕获仍须用其自身确切 HEAD/ELF/截图记录确认，不借用旧 HEAD 结果代替。
