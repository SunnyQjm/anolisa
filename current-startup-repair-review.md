# Startup / fresh-region repair 增量独立只读审计

本报告补充 `final-live-eligibility-review.md`，不覆盖或改写旧冻结候选报告。

- 基础 commit / 当前 HEAD：`c855492963b2cb2ddef54a2b357ab8de8642fbbf`
- HEAD tree：`4af240c7f6f18dcdadfeb82ade067eeb1d51824b`
- 当前状态：**该 HEAD 上的 dirty source 增量**，以下实际 SHA256 是本次审计绑定；不得声称旧 c855 commit 含此新增修复或已通过其新测试。
- worktree：`/Users/quejianming/vscode/cosh-shell-dev/.worktrees/cosh-track2-ui-approval-slice`
- 审计者：relay_behavior；source 只读，当前 source 经 ui_review 确认与 focused GREEN 一致、不再修改。

## 审核结论

此前已发现的 startup 错误 scrollout、partial acquisition 来源遗漏、failed-flush retry 丢 fresh region及直接 panel 入口绕 repair，在当前源码中已闭合。范围内未发现剩余确定 P1/P2；这不是生产 UI Go 或完整产品审查批准。

1. **Startup clean 不再被认定为 dirty。** activation 仅决定几何边界要求；`fresh_region_required` defaultfalse。worker missing / unexecutable 在 acquire 前失败，没有 rect或 Gate accepted来源，fallback保持 repair=false，不执行 CAN/full viewport scrollout。
2. **session存在不等于已拥有终端区域。** `region_needs_repair(error)`只判断 gate.rect存在，或当前 `SurfaceError::Gate(GateError::Write { accepted, .. })` 的 accepted>0。已 spawn但未 acquire、TooTall且没有写入均不需repair。正常成功withdraw留下的旧 accepted计数不被当作dirty来源。
3. **部分 acquire 与 owned-but-not-live 均覆盖。** Gate acquire只有完整 write_tracked成功后才记rect，因此 partial accepted>0/rectNone必须由当次Gate错误及时latch；完整acquire后到framecommit前live=false，但rectSome会要求repair。`present`错误分支在丢 session前保存该来源。
4. **先撤权、后 repair；错误不清必要标记。** invalidate在清claim前收集 inline/owned来源，先signal/fence/clearclaim。已有session且repairtrue沿session路径scroll一次；无session且repairtrue编码CAN/full scrollout。首flush、partialscrollout、flush或viewport复核Err均保留标记供重试，且不恢复旧claim。
5. **直接 panel 入口不再绕修复。** panel在ID/live快路径之前检查repair，转入helper。helper完成freshviewport后暂时清repair，避免同步递归；notice及panel包在同一Result内，任意Err会重新置repair并invalidate。panel自身在managed publication开始前置repair，完成write/flush/height/exactviewport检查后才清repair并提交claim。
6. **成功只清需要，不清约束。** worker或managed inline完整publication成功清 `fresh_region_required`，保留session级 `geometry_required`。无Pending时只有最终flush成功才清repair。geometry要求、当前claim和待修区域三者分离；未管理legacy保持原行为，不被activation或仅sessionExists误判需要full scroll。

## 证据与边界

本次未执行 Cargo、env或测试命令，未修改source、commit或push；只写此outputs报告。

只读回读 ui_review证据：

- `live-eligibility-scrollout/startup-red.json`：run `20261013T203144Z-ffcf6207`，实际1 test / exit101；首次startup RED到missing分支。不称unexecutable分支同轮RED。
- `live-eligibility-scrollout/repair-source-red.json`：run `20261013T203724Z-34a8bbc9`，实际1 test / exit101，partial accepted2但旧query判false。
- Root记录direct-panel RED run suffix `87448043`（Root提供；未独立回读完整run metadata）。该路径当前源码及测试断言已读。
- `live-eligibility-scrollout/startup-repair-green.json`：run `20261013T204704Z-e78e691f`，exit0，实际144 passed / 0 failed / 0 ignored；ui_review确认session4742结束且源码一致。该GREEN包含missing及0600 unexecutable startup两个分支，但coordinator未暴露errno，不能声称直接测得ENOENT/EACCES。

viewport ThreadLocal、ControlledTerminal及idle closed-TTY为组件模型；query accepted2不是实际TTY partial-write验收。startup fixture确实尝试未找到/不可执行worker路径，不称已有真实acquired region。真实TTY矩阵、完整quality gate、最终freeze和RPM/双架构验收仍由Root汇总。precommit/no-token保活不属于bounded postcommit保证。本报告不将源码审查、他人focused GREEN或旧commit候选等同production Go。

## 实际 dirty source SHA256

| 文件（相对worktree） | SHA256 |
| --- | --- |
| `src/cosh-ng/crates/cosh-shell/src/approval/slice_present.rs` | `9ed35713ae071dfc70a69e1c45eba449b4e54c530da6a1a14a298b306da8b299` |
| `src/cosh-ng/crates/cosh-shell/src/approval/panel.rs` | `d81af143b1c0c27db746665ee4dc0267408278d10a921365ab5ddd3f0d1edb99` |
| `src/cosh-ng/crates/cosh-shell/src/approval/surface_session.rs` | `669b07905fa626656a446dfa3d328f32801e1995bfd15452d6a6aab4ea912459` |
| `src/cosh-ng/crates/cosh-shell/src/approval/surface_session/tests.rs` | `3d82064dcff96f7cc23882e80a58d50e9578cfe972da89d67a664fe6e61f1b9d` |
| `src/cosh-ng/crates/cosh-shell/src/approval/slice_tests/live_eligibility.rs` | `43397a15f4172b6d8d51321b83478441c1d49c679f62f170bfd99219f1874d0d` |
| `src/cosh-ng/crates/cosh-shell/src/runtime/approval_ui.rs` | `7c56c69fc96004f3e0301b5dd1ea87810e3e167f52ed807f0a2beef0dfee209e` |
| `src/cosh-ng/crates/cosh-shell/src/runtime/approval_gate.rs` | `07ca165c9a5987f4f5c6d993b817c25f9fb8dc77e93653305a7348155dd191d0` |
