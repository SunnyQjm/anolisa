# #7891 U02 persistent TTY: approved-scope source audit

结论：当前树已继承批准方案的大部分局部保活/结算能力，不能重复报告为全未实现；但恢复prompt分支仍有未纳入物理错误隔离的实际出口。U02完整验收未关闭，kill/hang不替代持续TTY故障。无需再请求相同G1。

## Inputs and identity

只读新7891树，HEAD/base `a37dd32ae9f3d80b2a2388d38ca84ddb2d2d377e` 加production未提交补丁。读取已批准 `outputs/codex-takeover-20261013/ui/persistent-tty-recovery-proposal.md`。指定HANDOFF-NEEDS文件不在ui子目录，实际已定位并读取 `outputs/codex-takeover-20261013/production-worker-20261016/acceptance/tool-source/HANDOFF-NEEDS.json`，没有把路径缺失当内容已给出。

本次只做实施准备，未改源码/index/环境、未运行测试、未写其他owner或Root冻结树。旧候选或本轮worker kill/hang日志均不作为U02的实际GREEN。

## Approved mechanism: actual support

| Approved requirement | Actual function/path | Assessment |
| --- | --- | --- |
| Actual PTY write后绑定token | shell_host/raw_relay/pty_emit.rs `emit_to_pty`：先校验/stage/register origin/write_all_pty，成功后reset.bind_display_handoff(request.token) | 已实现。文件、parser origin和PTY写失败仍返回真实Err，不能被display恢复吞掉。 |
| 精确物理write/flush错误局部化 | shell_host/raw_relay/degraded.rs `PhysicalDisplayWriter/tag_physical_error/defer_physical_error/display` | 已实现。要求真实PhysicalDisplayError且已有token；否则严格Err。首次失败signal并置display_failed，retire capture并Hold。不是返回假成功的通用writer。 |
| 持续读OSC、UI之前结算 | runtime/controller.rs `render_raw_inline_event_view:65-108` | 已实现。token匹配pending handoff时，先observe_shell_command_activity/build_command_blocks/record_approved_shell_handoff_blocks/close_untracked_shell_handoffs，再处理failed display/worker teardown/Hold。 |
| 一次HostExecutedResult | activity/shell_handoff.rs `record_approved_shell_handoff_blocks` → runtime/evidence_delivery.rs `record_shell_handoff_completion:18` | 使用已有完成证据与provider delivery claim。该函数在构建UI activity之前调用deliver_host_executed_shell_result_if_supported，后者向既有response_sender交付并记录ledger；不是在屏幕打印成功才结算。 |
| 已损display仍保同Bash/新输入Hold | shell_host/raw_relay.rs `read_raw_until_exit` + raw_relay/observer.rs `observe_with_input_mode_lock` | 主循环每次尝试recover，失败仍Ok(false)继续；原输入/OSC照读，非授权emit强制Hold。批准的commit emit是一次受控例外，不自动重发。 |
| 原bounded timeout | runtime/controller.rs `shell_handoff_timeout_recovery_action_with_timeout:262`，raw_relay/pty_emit.rs InterruptForeground | 现有时限触发一次foreground interrupt，再等待真实boundary；无marker时不假造成功、不自动retry。恢复后延迟notice成功会返回RestorePrompt。 |
| 物理恢复/fresh region/caret | degraded.rs `recover:108` | 先取消可能半截控制序列、重置SGR/wrap、ShowCursor、滚出fresh region并flush，成功才清failed/signal/notify_resize，Hold不会仅因写一次字节提前授权。 |
| 原生PS1且before-input | raw_relay/pty_emit.rs RestorePrompt；tests/support/ui_approval_slice.rs `persistent_output_fault_and_recovery` | 既有parser.last_prompt_display→prompt_replay/native presentation，保原内容/颜色/cwd展开，不替换固定Cosh prompt。测试在下一条printf/Enter前检查原cursor行、col、绿色与!hide_cursor。静态支持存在，不等于本轮实际release故障验收已跑。 |

原proposal的“后续display cut/write先于observer返回”在当前主display-cut路径已由 degraded::display 包裹，不能照抄成该路径仍全缺。controller还在每pass前做结算，真实完成marker不依赖UI先成功。这些均需新release候选/ELF证据重新验证，不能借旧debug源码结论。

## Concrete remaining error exit: prompt recovery can fail again

`shell_host/raw_relay/pty_emit.rs:220-260` 的 RestorePrompt 分支仍直接使用raw output：初始flush(:224)、write_pending_display(:234)、write_restored_prompt(:242)、ghost(:257)和末尾flush(:259)，都没有以PhysicalDisplayWriter标记实际物理错误并调用defer。

触发：已批准token的持续TTY故障先经历一次成功fresh-region recover，随后writer在原PS1重画的write/flush上再次EIO/WriteZero（也包含间歇恢复后立即再次故障）。错误经raw_relay.rs:177-194的resolve_pty_emit `?` 直接离开循环；remember_pending_prompt_restore在:195尚未执行，恢复动作也未保留。因而前半程保活并不能保证这一恢复阶段仍保活。

`raw_runner.rs:460-495` 将read_raw_until_exit错误继续`?`向上返回，后续正常wait_child/observe结束不运行。代码里**没有该Err分支显式child.kill()**，不能说已静态证明“raw_runner调用kill杀Bash”；但返回会释放PTY/session资源，Shell主流程退出后剩余fd关闭可能引发hangup，无法由源码保证原Bash继续存活。必须用实际PID/fd/效果证据证明，不能把“没有显式kill”当保活通过。

最小接线建议：仅在RestorePrompt的物理呈现边界使用已有PhysicalDisplayWriter，保存该restore动作；若实际tagged物理错误且token有效，走现有defer/Hold并保留pending_restore，下一次fresh recover后重新绘制原prompt。parser/storage/PTY/staging错误仍严格传播。不能在整个resolve_pty_emit或raw_runner外泛catch io::Error，也不能重发approved命令/HostResult。沿现有pending_prompt_restore和input-generation retire/reset，不新增CPR/sharedslot或通用恢复平台。

### Token retirement is part of that same narrow fix

进一步实读发现：degraded::recover成功只清display_failed、signal和notify_resize，本身不清display_handoff_token；但controller.rs约172-181在handoff pending队列已空时调用reset.end_display_handoff()，该行在trigger_pty_prompt→RestorePrompt返回之前。已完成marker/HostResult后，writer恢复进入该pass，就可能在实际原PS1恢复前先清token。此时即便RestorePrompt加了PhysicalDisplayWriter，后续defer_physical_error仍因无token严格Err。**只包writer、不调整此退休时点是不完整修复。**

最小接线应把这个“只用于显示恢复”的token lease保留到该次native prompt restore的真实write/flush成功边界：结算/执行身份仍按原逻辑完成，不再批准、排队或交付一次HostResult。若prompt write/flush再次失败，token仍bound，可用原defer标记display_failed，保pending_restore和Hold；若native prompt全量成功且无需待呈现，则及时end_display_handoff，不能把旧token长期挂住以catch后续无关故障。避免新request或新token复用时错误释放他人的lease，按现有token身份核对结束即可；不需要新共享slot。

自动恢复链应为：每次无输入maintenance loop→原recover输出fresh region/ShowCursor并flush成功→observer持该显示lease取得/重试原RestorePrompt→使用parser.last_prompt_display保存的原始ANSI/目录展开字节、prompt_replay_bytes与write_restored_prompt（或既有pending display replay）自动重绘→最后真实flush成功→清该恢复动作和显示lease、再允许既有输入模式。整个链不等待Enter/printf；失败则回到display_failed/Hold，下次仍从同一原生prompt owner恢复，不能替换固定Cosh prompt。未知raw prompt时保pending action，不捏造提示符。新RED必须同时证明token未提前退休与PS1 write/flush再失败保活，不只检查某次writer返回值。

### Narrow design review: explicit pending display restore

仅以controller当轮trigger_pty_prompt决定token保留不够：该trigger在第一次返回RestorePrompt时被清，下轮controller不知道raw loop里的pending action，仍会提前退休token。建议采纳主任务提出的一个局部 `display_prompt_restore_pending` AtomicBool，放在现有CaptureRepresentationReset共享句柄，只表达显示恢复未完成，不是执行/批准权限。

最小正确顺序与边界：

1. controller对已bound display token决定返回RestorePrompt时，**返回前**mark_pending；trigger清后下一pass仍以pending阻止end_display_handoff。pending优先于新pending_card_capture；亦须在emit_next_approved之前阻止新的handoff抢占旧lease，已有批准可按原queue等待，不重发旧命令、不撤销已结算事实。不能靠最终raw-mode Hold替代阻止Emit action，因为PTY发送发生在mode更新之前。
2. observe_with_input_mode_lock在锁内最终mode更新后，对 `display_failed || restore_pending` 强制Hold；degraded::update_input_mode_after_display也同样检查。否则observer会先把无ghost的RestorePrompt按现有映射置Passthrough，解锁后到实际write/flush之间存在输入线程窗口。raw prompt为空是“尚无可画证据”，应保持pending/token/Hold和原Restore action，不伪造physical failure，也不交还Passthrough。
3. 原merge_pending_prompt_restore对任何非Continue/Restore action都会pending.take，Hold/Delay可把重试丢掉。只在这项受损恢复lease作用域保留原pending Restore：坏TTY pass返回Hold不覆盖它，恢复后Continue再消费；合法timeout Interrupt或暂时更高优先级observer动作不能顺带删除它。优先复用raw loop的原Restore payload/ghost；若改成controller每轮重新发Restore，必须保留原payload而非第一次take之后重造空ghost，并避免重复成功重画。无需每次正常handoff都强行restore。
4. RestorePrompt内部以PhysicalDisplayWriter标记真实物理write/flush；失败defer必须有当前boundtoken，保pending并交给原display_failed/Hold，不放过parser/storage/PTY错误。成功的末flush后才完成该显示lease/clear_pending，后续update才允许正常输入。当前ghost分支在末flush前直接设置PromptGhost也会开放编辑窗口，需同样延后到真实成功flush后；不要只修无ghost形态。
5. end_display_handoff应明确结束对应token的显示lease（确认仍为本次token），清pending；新bind不要继承前一token的pending。以上退休只能在原PS1实际完成且无需重试时发生，非“已生成字符串”“freshregion刚成功”或“HostResult已交付”。无token的普通Restore保持原严格/独立语义，避免吞掉无关终端错误。

应补相邻component controls：trigger已清后的第二pass仍token+Hold；rawprompt空多pass仍Hold且旧输入无效；Hold/Delay期间原Restore payload不丢；ghost写成功但末flush失败仍不能获得PromptGhost权限；新capture/queuedhandoff不能先于恢复抢占；最终成功只结束一次lease、后续pass不重复restore。真实refault测试保留无新输入原PS1内容/颜色/cwd/caret oracle。真实RED正在主任务执行；本节是只读设计审核，不是已实现或已验证结论，不要求再次G1。

### Final narrow retirement recommendation

主任务指出仅等trigger仍可能在provider response前清token，这一问题成立。最简单的**限定受损恢复**方案是让同一个pending位表示“本token发生过物理显示失败，欠一次原生prompt恢复”，不额外引入was_failed/执行状态：在实际tagged失败/committed display失败时置位，commit前已知失败则由绑定token继承；recover只清physical-failed，不清这项恢复债务。

- token仍在真实handoff队列时：先OSC/既有结算与bounded interrupt，不因恢复债务提前绘制可编辑prompt，也不借标志生成执行权限。
- 本token真实settled且pending=true：在new Emit/Capture之前直接要求无ghost原生RestorePrompt，不再等provider最后response决定的trigger。raw prompt未知则仍pending/Hold；成功实际flush后结束这个显示lease/clear pending。仅恢复显示，不重开已结算handoff。
- 没发生物理损坏的token、pending=false：保原退休/response布局流程，不对每次正常handoff新增一次强制Restore。这样不为解决受损case默默重排所有正常provider输出。
- 该lease-only恢复成功后，不应直接用Continue→Passthrough开放输入：provider下一response或更高优先级card可能仍活动。可返回一次现有Hold，下一observer按真实run/capture重新决定mode；无需新post-owner状态或执行权限。恢复前两处pending/failed强制Hold仍必要。
- 原`trigger_pty_prompt`如在provider后续响应终态再次要求正常prompt恢复，可沿原流程；不能为了“避免重复”删掉它而导致后续response输出后再次丢prompt。受损fresh prompt与之后新输出后的prompt是两个边界，不得预宣称布局完全不变，应对照无损路径做实际输出/ghost正控。

受损恢复的关键承诺是原生PS1，而非旧输入ghost。对已经失效代际的ghost应沿既有reset/retire丢弃，不能为了原payload保留而重新授予旧PromptGhost输入权限；非受损的正常ghost流程保持。若主任务选择对所有settled token直接Restore，必须额外证明不会提前放开active-run输入或改变正常布局；上述仅pending受损债务方案避免该扩张，仍只一个局部布尔位。

无token、单纯启动TTY失败、实际PTY断开/文件失败仍应严格失败，本批准范围不保证任意Shell启动/退出错误的无限保活。

## HANDOFF-NEEDS interfaces and remaining U02 gaps

- U02a：真实旧generation/descendant IPC witness需要从旧worker进程/旧socket到实际Host consumer的拒绝证据。当前kill/hang/重建和malformed帧测试不等于旧代后代仍持IPC的有效反例；不宣布该项闭合。
- U02b：当前有实际token/marker/interrupt及HostResult证据接口。可信命令完成走实际状态；可信prompt但无tracked outcome走existing untracked completion（exit=-1/uncertain），不应凭墙钟超时伪造成功。Bash忽略interrupt且没有可信boundary时仍可能Running/Hold，HANDOFF所需Running/Unknown具体witness尚须绑定tool observer；不能默认已有一个公开Running/Unknown查询接口，更不能重复执行求结果。
- U02c：未在当前slash/runtime/raw_input中找到明确的公共terminal takeback入口；恢复writer或既有timeout interrupt不是用户显式takeback。原批准首版只保证既有bounded语义，不授权凭空建立新协议；该更广接口需求保持单列No-Go/由Root作范围处理，本audit不要求重走已批准G1。
- HANDOFF指定newcandidate/commit/tree、release RPM归档SHA/NEVRA/六payload、contract/identity/fixture/observer hash与real-provider HOME预检仍需Root冻结；old v7明确不可用于新验收，旧资源/kill/hang/假adapter不可替代。

## Required next evidence (not executed here)

在actual release Shell/Core/Bash/PTY中按真实commit后回执、Gate撤回、display cut、持续flush和恢复prompt各位置注入；保持故障期间完成一次延迟效果，验证effect=1/HostResult=1、相同BashPID、旧输入无效、新审批无capture权限。新恢复分支补“fresh-region成功后prompt write/flush再次失败”的RED/GREEN；无token/非物理/实际PTY失败作严格负控。

故障解除后在任何新输入前核原PS1文本/颜色/cwd/caret currentcursorline，另测原bounded timeout effect0、失去marker的Running/uncertain、不自动retry；保original cast、fullsizePNG、termios/进程清理及精确source/ELF身份。当前结论是已批准实施准备与具体接线缺口，**U02未关闭，不宣称production UI Go**。


## R4 actual implementation read-only review — 2026-10-16

结论：本轮五个产品文件及其调用链静态审查 `findings_count=0`，未发现可验证的新增 P0–P2 阻断。此结论不把尚在执行的真实 RED/GREEN、编译变异或 release 验收判为通过。读取时 WT HEAD 为 `fd31f09b29e3a9a9fb617c9e404a7fa81c2e39bb`，五文件为未提交工作内容，不能用该 HEAD 单独代表补丁。

| 产品文件（相对 src/cosh-ng/crates/cosh-shell/src） | SHA-256 |
| --- | --- |
| runtime/controller.rs | aa5faf99424c1f05797e08a4de5d9983a5cfacb9ab64e1add45f1b1f987d04d3 |
| shell_host/model.rs | 8a19731e3fb1445f2db8c32e9c1eb9db308227f65d396fcb451b02eb50ff87ed |
| shell_host/raw_relay/degraded.rs | baeceb73a7a5a76b345bab2e68e62cf79508065091daeb2547db80173e5eefe0 |
| shell_host/raw_relay/observer.rs | 050e9b928d321dc950771c6063317ab5398522ba14d24ea5c83b81cb81ac0243 |
| shell_host/raw_relay/pty_emit.rs | e50bab3706cfb85fd092f31f7837c0219104923cc728e01a446ec6b4013965a1 |

### 实际接线与安全边界

- controller.rs:65–121 仍先处理当前 token 的真实 command activity、ledger 和结算，再看显示恢复债务；本 token 仍 pending 时不提前 Restore，沿原 bounded timeout/Interrupt/Hold。settled 且 pending 且物理健康时在新 Emit/Capture/旧 end_token 之前返回 noneghost Restore，因而旧 lease 不被下一审批抢占。无损 pending=false 保留原流程。
- degraded.rs 仅在原 tagged + bound-token defer 或既有 committed presentation failure 上置新 pending 位。recover 的成功 fresh-region/ShowCursor 不清此位。没有扩大 generic io::Error 的捕获范围；parser transcript/storage/PTY/staging 等非物理错误仍向上返回。
- observer.rs:65–70 在输入锁仍持有时强制 failed||pending→Hold；degraded.rs 的显示后更新同样强制 Hold。因此受损恢复的 Restore→Passthrough 或 ghost 提前授予窗口被封住。原无损 ghost 的 observer 映射仍是既有行为，本补丁不能被描述为全面重写了所有正常 ghost 的输入发布顺序。
- pty_emit.rs:224–263 保留完整 Restore action，空 prompt 直接返回而不清 token/债务；物理初 flush、pending display、原 PS1、ghost 和末 flush 均经过 PhysicalDisplayWriter。失败仍 bound，可 defer 后重试，不重发 approved PTY command/HostResult。parser read/mark 的错误未经 tag，不能被假定物理故障吞掉。
- pty_emit.rs:265–281 仅在实际末 flush 成功后清 lease/pending，并返回一次 Hold；下一 observer 再依据真正 provider/capture 状态选择 owner。已失效 ghost 不因这次受损恢复被重新授予权限。
- merge_pending_prompt_restore 原实现仍会在 Hold 时丢 raw pending action，但 controller 依赖未清的共享 pending 位，在物理恢复且 settled 后持续重新生成 noneghost Restore。对本次受损原 PS1 债务，这条重发链成立；不需要为它再加第二个状态或泛化 pending merge。空 prompt 多轮也由同一链继续 Hold。
- bind/end/flag 的产品调用点均已核查，当前所有写入仍在 relay/controller 的单写入顺序中；输入线程通过 input-mode 锁消费权限。未发现 end 清 flag 与清 token 的两步顺序可在其间给输入线程授予新的执行权限。

### 完成 marker 与新 cwd/PS1 的顺序

`osc.rs` 的 precmd 分支在生成 CommandCompleted/CommandFailed 前调用 `start_prompt_display_capture()`；`osc/command.rs:205–208` 会清空旧 `last_prompt_display`。post-hook prompt_ready 也会从新边界开始 capture。Bash marker 的用户 PROMPT_COMMAND hooks 在最后 `_cosh_bounded_prompt_marker` 前执行。因此仅收到完成 marker 而新 PS1 尚未到达时，Restore 的空 prompt 分支保留债务/Hold，不会直接重画上一 cwd 的旧 PS1。

已有 `OscParser::has_prompt_painted_since_ready()` 可判断 ready 后是否有 display bytes，但其语义是“已有字节”，不能声称保证完整 PS1/完整 ANSI 序列；无现成 shell-after-entire-PS1 marker 可据此伪造完整性保证。当前读取未发现具体旧 cwd 复用反例，不建议加 sleep。真实 cd/动态自定义彩色 PS1、marker 与 prompt 分批/ANSI 分片仍应通过实际 PTY oracle核验，不能只检查字符串已非空。

### 测试阅读和执行限制

附带只读查看 degraded_tests.rs 增加的 fresh-region 后 Continue 仍 Hold 断言，以及新 raw CLI refault case/interposer。后者在真实 stdout write/writev 第二次命中原 PS1 `owner@host:` 时返回 EIO，且最终要求 hit 证据，不是故障未触发也通过的空控制。原真实 baseline/effect/HostResult/same Bash/无输入原 PS1 oracle未在此增量中删除。

本评审没有运行 cargo、构建、环境或测试；主任务报告的原真实 RED（effect=1、HostResult=1、same Bash，随后 prompt EIO 导致 raw shell 退出）是待绑定日志的执行证据，不能冒充本评审独立重跑。仍需 exact-source GREEN、有效可编译回退控制、空 prompt 多轮 Hold、末 flush refault、运行中 timeout，以及 no-input 原 PS1 文本/新 cwd/颜色/可见 caret。该源码结论不关闭 HANDOFF 的 U02a/U02b/U02c，也不升级成生产/release Go。


## R4 first real refault failure follow-up — blocking pending correction

主任务新增实际 `local-linux/r4f-production-prompt-refault.json` 已只读核实：Rust 1.97.1 exact raw test exit101；1 failed / 626 filtered；3.77s；effect=1、HostResult=1、sameBash=Some(44019)，before-input 当前光标行为空而 expected `owner@host:~$`。这是恢复位置硬契约失败，不是据此证明 Shell 已退出。前节静态0finding不等于该实测通过；当前验收保持阻断。

### [P1] 提前发布原 PS1 后，旧 native_prompt_after_run 标记仍会抑制 provider 终态之后的重画

位置：本次新增 `runtime/controller.rs:85–96` 的受损强制 Restore 分支；交互契约位于 `runtime/evidence_delivery.rs:43` 与 `runtime/dispatcher.rs:586–589`。

触发路径：真实 completion/HostResult 被交付时，既有 record_shell_handoff_completion 设置 `agent_run.native_prompt_after_run=true`。R4 在 dispatch/provider 后续输出前提前返回 Restore，实际输出原 prompt 并推进 display_start、结束显示恢复 lease。下一轮 dispatcher 才消费 provider 文本（真实用例为 `slice first done`），文本的 CRLF 可让光标落在原 prompt 下方空行。run结束后 render_owned_shell_prompt 仍见 true，清 needs_prompt_after_run 并直接返回，不设置 trigger_pty_prompt；此时原先依赖的“还有 native prompt bytes 待正常释放”已被 R4 提前消费，显示在历史行的 PS1不能让 caret 回到原行。

这是新增提前 Restore 与原状态位语义的具体不匹配；不应靠等待任意历史 prompt 字符串、移动断言、补新输入或放松 currentcursorline oracle掩盖。实际 transcript 的最终字节仍由 acceptance owner 采集，本评审未进入运行中环境，所以不把上述源码反例声称为已独立观测本次 CRLF 的确切 producer。

最小建议：仅在受损 token settled + pending 的提前 Restore 分支使 `agent_run.native_prompt_after_run=false`，保留 needs_prompt_after_run 和全部正常无损分支；明确这一次是故障期间的临时提前 native paint，不能免除后续 provider 输出完成后的原有 prompt trigger。继续复用末 flush 成功边界、原 parser prompt、prompt replay 和既有 trigger，不新增状态/CPR/共享 slot，不全局重排输出。若实际 transcript 表明另有 trailing bytes producer，应先核其输出和 trigger 次序，再定修复，勿凭候选添加泛重绘。

相邻有效回归应构造 HostResult delivered/native_prompt_after_run=true → 强制恢复成功 → provider terminal text/CRLF → run完成；断言最后 action 经现有 trigger 再次 Restore，且当前无输入行/颜色/cwd/可见 caret 与原 PS1 相同。另保 provider 长时间 Running 时提前恢复仍可保活/Hold、normal no-fault layout、once effect/HostResult、ordinary及第二 request真实通过。before-input child.try_wait none 可强化定位；不能用它替代 ordinary/二次request/once baseline，也不是单独新增源码阻断。


### R4 follow-up: needs_prompt_after_run cannot be assumed true

进一步完整检查赋值点后，对上一段最小建议作必要修正：`agent/intercept.rs:141`（及:90、approval/runtime.rs:74）按 `event.cwd.is_none()` 设置 needs_prompt_after_run。真实 marker 携 cwd 的请求可为 false；dispatcher.rs:581–583 在 !needs 时先直接返回。因此仅清 native_prompt_after_run 不能覆盖正常真实 marker 路径，前段“保留 needs”不足。

若 transcript确认提前消费后仍有 provider输出，该受损 forcedRestore 分支的现有字段最小写法应同时为：

```rust
inline_state.agent_run.needs_prompt_after_run = true;
inline_state.agent_run.native_prompt_after_run = false;
```

这是设置后续原生 prompt 的显示意向，不是发布输入模式或执行权限。放在 controller 该受损分支返回 Restore 前可行：若首次恢复写/末flush失败，pending+Hold阻止继续 dispatcher/输入，重试仍保留显示债务；若成功，下一轮 dispatcher在 provider终态后使用原 trigger恢复。无需为了这两个 runtime意向位增加 callback/第二共享状态。token和pending真实退休仍留在末flush成功之后，不能提前。应有 needs初始false/native初始true 的控制，避免只测手工初始化needs=true而漏掉真实marker入口。此修正不要求改任何正常无损路径。


## R5 narrow static re-review — dynamic P1 remains open

本轮仅复评 R4→R5 两文件增量，静态新增 `findings_count=0`。读取 HEAD 仍 `fd31f09b29e3a9a9fb617c9e404a7fa81c2e39bb`，源码未提交；R5 controller SHA-256 `0056f713eff19dda90d30d6f452c133245960ae0f7f3a654db0e9e40b0a88c1b`，support/ui_approval_slice.rs SHA-256 `462c80a24c948d6fcf2c0dbf9e549c9aafa85827c17201c80f7557dae0d0f662`。R4历史 controller SHA仍为前节 aa5faf…，其 forced Restore 为当时:85–96；R5对应:85–99，其中:94–95是两字段纠正。

R5确实只在“bound token 已settled、显示债务pending、物理healthy”的强制 Restore 分支设置 needs_prompt_after_run=true/native_prompt_after_run=false，并用一行WHY说明提前消费native bytes。该分支仍位于真实结算之后、新 Emit/Capture之前；原正常无损逻辑、HostResult唯一交付、token/input末flush退休不变。若prompt为空或refault，显示债务仍pending/Hold；两字段仅是既有终态显示意向，不会使失败write被当成功或开放输入。

support增量只为原 currentcursorline assert补row/col/screen/fault-hit/transcript失败诊断；期待文本、列、绿色属性、visiblecaret、无新输入时点、ordinary/第二request/once baseline均未放宽，也没有增加sleep/timeout。该诊断来源为fixture自建会话，未引入凭据读取或额外外部扫描。

未运行构建/测试，未查看运行中环境。R4实测P1仍开放：本节只确认最小源码纠正与建议一致，不得写“已关闭”；须等待R5 exact-source实际GREEN并保留R4 exit101和后续有效变异控制。实际末尾CRLF producer的诊断身份仍由acceptanceowner证据绑定。
