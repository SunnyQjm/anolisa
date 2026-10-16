# U02a / U02c generation 与显式接回审计

只读范围：7891 worktree `/Users/quejianming/vscode/cosh-shell-dev/anolisa/.worktrees/cosh-7891-ui-worker-production`；HEAD `fd31f09b29e3a9a9fb617c9e404a7fa81c2e39bb`，HEAD tree `a1ad327ce78bccf62021adb2c962ab9fcac433ff`。当前有未提交增量，以下实际源码hash为本次观察绑定；不是最终发布候选或运行通过声明。未修改源码、操作环境、读取.env/credential或运行测试；仅写本报告。U02b/persistentTTY prompt由review_7345负责，本报告不重复审核其实现。

已读 `production-worker-20261016/acceptance/tool-source/HANDOFF-NEEDS.json`（SHA256 `08390a4f030b9fa9dcc1d05aa83ca3818432a780b684f1af29cf13a6519e1918`）；其中明确仍需 U02a genuine old-generation/descendant IPC witness、U02c public explicit terminal takeback + consumer evidence。旧v7工具证据不可充作新验收。

| 验收项 | 当前代码/测试映射 | 当前判断 |
| --- | --- | --- |
| U02a：旧generation消息拒绝 | `runtime/ui_coordinator.rs:450` PreparedFrame身份与active key校验；`:542` failure清inflight/published、take旧process并kill/reap，generation递增；process每次spawn创建新UnixStream pair | 有实现和协议负控，但未闭合真实后代迟到见证 |
| U02a：后代持旧IPC跨重建 | `ui_coordinator/tests.rs:491` 的old-generation fixture仅由当前worker发送`generation-1`（`:144`）；`:433` SIGKILL只断言direct child消失和generation2 | 没有fork后代持socket、父死后实际latewrite、与新代positive并存的测试；普通kill-loopback不能替代 |
| 旧raw-input generation失权 | `shell_host/raw_relay_tests.rs:192` 调用受控reader矩阵；旧read/suffix在observer失效后变CaptureInputRejected，fresh gen Enter仅产生一次Approve或保留Deny；`:396`实际consumer经UnixStream传输且断言无旧输出 | 真实input worker/component覆盖；不是后代IPC/真实TTY接回验收 |
| 新consumer仅接收新字节 | `raw_input/spawn/reader.rs:23-39` 在read前后比较ownership；`input_router.rs:378-415`验证身份与input_seq>publish_seq；router tests有stale-seq、epoch、worker-generation负控；shell_host relay integration有capture-chain旧suffix拒绝 | 有底层构件与部分真实Bash integration测试，无公开takeback动作把这些构件串成同终端切换见证 |
| U02c：明确接回原终端 | 未找到独立public takeback入口；现有Ctrl-C/Esc是取消/中断，`/send-to-shell`是发送特定审批命令，`/resume`是会话恢复 | 接口与端到端证据缺失，保持OPEN |

## U02a：确切边界与最小补证

- `process.rs:241` 每次worker建立新socket pair；`ui_coordinator.rs:552-577` drop旧WorkerProcess、推进generation后重建，可在代码上隔离旧端点。`:450-470`拒绝generation/frame/capture身份不一致。
- 现`coordinator_rejects_late_frame_from_prior_generation`是实际IPC fixture的字段伪造负控；不是一个已失效generation的实际进程/后代在新代启动后继续发送。
- `process.rs:329-342` kill/wait的是direct child PID；当前代码没有证明已持IPC的fork后代被杀或reap。端点失权与后代清理应分别给证据，不能以旧parent不存在推导后代不存在。
- 最小补证：沿现FixtureBinary fork一个记录pid/starttime且持旧IPC的后代，Host故障重建后由该后代发送旧frame/heartbeat并记录实际write/EPIPE；同时新代完成合法frame publication。断言旧消息不进入draw/capture/businesseffect，新代正控成功；最后显式清理该后代并核对身份。无需新增UI平台或把生产恢复policy改成迎合测试。

## U02c：当前公开行为不是 takeback

- Hold路径 `raw_input/spawn/capture.rs:172-175`只转held events，不把普通文本送PTY；`raw_input/relay.rs:304`的取消控制产生CtrlC事件。
- `runtime/controller.rs:85-108`在bound token且display_failed时先收集既有结果/timeout，再返回Hold，早于普通cancel dispatcher。故不能声称Ctrl-C已经完成显式原终端接回。
- `runtime/cancel.rs:18-79`定义Agent/approval/question取消；`tests/raw_cli/provider_handoff/send_to_shell.rs:4`只证明用户显式发送特定命令并后续回到Shell，不证明坏UI期间接回consumer。`RecoveryMode::ManualReconnect`只有类型声明，未发现生产赋值或public入口。
- `surface_session.rs:279-280`的RenderRequest使用capture_id=None；当前router token单元测试不能自行证明真实stdin已从旧UI consumer切回原Bash。实际raw consumer所有权由RawInputMode链处理，两层不能混作一条已验收链。

最小范围建议：Root先冻结一个明确、可发现的接回入口（不要把取消/中断暗称接回），沿既有raw mode锁/ownership epoch切换consumer；切换前已读与同readbatch余量必须丢弃或显式拒绝，不可重放到Bash。用真正PTY记录同一Shell PID/starttime/tpgid，切换前带唯一旧canary/旧Enter，动作后只输入新的命令并证明仅新字节产生一次效果；用户的原Shell prompt必须持续可见/恢复可用，不能以另启Shell、退出重连或kill-loopback替代。既有Approved/Running/Unknown结果不因接回动作被撤销或伪造；其业务/prompt细节仍属review_7345范围。

## 结论与证据限制

U02a有防线与局部真实测试，后代持IPC跨代迟到见证仍缺。U02c未找到符合要求的公开接回入口及真实consumer切换证据。两项均不能标关闭，不是production Go。本次仅读源码和已有HANDOFF文件，未复跑任何测试，不能将测试名称或源码断言当最终HEAD/RPM验收通过。

## 实际源码 SHA256

| 相对7891 worktree路径 | SHA256 |
| --- | --- |
| `src/cosh-ng/crates/cosh-shell/src/runtime/ui_coordinator.rs` | `97c967a0b89cf5e41b7e4554e0dc580df2445f979bde59705c370b1d90486e8c` |
| `src/cosh-ng/crates/cosh-shell/src/runtime/ui_coordinator/process.rs` | `f861c37cffe08a28bc3d4a3c8aeb9181cefddbe7c510aae0dea95ae5ccbd9b94` |
| `src/cosh-ng/crates/cosh-shell/src/runtime/ui_coordinator/tests.rs` | `c1442cab43154c194ad59f3758466a1df57a68176d809e357083d0d612dc1bc8` |
| `src/cosh-ng/crates/cosh-shell/src/raw_input/input_router.rs` | `5c458914b16b89913035a212afcade187950603ffa2ac425df81a581cc5ceaae` |
| `src/cosh-ng/crates/cosh-shell/src/raw_input/input_router/tests.rs` | `171c981d18e58a3e7d5af6bb11ee03c2f375a8fa4e272d9125d1f07b23939628` |
| `src/cosh-ng/crates/cosh-shell/src/raw_input/spawn/reader.rs` | `104ae9c4a4c23eb9da8400185849a686c6ddbb1413ec4951a6e4572921aaa1c9` |
| `src/cosh-ng/crates/cosh-shell/src/shell_host/raw_relay_tests.rs` | `97c2124243e3b9dfdf5d1f1bdd6717187e59f35154c2abc037e22f8dc7fddbbb` |
| `src/cosh-ng/crates/cosh-shell/src/runtime/controller.rs` | `115badec302c85ccdaf357b308d5708f6c315d10b980a996827a503c7f28a1b2` |
