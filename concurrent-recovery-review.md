# Concurrent prompt/readiness recovery review

静态结论：本次必要追加修正的两个机制未发现 actionable 源码阻断项。运行验收尚未完成；现有 recovery-green.json 实际包含失败，不能称整体 GREEN。

## Scope

UI 独占工作树 e315fef6 基线上，审查 dirty runtime/controller.rs、runtime/controller/tests.rs、tests/support/raw_cli.rs 三文件，94 additions/20 deletions。只读检查必要 observer/action、prompt replay 与 readiness 生命周期及已有故障断言；没有改 code/index/环境，未执行测试，未访问 Root 或其他 owner tree。没有扩展 CPR/shared slot、审批/capture 或依赖架构。

## Prompt fix

- 新动作只发生于既有 deferred timeout notice 存在、foreground 不 busy、handoff queue 无 pending 的分支，且 notice writer 成功返回后才返回原有 RestorePrompt（无 ghost）。不改变 interrupt deadline、批准结算、HostResult、Shell ownership 或下一命令。
- 现有 controller 流程在此之前处理 pending capture 和已有 trigger_pty_prompt；物理 display failed 路径仍先 Hold，不借新增动作在持续 EIO 下擅自恢复或解除输入冻结。
- RestorePrompt 由原有 observer/PTY display 路径消费：flush notice，获取 parser 保存的 raw native prompt，使用原 prompt_replay/presentation 输出并 flush；raw prompt 未知时保留待恢复动作。没有合成默认 PS1，也不请求新的用户输入来触发重画。
- 因而修正针对“原 prompt 已出现，后续 deferred timeout notice 使 cursor 空行”的具体顺序，动作在本次 render call 中发出，真正 before-new-input 可见恢复仍必须由原三项真实 Core/PTY currentcursorline oracle 验证，不能仅凭 action unit 代替。
- 原 timeout-notice unit 的 None 改为 RestorePrompt 是新的正确契约；新增单元要求一次 notice/action、pending 清空，再次调用不重复画或恢复。原故障 fixture 的 row/col/green 强断言未改。

## Readiness isolation fix

- 旧 timestamp+pid/create_dir_all 只保证目录存在，不保证同 test process 多 writer 独占；固定 realtime 对照能令它们别名，共享 request/token 即可解释等待2却观察到3/4/5。不能从单 writer 逻辑推导原 full failure 无风险。
- 新实现用已有 tempfile 原子独占 TempDir，持有在 RawCliInputReadiness 内直到 driver 生命周期结束。token 包含该目录唯一 basename，request_path 与 token 一起隔离；不依赖 wallclock，也不改计数递增、request ack 匹配、超时或 token strip。
- 两个 helper 均在 spawn 前创建并持有该对象，正常流程等 child/output 收口后才离开作用域；TempDir 替代原手动 remove_dir_all，删除只限自己的路径。不会因其他 driver drop 删除 survivor。没有新生产 API/.env/lock/依赖。
- 新 regression 并发四对象，断言四路径、各自请求写入并在其他对象销毁后读 survivor=4；它检查 identity/lifetime，不是只检查随机名字符串格式。固定 CLOCK_REALTIME 时有效 RED（1路径 vs4），正向通过必须保留真实编译输出。该 unit 不证明所有 auth 状态流已关闭。

## Actual evidence and limitations

已读 timeout-red.json：实际1 FAIL，None vs expected RestorePrompt；readiness-red-equal-clock.json：实际1 FAIL，paths1 vs4；auth-equal-clock-negative.json：三并发auth **1 PASS/2 FAIL**，与原 request collision 同类失败。CLOCK_REALTIME interposer 位于测试过程，真实 monotonic deadline 不变；不冒充生产部署。

已读 recovery-green.json：总 exit101，controller11 PASS、独占路径unit1 PASS，但并发auth **2 PASS/1 FAIL**。故该 artifact 尚不能作为最终修复 GREEN；失败 transcript 有独占 token 的 request2/3，说明必须分析剩余失败，不能只以“已独占目录”删除原失败或判 flaky。此处不预先判断其为目录修复无效或 unrelated。正常clock和fixedclock的新正控、PS1实际并发正控正在主任务完成，不能由本报告提前认证。

新增修正最小且 oracle 未减弱；尚需实际最新候选并发/fullraw 将 auth 与原生 PS1 全部收口。原 recommendation request4 历史归因保持未证实，不以本独占路径对照自动宣布同因。审批、capture、输入冻结和 prompt 强断言不能为求 GREEN 放宽。

## Reviewed SHA256

| File | SHA256 |
| --- | --- |
| runtime/controller.rs | 115badec302c85ccdaf357b308d5708f6c315d10b980a996827a503c7f28a1b2 |
| runtime/controller/tests.rs | 46c66780981ec0ca5621138e64676d1ce9275f402f4b5cc506191ea208715159 |
| tests/support/raw_cli.rs | 27c40c04fd17df7895805384a8d4e299796da64175d447c0728dd885c839283c |

本次无静态阻断项不是 acceptance；直到真实并发 PS1/auth full failures 解决仍 No-Go，没有 merge/发布结论。

主任务已确认早期 recovery-green 的固定 clock interposer 作用到全部 cosh-shell children，edit API Key 剩余失败中 request2/3 已正确 ack、没有 future request 编号，因此该组正控存在外部时钟干扰，不能混成有效完整 GREEN 或擅自称与原 readiness 同因。原 auth preserves case 在此组实际 PASS。保留原 exit101/日志；主任务将仅限制 raw_cli-* 测试驱动的 CLOCK_REALTIME、使 Shell/Core wallclock 正常后重做三 auth、path unit 与真实 fault 并发正控。新的限制与正控结果尚未由本报告认证。

## Restored final source and layout

最终实际 HEAD `12eeef0173c85f11a835a83b540c55ac0fbed9c5`，tree `f2af294c497f3b2a0a33b9b519878495cbc04930`，base `b75eff716d8c42ba17b8355b47373430d25d2505`，Cosh subtree `36ac66f144896958bff3d536e9636f73412d4524`。tracked clean，仅 .cosh-lab 未跟踪。整体相对 base 为七文件149+/29-，前述三项原补丁和本次四路径必要追加，没有夹带诊断源码。

最终 layout 修正已实际检查：support 不再注册 #[test]，只提供 pub(crate) assertion helper；五行 #[test] wrapper 注册在现有 tests/raw_cli/auth.rs，按既有 integration test 入口被发现。没有 public production API、原断言移除或 inventory 门限改动。controller 新 unit 的 initializer 调整符合 Clippy，仍保留一次 RestorePrompt、pending 清空与第二次 None/无输出检查。

最后两个 commit 的英文 scope/[shell]、长度和 Assisted-by/Signed-off-by 顺序合规。已实际读取 0000cabe8c 新增 deferred notice 分支，ee9c56278e 新增 timestamp readiness fixture，支持对应 Fixes attribution。controller 只恢复原 action，TempDir 只更改 test-driver ownership；没有扩大执行/审批/capture 权限或抢占 foreground 输入。

| Final additional file | SHA256 |
| --- | --- |
| runtime/controller.rs | 115badec302c85ccdaf357b308d5708f6c315d10b980a996827a503c7f28a1b2 |
| runtime/controller/tests.rs | 3568eca1953bcfcf6b4c9b1e1003ddfc33d38842356bd7db71b7a03a6dfe5776 |
| tests/support/raw_cli.rs | c0a9f027f22d19a752c41544b277fc68f43b405c24e17c3bb2b85687f05c03d5 |
| tests/raw_cli/auth.rs | 873bfc5df120da90c59d83eecda0cfcee3dde8f80df9b0015e3aab4cd3de3caa |

## Observed scoped controls and effective mutation

实际读取 scoped-clock-and-fault-green.json，总 exit0：独占 path1 PASS，driver-only fixed realtime 下 auth三项3 PASS，实际 Core/PTY fault三项同时运行四轮共12 PASS。十二次均输出 row31/col14 原 native prompt，现有绿色强断言通过，检查在任何新输入前；未删原 HostResult/同 Bash/timeout settlement oracle。它支持两个具体机制修复的并发 focused 正控，不替换旧 full-run 空行失败证据。

实际读取 compiled-mutation-results.json：外层exit0表示验证预期失败成功；移除 idle RestorePrompt 的可编译变异使 unit exit101（None vs expected action），恢复旧 timestamp 名的变异使 identity unit exit101（1路径 vs4），并在仅 driver 固定时钟下原 auth并发1 PASS/2 FAIL、原 preserves-picker case 再次出现 request2/future4。没有用新的 edit API Key 失败或全 child 固定时钟混杂当同因证明。两个 unit 及真实 auth 路径构成有效区分；恢复源码后 SHA 如上。

实际读取 restored-layout-validation.json，总exit0：controller11 PASS、identity正常clock1 PASS、driver-only fixedclock1 PASS，以及 layout/Clippy/inventory通过。早期 recovery-green exit101继续保留，不改标签。该组 evidence 的 raw总量显示622，不能再借旧621/631作最终候选数量。

最终增量静态无阻断项，具体 focused/mutation 已有实际支持；最终冻结 HEAD 的完整 fullraw仍待主任务完成，不宣称完整验收或 merge/release Go。recommendation历史 request4 timeout仍未归因，不能因为 fixture独占修复有对照就自动给它同因结论。未运行测试、修改 code/index或操作环境。

## New caret contract gap: narrow cause and planned recovery review

主任务报告12ee fullraw 621 PASS/0 FAIL/1 ignored；这个既有测试 GREEN 不能覆盖随后原始 PTY 发现的真实 caret 隐藏缺口。实际读取 original-cursor-visibility-proof.json，确切12ee gate-withdraw failure 在 native-prompt-recovered row31/col14 处 cursor_visible=false；receipt 与 timeout 两例 true。原 prompt 文字、位置、绿色不等于可编辑 caret 可见。

实际读取 caret-pty-red.json：3项真实输出故障测试 **2 PASS/1 FAIL**，exit101，failed gate-withdraw case 明确为 `native editable cursor must be visible before input`。新增 VT100 `!screen.hide_cursor()` 断言位于原 row/col/green 强断言旁、任何新输入之前，不靠之后 Bash Readline输入修复隐藏状态，oracle有效且没有放宽任何现有断言。

源码机制支持该根因：relinquish_untrusted 将 gate rectangle 清空以免 stale erase，随后关闭 worker；Drop 的现有 ShowCursor cleanup 仅在 rect Some 时发送，所以 untrusted withdraw 路径合法失去该 cleanup。degraded::recover 当前重置 SGR/wrap/scroll并flush，却没有恢复 DECSET25。恢复光标不应通过重新授权不可信旧 rectangle 的 Drop 绘制来实现。

计划在现有 physical healthy recover 字节串增加 `ESC[?25h` 符合最小修正方向：仅正常物理 write/flush后解除 display_failed；若EIO仍存在，原 defer/Hold继续保留。既有 component fixture明言 recovery alone never grants input，新增 ShowCursor 字节不会改变它，审批、capture、worker销毁和bounded handoff不变。无需CPR或sharedslot，新product职责留在已有终端状态恢复路径。

新增 component assertion要求实际 healthy bytes包含六字节ShowCursor，保留 failed-writer/无token严格传播、newline数量及Hold断言；可编译移除此新增序列应导致新component和gate-withdraw原始PTY强断言FAIL，不能只测字符串生成或下一输入后的屏幕。review当时 product degraded.rs 尚未改，所以这是方案路径审查，当前候选仍有已证实caret缺陷；后续最终字节/SHA、真实GREEN/mutation需再绑定，不能提前认证。

主任务同时报告CI fast在未改checkpoint.rs发生ETXTBSY，source blob与base一致；该日志仍是阻断项，未审或修改Platform，不判flaky、不以Shell修正覆盖它。即便原fullraw全部通过，也不能宣布可编辑原prompt硬合同满足或生产Go，直到caret和CI各自收口。未code/index/环境编辑或运行测试。

## Exact caret commit review

实际核查 HEAD `60b68369eb0d573b0c9ba61106e04cab7ba56f0f`，tree `0f29bc0fbe6d068dc99d53bb955b788bdbb05277`，base仍 b75eff716d8c42ba17b8355b47373430d25d2505，Cosh subtree `6a25f82f406beb0ce72af9c6f38a63dc44a43e97`；tracked clean。最终 caret commit 相对前一commit仅三个指定路径：一处恢复字节literal增加六字节 `ESC[?25h`，component assertion和before-input VT100 caret断言。不是新状态机/API/CPR/sharedslot，不松Hold、审批或worker边界；既有SGR/wrap/newline/flush/failed-write逻辑保持。

| Final caret path | SHA256 |
| --- | --- |
| shell_host/raw_relay/degraded.rs | 1c7d5616d4b0ba96af5c731defa7dbaaac770ce88e8aa78054c8da9ee011fc51 |
| shell_host/raw_relay/degraded_tests.rs | 4a45a4740dcb5b32312668b1e1fd73cec07c10469da667eb4b3de96ef155771e |
| tests/support/ui_approval_slice.rs | 7bc2bc494ab6b4b3445973fb5aaa24aafe756c9ea3fb9512d899215b585d4375 |

实际读取 caret-green-and-audit.json：总exit0，controller11 PASS、实际Core故障3 PASS，三例在任何新输入前原row31/col14/green/caret-visible断言均保留并通过；Clippy/layout/inventory通过。caret-compiled-mutation.json 外层exit0是成功捕获预期失败：移除25h重新编译后实际component1 FAIL/exit101，断言为“physical recovery must restore the caret hidden by the worker”，提供有效区分；最终源码当前实际字节和SHA如上。此次读取没有自行跑测试或改源码。

最终产品范围为原hook predicate/idle notice恢复/独占测试probe及caretrecovery，不增加平台修复。十路径的必要scope有具体根因/控制来源，caret增量静态无阻断项。12ee前驱621/0/1的旧full结果继续保留，但不能当60b的新caret验收；新的exact preflight/原始PTY证据/fullraw仍待完成。既有Platform checkpoint ETXTBSY CI失败继续记录阻断，原recommendation request4归因不升级。未宣布最终整体Go或正式合并批准。

## Final 60b execution readback

实际读取 final-visible-caret-four-thread-raw-cli.json：exact60b候选四线程 fullraw完成，**621 PASS / 0 FAIL / 1 ignored，622 total，709.66秒，exit0**。这次包含强化caret oracle，不是12ee旧full的复用。post-full-source-readback.json实读HEAD60b/tree0f29、1188源文件、mismatches为空、tracked clean，仅.cosh-lab未跟踪。

实际读取 caret-final-head-preflight-and-pty-evidence.json：outerexit0，inner formalpreflight ok=true；controller11和实际Core/PTY故障3（14项focused）PASS，原色PS1/currentrow31/currentcol14和visiblecaret强断言在新输入前通过。此次exact记录不借用更早四轮dirty source结果。

native-prompt-replay-summary.json的原始字节点/确切HEAD绑定为60b/tree0f29，三个补充tmux回放均记录visiblecursor=true、row31/col14。该回放明确为synthetic timing、保留原始字节顺序/geometry；视觉PNG由主任务view，我只读metadata，没有冒充自己看图或原native runtime录制。原始PTY包含实际before-input字节点，补充回放与原始证据应分开标识。

历史证据全部保留：e315 full618/2/1的auth/PS1失败，12ee full621/0/1但caret仍隐藏的限制，以及强化oracle有效RED/compiled mutation；不能把历史失败改写成未发生或凭targeted PASS称无害flaky。当前60b的完整raw结果支持该十路径修正的raw验收，不自动解释旧recommendation request4。

最终实际读取 pr-final-readback.json：PR #7489 HEAD60b、draft=true、REVIEW_REQUIRED，请求zkl123；25项check均COMPLETED且SUCCESS/SKIPPED，无pending/failure（含主任务所述Cosh aggregate）。CI终态已收口，formal human review尚未批准。原12ee未改Platform ETXTBSY日志保留且未知原因，不涉及Platform修复、不判flaky；当前CI成功不赋予该旧故障归因。

最终实际读取 final-cleanup.json：ok=true、status=cleaned、already_absent=false；独立 final-cleanup-container-readback.json 确认 owned codex-raw-cli-main-20261015 present=false。属于实际清理且有独立回读，不是仅列表缺名推断。此清理终态已收口，immutable artifact发布由主任务另行完成。

终态审查结论：静态无阻断，exact60b focused/preflight/fullraw与CI已有实际GREEN，owned环境实际清理并独立回读；正式human review pending、历史request4未归因，保持draft No-Go，不声明生产/RPM/release Go。本轮未运行测试、操作环境或改code/index，只更新自身review报告。
