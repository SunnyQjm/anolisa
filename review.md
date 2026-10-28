# #9106 独立行为、组织与 L3 源码安全复审

未发现阻塞问题。

## 范围与规则

只读审查 worktree cosh-pr-live-state-20261026 相对 origin/main c894728f1 的完整候选，包括 HEAD 4d81db3e 与未提交修改，以及未跟踪 auth/activation.rs、tests/protocol/provider_activation.rs。全部变更/未跟踪产品文件 SHA 与 9106-green-v1-manifest.json 一致。

沿用已读取的根/组件 AGENTS、CONTRIBUTING、behavior-review、commit/documentation 规则，并核对本 worktree 测试布局条款。仓内实际只有 decisions.md 与 large-file-inventory.md，两者与评审机镜像逐字节一致；standard/review 使用评审机镜像规则。

## 行为核对

- Run 与 Registry 共用 Mutex<AdmissionState>。reserve、非阻塞 mpsc enqueue 与失败 rollback 同锁完成；service finish 使用同一锁。Run{queued:true} 直接转 Run{queued:false}，没有继任请求排队后的 Idle 窗口。
- cancel_pending 的继任准入仅在 Run{queued:false} 分支消费；Registry 不允许该路径。fresh enqueue 失败归还 Idle，queued enqueue 失败恢复原 Run 预留，不释放他人 owner。
- live Registry 的所有权交给 service，调用方 recv_timeout 不清 admission；service 完成/重置后归还。short activation 在锁外执行，独占预留由 RAII 在正常返回、错误与 panic 时归还。
- 实际锁序是 admission→command_tx；未发现反序获取。recv_timeout、provider 子进程执行与 service recv 不持 admission，service finish 不持 command_tx。不是新增通用调度器。
- activation 失败仅渲染 not-confirmed notice 并保留原 panel、provider selection、foreground model 与 startup probe；未知执行状态不报告成功或回滚。成功才清旧观察值并退出面板。
- 失败递增 field_capture_revision，旧 capture id 不再匹配；回归同时断言旧输入静默拒绝和 fresh 输入真实重试，避免仅测试捕获 id 变化。primary auth 与 active-run 模式字段未被该失败 helper 改写。
- auth.activate 成功后 Core 重建 provider，并同步 model、extra_params；失败响应不更新 live provider。真实 Core 配本地 HTTP fixture 的集成测试检查切换前后 endpoint、authorization、model、extra 参数及历史保留。
- 后台 compaction 仅在同一会话、较高 generation、较高 revision、持久化脱敏 transcript digest 一致时刷新；live 原消息保留，store.load 拒绝的 projection 不被复活，但 revision floor 保留。无新增 generation/revision 回退或换会话路径。

## 测试隔离与组织

新增 protocol/provider_activation.rs 通过真实子进程与文件 barrier 验证 adapter API 的 short activation/首次 start 互斥及 stale-cancel 不能穿过 Registry。它不是正常 UI 并发或真实 provider 验收证据。内层 admission/rollback/timeout/panic 检查是无真实服务进程的 private component/channel 测试。

UI 错误恢复检查为 private auth component test，使用 Fake/无 registry backend 故意制造错误；不能据此声称 UI 正常并发已复现。Core provider 更新使用真实 Core 与本地 fixture，不能称真实 provider。

background_compaction_fixture 本身不改 env；三个 async 用例在调用 fixture/await 之前取得既有 SLS ENV_TEST_MUTEX，并用既有 EnvVarGuard 恢复两个 telemetry 路径。返回 tuple 按字段顺序先恢复 env，再删除临时目录，最后释放锁；没有重入该锁。环境保真用例使用相同锁。SLS 暴露仅 cfg(test)+pub(crate)，不改变生产 public surface。新增错误日志保留 Debug error-chain 字段。

auth activation 方法抽到 auth owner 子模块，原大文件缩小；service runtime 526 行，没有新增 >700 production 文件。没有新 crate、依赖、lock、floor 或 Shell root/public API。Core/Shell 为同一 live-state contract 的必要配套，文档英中一致。未发现新增命令注入、路径/权限绕过；L3 为本次独立源码安全审查，没有运行安全扫描工具。

## 验证边界

本代理没有运行测试、fmt、Clippy、layout 或产品命令，没有修改产品、Git refs 或 GitHub。root 提供的旧源码 RED 与正在执行的 GREEN 由主任务保留和判读，本报告不冒称执行通过。最终运行证据必须绑定此 freeze；后续源码变化需增量复评。#9103 保持独立冻结，未纳入本报告。本轮禁止合并。

## 冻结后的唯一格式增量复评

protocol.rs 只将 provider_activation 模块声明移到 provider_lifecycle 前；模块名称、path、test target 和测试内容均未改变，无新增行为或组织阻断。worktree、9106-green-v1、combined-source 三份文件逐字节一致，SHA256 均为 edda01736d22e3554e5372762d38c2e9c0e9a0b144ac079a0191ba314dacba44。该核对不是运行 rustfmt 或测试。组合静态复审另见 combined-independent-review.md。

## green-v2 唯一 Clippy 增量复评

v1/v2 两份 manifest 均为 1436 文件，独立核对仅 headless/live_state_tests.rs 不同，唯一一行将 fixture 的 persist(&mut engine) 改为 persist(&engine)。v2 文件 SHA256 为 27e8c0d65a0aea9ffbfee7bc403a0da7eadb16aac676a2c2bd65ab91ae31d9b2。独立 #9106 的生产 persist 仍接收 &CoshCore，因此这是等价的测试借用收窄，不改 API/行为、不加 allow，无新增阻断。组合采用 #9103 的 &mut CoshCore 签名，保留该测试调用 &mut engine 是必要适配；当前组合字节与此前已审快照相同，后续真正合并时不能机械选择独立分支的 &engine。没有运行测试。

## green-v3 唯一格式增量复评

v2/v3 manifest 均为 1436 文件，独立核对仅 headless/live_state_tests.rs 改变；diff 仅把 `runtime.persist(&engine).expect("persist completed turn");` 从三行折叠为一行，表达式与借用语义完全一致。v3 文件 SHA256 为 b4a6f58e5f8962980e9743bcabf725b469ade59480506b9a5c50400cab5d0d15，与 manifest 匹配。无新增阻断；未执行 fmt 或测试，不将此前过早的 fmt 通过表述当作验证证据。组合仍保留已审的 mutable 三行调用，未因该独立分支格式修正改变源码字节。

## 2026-10-28：最终验收材料数字/措辞审计

只读核对 pr-9106-body-draft.md、9106-assets/validation.md、formal-review-9106.md 与最终原始receipts。green-9106-final-raw-cli.json 的exit_code=0，顶层summary为631 passed /0 failed/1 ignored；green-9106-final-shell-host.json 的exit_code=0，summary为232/0/1。汇总4656(serial lib+bin)+12(logic)+85(protocol顶层，nested child不重复)+631(raw)+232(host)=5616，existing ignored合计5；三份材料的数字口径一致。本文仅审阅已有执行证据，不是本代理运行测试。

材料如实披露串行unit与四线程integration组合、先前并行失败与fixture缺目录修复，未把它称为全parallel crate通过；localHTTP/Fakebackend/真实fixtureprocess与真实provider、安装ALinux4/default-login/release验收区分清楚。当前独立9106仍冻结v3；不因9103出现新finding而否定独立9106的这些证据。

发布前唯一措辞建议已发root：三份组合段目前仅称与#9103组合或combined-source-v4，应显式注明组合仅覆盖9103=977ffb8118da6d096706a90534d3f0e2fd2c3553，不包含待实现的Gateway mandatory与exitcode修复，防止后续同PR更新时误读。补齐该绑定后，现有数字与其余措辞可以用于请求正式评审；不构成全parallel/release Go，也不授权合并。未修改产品、正文或GitHub。

发布措辞复核闭合：最新版body、assets/validation与formal-review三份均已显式绑定组合所测9103=977ffb8118da6d096706a90534d3f0e2fd2c3553；说明后续Gateway/退出码候选需重新组合验证。上一节唯一建议已解决。**独立9106当前验收材料可用于请求正式评审**，不代表全parallel或release Go，不批准合并。
