# #7891 独立 Linux 本地验收

本地已测范围及标准 aggregate gate 均为 Go；正式发布结论未作出。准确 native commit S6、真实单提交 lint、独占容器清理及实际 inventory absence 均已完成。

## 来源与环境

实际运行来源为 base `2b4af68af60880790092011b96d204b33adb0c0b` + staged candidate tree `ec6349fd690403b2e4003e846e3f8234daf1f6d0`，19 文件完整 patch SHA `df0d825fc8494d008e78c1152dd42d4a95b4819f5c7a82db61e5a9ea4135020c`。源 archive、1307 文件 build manifest、RPM Source0 全文件 hash 和前后读回均保留。没有把 dirty source 冒称提交 HEAD；后续 rebase/commit 仅可追加等价链，不改原 run 标签。

独占 ALinux4 arm64 容器 `cosh-7891-production-20261016`，env `20261016T084049Z-5880afba`，2CPU/6GB。Rust/Cargo 1.97.1，私有 CoW cache 与 target；禁全局自更新，未写 Root cache。所有环境/测试/传输走既有 cosh-lab。

## 具名测试与反例

R5 debug 34、production 23 均原具名 exact 非零通过。原 3 个 physical-fault 加第二次 prompt-EIO 反例均保持原始新输入前 PS1 颜色、cwd、当前行光标和 visible caret 断言。R3/R4 真实失败及其原始 bytes 保留；R5 最小修后同 oracle 通过。

真实 release 编译变异：heartbeat 3→1 导致原 idle12 反例失败；pending getter=false 导致原第二次 prompt-EIO 反例失败。分别有未改 harness 的 fixed R5 positive。真实 profile owner、深层 writable ancestor、symlink 注入均在真实 Core/card 前置后得到 worker1/0 预期 guard 拒绝，恢复 profile 正控通过。协议 stub Core lifecycle 结果不冒充真实生产 Core。

完整原 raw_cli 首轮 `110455-7da86edc` 为 610/16/1，原始日志完整保留。8 composer 在产品 launch 前缺 archive 下物理 target；8 zsh 用例所在环境未安装 zsh，保留实际 rpm/command-v 事实，不标 flaky。仅补 owned 容器 zsh/pcre 和 ignored fixture target 目录、未改源码/原 argv/阈值后，完整同命令重跑 `114618-abd375a6` 为 **626/0/1，2346.92s，exit0**。原 ignored zsh native completion 原样保留。1307 源文件前后匹配。

候选 preflight 必需两 gate 与 fmt/workspace-all-targets Clippy 实际通过；额外 source-layout 是独立 Linux Bash5.2.15 实际 exit0。首轮 Bash3/并行环境锁 tooling 失败保留。staged candidate 的空 commitlint range 不算新提交 lint；Root 最终 S6 另做。

## 原脚本真实 RPM 与安装

原 `scripts/rpm-build.sh cosh-ng`、原 spec workspace release build，Rust1.97.1。基线 a37 的本地事务版本 0.27.0 不含 worker；候选本地事务版本 0.27.1 含 worker。版本仅测试事务标签，不冒历史 release。

RPM Source0：baseline 1296、candidate 1297 文件逐 hash 匹配。原 rpmbuild 自动 rmbuild 删除 BUILD，未留 pre-strip ELF；如实保此边界，以 RPM 内 post-strip ELF 与安装外部 SHA 一致为身份链，没有拼 payload 或改变构建参数。

已实际 install baseline→upgrade candidate→reinstall candidate→rollback baseline→uninstall。每步文件所有权/模式/SHA/`rpm -V` 读回；基线 worker 不存在，升级后 worker 由 candidate RPM 拥有，回滚后 worker 与 candidate 独占 build-id 路径消失，卸载后 package 与两包 payload union 及 profile 目录均不存在。

候选安装三 ELF：

- Shell `e28e34ea5f9ece2fdeaf2e4254fc8096f2ad1bb4a9edcf3e9e2520de43778ee9`
- Core `866e28cc643c6871fc4312a66f3dab79deb8376e8130d484f4a32019ed0056d5`
- worker `76b7844d3c29ef5a5c843c005ba834661f4762e57c350edeee5c1b402d8f0407`

installed 原 harness eligible/closedloop/deny/第二次 prompt-EIO/idle12/debugenv 注入隔离六个 exact 均各 1PASS。实际 worker `/proc` 身份有原断言：sibling ELF、Host parent、独立 session/pgrp、cwd `/`、空环境、fd0..2 `/dev/null`、fd3 socket。deny 的原 inline comparison 使用 debug Shell，单列而不混称 installed。注入不存在 worker 路径元数据 null 不代表真实 sibling 缺失，ledger 实际 SHA 为安装 worker。

## Canonical 与视觉

原两个 YAML ID/input/expect/evidence 不改，只在 owned variant 将 command 指向实际安装 profile 并 `--production`。两个真实 case：resize `125014-316465a4`、fault `125120-b240c26b` 均 exit0。固定 owner renderer `6684b54820f9d3c475b80d6595bffeb8d64529f9` 的只读归档处理真实 r 事件；标准 verify 两者 verified:true。

八点 source SHA/event/time/geometry、最后 PTS≤point、PNG/WebM SHA 和裁剪逐像素比较通过，最大 RGB 差 2；已实际打开 8 PNG。完整 CJK 与 sentinel 历史、唯一完整当前卡、Deny 焦点、窄屏过期提示/新卡、Bash Ready 均核验。两条副车 production=true、UI test env 空、三 ELF 同安装、effect1/request2/HostResult、稳定 Bash/termios/零残留；fault 为三个不同 worker，首代同 worker Allow→Deny→Allow 完整物理 frame 后才 kill。

两个 bash-returned 截图为显式 printf UI_BASH_READY;exit 后终态，不能当输入前空闲 PS1；该强证明来自 installed prompt-refault 原断言/副车。canonical 仅 loopback HTTP 模型，非真实 provider。archive manifest/provenance Git null 原样保留，通过 Source0/RPM/ELF/variant 和外部 source binding 关联，不伪造 Git。

## 最终身份、清理与范围

准确 native commit `b353d6185b2abe0b99460430ccd7954bd4ce21ad`，parent `585d71fd3f6a95a9d3fb5fec50ab721fcf767306`，tree `cf23b75a2c151da8e85a16e44b3653422cbb4f7b`，Cosh tree `f1dbd5bd1cee77ee311a9a104aa539dcdd692afc`。19 文件/1307 build-source hash 及完整 patch 与已测 2b4/ec 来源逐等。最终 native commit 全 S6 再跑：fmt、workspace all-targets Clippy、Shell layout/inventory 全通过，6 native Cargo exit0，inventory 1100/189/3092/1625 非空；独立 Linux source-layout exit0。真实 Git log/lint 范围精确 1 条 b353d；固定 CLI `commit_lint=[]` 代表零问题而不是空提交范围。原始正文/Signed-off-by/命令与实现 hash 已归档。没有改旧测试、RPM、canonical run 来源标签。

标准 CLI down `130601-c8f9f21b` cleaned，仅清本任务 owned env。随后 env status 因 backend 已不存在返回 environment-unavailable，原始结果保留；独立 `/usr/local/bin/container list --all --format json` exit0，确切 container name 与 run label 均 absent。其他容器/cache/冻结对象未动，全部 RPM/SRPM/cast/PNG/WebM/JSON 保留。

同九项原 aggregate argv 原样重跑 exit0，`data.verdict=Go`、`errors=[]`；首轮仅环境未终态的 Blocked 仍保留。RPM 已卸载，union payload/profile 路径无残留，最后 installed capture Cosh 进程为 0。独占容器实际不存在，cache 作为证据保留。

正式 dualarch、真实 provider、默认登录/systemd、全 workspace 测试体、性能 SLO 不在本报告 Go 范围。
