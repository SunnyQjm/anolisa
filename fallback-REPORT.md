# PR #6892 caller fallback 回归验收

功能验收通过；aarch64 container unit/logic/raw-cli scoped gate 为 Go。标准 preflight 的 fmt、workspace all-targets Clippy、layout、source-layout、test inventory 与 drift 检查通过；原始 data.ok=false 保留，唯一元数据问题仍为 d029 标题 62>默认50，例外由 Root 管理。本报告不作发布 Go 结论。

本轮基线为 `b811c9742c80ff781be34293d12f073a3a433d88`。实际执行的是该基线加冻结的两文件 diff：Root 的 intercept.rs +15 与本任务的 intercept_tests.rs +195，未提交阶段由 source manifest 的 6798 个 tracked 文件 SHA 逐一绑定。测试文件 SHA `b4867e9ebe17aa026a777a0edebbee90590bd7473f5978a48162aa7e6a207f38` 从 RED 到 GREEN 未变；Cargo.lock SHA `f3e07df2534be0498e46868f5427c6d207df50a2049b370e85cdd1cf212c4115`，全部 tracked 文件在测试、mutation、preflight 后仍与冻结 manifest 一致。最终提交/推送由 Root 负责。

调用层测试实际进入 render_intercept_agent_guidance。b811 产品代码在 Rust1.97.1 成功编译后出现两个预期行为失败：idle matching ghost 产生 unexpected active run；busy queue 从1变2。AI-on bound queue、不同 ghost/ordinary input、health ghost 三项正控通过。原始结果和 machine183 的实际测试 ELF SHA 均已归档，RED-READY 在 Root 改产品前落盘。

Root 随后在 handled_intercepts 记录后、compaction poll 前增加 caller 消费分支。相同测试 GREEN5：匹配 id 和 legacy 无 id 的 AI-off insight 提交均消费 binding，无 active/queue/Thinking；busy 场景保留原 active 和已有 queue；不同 id、普通输入、health binding 与 AI-on 正控保持原路由。

| 范围 | 结果 |
| --- | --- |
| 新 caller 回归 | 5 PASS |
| intercept focused | 25 PASS |
| failed_command focused | 41 PASS |
| insight focused | 13 PASS |
| main-hook AI-on/off 正控 | 1 PASS |
| wider Shell unit | lib1625 + binary3069 = 4694 PASS，1 ignored |
| wider logic | 11 PASS |
| qualified existing raw AI-off | 1 PASS |

focused 与 wider 有重叠，不相加为独立 case 总数。唯一 ignored 是既有 Gate4 real-Core protocol 测试，不纳入通过。unit 与 existing raw 使用 fake adapter，只证明调用/脚本契约；没有真实 provider、x86、RPM、性能或 release 验收。

另在自有 tracked-only scratch 源码与独立 target 中，仅删除新 caller guard，保持旧 helper guard 与测试不变。变异实际编译成功，准确复现相同2项失败，另3项正控继续 PASS；恢复 caller guard 后5项全部 GREEN。每轮核对唯一变更文件及实际 ELF SHA，stdout/stderr 的独立 tar 成员 SHA 已验证。随后移除 mutation target，Root 源码未被变异触碰。

原生命令采用 cosh-lab test run 的 cargo test --locked --package cosh-shell --lib --bins FILTER -- --test-threads=1；logic/raw 使用 CLI 原生映射，具体 argv 在各 *.command.json 与 runs/commands.log。mutation 的独立副本命令为 cargo +1.97.1 test --locked -p cosh-shell --bin cosh-shell agent::intercept::tests::insight_intercept_ -- --test-threads=1。标准 preflight 使用 base HEAD^2/default50，Linux 转发执行 fmt/Clippy/三审计。未改写标准命令或降低 gate。

首次测试缺少离线 crate，产品未执行，不能计作 RED；随后用 Cargo.lock checksum 验证公共 crate/cache 与公共索引元数据后导入私有 cache。第一次 ripgrep 工具安装遇到 TLS 证书链失败，保留原记录，再用 ripgrep 自带锁 checksum 校验公共 cache、离线安装成功，未关闭 TLS。一次 rustfmt stdout 被 CLI 脱敏导致 fixture 文本不适合回写，已在实际编译前恢复原 HEAD 前缀，仅保留新增测试；原记录与修正说明保存。未读取/复制用户凭据配置，未改 .env、lock 或产品依赖。

profile cosh-pr6892-fallback-aarch64，环境 RUN `20261015T044911Z-777e9ea7`，ALinux4 aarch64/Rust1.97.1。最终实际 Shell ELF 已与 manifest 一起归档并核成员 SHA。自有 build/test 进程0，容器 env down 后二次独立回读 already_absent=true，私有 cache0。未采购、未触碰原8h hosts、未推送或修改PR。

[最终证明](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-review-fallback-after165/FINAL-PROOF.json) · [RED 交接](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-review-fallback-after165/RED-READY.json) · [冻结源码及 diff](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-review-fallback-after165/green-source.patch) · [标准 preflight](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-review-fallback-after165/standard-preflight.json) · [scoped gate](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-review-fallback-after165/final-scoped-gate.json) · [编译变异日志](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-review-fallback-after165/caller-mutation-logs.tar.gz) · [最终 Shell ELF](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-review-fallback-after165/final-elf.tar.gz)

[最终独立复核](/Users/quejianming/vscode/cosh-shell-dev/outputs/codex-takeover-20261013/acceptance/pr6892-review-fallback-after165/INDEPENDENT-REVIEW.json)：无阻断发现，源码/ELF/清零与结论边界均核实。
