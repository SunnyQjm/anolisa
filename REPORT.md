# PR #6892 conflict validation

合并头 `b811c9742c80ff781be34293d12f073a3a433d88`、tree `e2866588aa9ea39fcf8a7e20c33eceed90fc9cf5` 的 aarch64 Linux Rust 1.97.1 功能验收通过，scoped gate 为 Go。标准 preflight 原始 `data.ok=false` 保留：唯一问题是原作者提交 d029216f 的标题 62 字符超过工具默认 50 字符。Root 已明确按仓库 120 字符硬限制记录例外；此处不重写历史、不将原结果改绿。

源码由 Root 独占，容器只读挂载。全部 6798 个 tracked 文件执行前后 SHA 一致，HEAD/tree 一致、tracked clean；Cargo.lock SHA `f3e07df2534be0498e46868f5427c6d207df50a2049b370e85cdd1cf212c4115`。相对 main parent2 为 5 文件 +155，三个入口限制 AI-off Agent 启动、insight 渲染和接受绑定；保留 main 的 hook consultation 正控。本任务没有修改产品源码、.env、lock 或依赖声明。

| 范围 | 实际结果 |
| --- | --- |
| failed_command focused | 41 PASS |
| intercept focused | 20 PASS |
| insight focused | 13 PASS |
| main hook AI-on/off 对照 | 1 PASS，包含两行对照 |
| wider Shell unit | lib 1625 + binary 3064 = 4689 PASS，1 ignored |
| wider logic | 11 PASS |
| qualified existing raw AI-off | 1 PASS |
| fmt / workspace all-targets Clippy | PASS |
| layout / source-layout / test inventory | 全部 PASS |

focused 与 wider 重叠，不能相加为独立 case 数。唯一 ignored 为 `gate4_real_core_uses_one_bare_toolless_request_without_touching_foreground_state`，要求另建 Core 的 Gate4 protocol 证据；不纳入通过。最初未限定模块的 raw `--exact` probe 命中 0，原记录保留且排除，后续 qualified raw 确认实际执行 1 项。既有 raw 使用 fake adapter，unit 也含 FakeAdapter；只证明组件/脚本契约，不证明真实 provider 或生产隐私链路。

独立 scratch 副本逐项移除三个 guard，使用独立 target 实际编译成功，再分别出现预期 2 / 1 / 1 个 Rust 测试失败（exit101）；不是编译错误。render 变异中的 ShellRewrite 正控仍 PASS。每轮仅一个指定 tracked 文件 SHA 改变，Root 只读源保持不变；恢复原副本后 8 项 AI-off GREEN。各轮 ELF machine=183、SHA 各异，原始 stdout/stderr、命令与归档 SHA 完整保存。

首次下载依赖因 rsproxy TLS 证书链失败，产品测试当时未执行；未关闭 TLS。随后仅从可读公共 registry cache 及已校验下载导入当前 Cargo.lock checksum 匹配的 crate 和公共索引元数据，在私有 Cargo cache 离线执行。未导入用户/凭据配置或既有编译产物。初次工具运行、零命中 probe、命令互斥拒绝均保留，成功离线重跑与有效 mutation RED 单列，不伪称首次全绿。

真实 Rust/Cargo 1.97.1 在自有 ALinux4 aarch64 容器执行；fmt/Clippy/审计由固定转发器进入同一 Linux 环境。standard-preflight-v2 为原始标准入口、base HEAD^2、默认标题50限制。最终实际 Shell ELF 与 source manifest 已 tar 归档并校验成员 SHA；各阶段测试 ELF SHA 在 source guard / mutation receipt 中保留。无宿主 Cargo 测试、无旧 ELF 复用、无性能结论。

环境 RUN `20261015T034016Z-f22bf781`；最终 build/test 进程 0，env down 成功、二次 down `already_absent=true`，私有 cache 已删除。mutation target 已先单独清除，副本随容器删除。未采购或触碰 Root 的长测 ECS，未重复 #7559，未运行 x86/RPM/真实 provider/full release，也未推送或调整 PR。

[最终证明](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-b811-after111/FINAL-PROOF.json) · [标准 preflight](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-b811-after111/standard-preflight-v2.json) · [源码及 ELF 证明](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-b811-after111/FINAL-SOURCE-PROOF.json) · [scoped gate](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-b811-after111/final-scoped-gate.json) · [mutation 原始归档](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-b811-after111/mutation-evidence.tar.gz) · [Shell ELF 归档](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-b811-after111/final-elf.tar.gz)
