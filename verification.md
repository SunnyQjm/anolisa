# 最终源码开发验收

提交：`9e092d16c4e10538747f429bf5d6454de012805c`。基线：`f571226499ea08006f14b2eb9b63d2050aab9e2f`。58 个变更文件在测试前后均核对 SHA256、mode、HEAD 和干净 tracked diff；见 `source-manifest.json`。

| 当前源码 / ALinux4 x86_64 | 结果 |
| --- | --- |
| Rust 1.97.1 / Bash 5.2.15 workspace | 9348 passed / 0 failed / 14 ignored；13 门禁、4 异 UID 用例通过 |
| Rust 1.97.1 / Bash 5.1.16 workspace | 9348 passed / 0 failed / 14 ignored；13 门禁、4 异 UID 用例通过 |
| Rust 1.97.1 preflight + 文档构建 | fmt、Clippy、六项配置门禁、commit lint、漂移检查与 cargo doc 通过 |
| Rust 1.88.0 release workspace | 构建通过 |
| 无注入基线采样 | 私有报告 200/200 联合完成，最大 27.942ms；release 入口 200/200 完整输出，最大 28.791ms；超 300ms、残留、过大/非法 UTF-8 输出均为 0 |
| 实际 Bash 登录 pre-prompt 就绪采样 | 每版开启 200、关闭 200，均成功退出且展示开关正确；开启最大耗时 5.2 为 50.949ms、5.1 为 52.172ms |
| 安装态 canonical | 两版各 6 个原有场景，覆盖 40/80/120 列、中英文、plain/nocolor/styled 和真实 login shell |
| V2 开发对照交错验收 | 7 个脚本化 journal/df 场景通过；V2 writer 新记录在当前 writer 提交后仍保留；抑制时缓存不变；程序替换和 Bash 均恢复原 SHA |
| 传回后复核 | 19 组证据全部通过本地 evidence verify；17 张当前版本截图逐张检查，文字隐私扫描通过 |

workspace 数字是 39 个测试可执行目标和 6 个 doctest 目标的 45 组顶层执行摘要，不是去重 case 数。每组另有 7 次成功 filtered helper 自测，未重复加进上述数字。17 项最终事件/兼容回归、9 项 frozen-baseline 回归和 panic 清理回归均在两版 Bash 全量里实际执行一次。

验收 harness 按 owner 将 root 专属场景与普通 UID 分开，Shell lib/host/protocol 单线程、raw CLI 四线程。这份冻结材料记录本地原生验收；标准 GitHub CI 另看 PR checks。

无注入基线保留实际主机状态，构建盘 89%/90% 的警告是真实采样结果。脚本化 OOM/99% 磁盘仅为隔离环境的受控文本输入，没有制造真实 OOM、填盘或调用 provider。V2 对照为开发提交 `7cefbf36e263c30b9bd0ea3408ff4a4ee9870ef1`，不将其称为已发布版本。公开截图全部来自当前提交的安装二进制；旧 reader 的原始回放仅保留在私有证据中。

测试后的 Bash 恢复曾因任务等待进程及持久 Workbench shell 占用挂载点而失败；准确识别并关闭任务进程后，正常卸载并核对恢复 SHA。V2 对照首轮误复用共享 target 缓存，随后刷新源文件时间强制编译，并核对二进制含 V2 文件名、不含 V3 文件名后重新验收；重跑初始化与 helper 路径错误也保留。最终结果来自成功的新目录，原失败记录未覆盖。

三路独立源码评审及修后复审无剩余 P0/P1/P2 阻断；详情见 `review-summary.md`。内部评审不替代请求的人工作者评审。

历史 v12 双架构四组日志另行保留。逐份统一计数后各为 9314 顶层 passed / 0 failed / 14 ignored，另 7 次 helper；旧 9321 汇总包含 helper。最终事件修复后的 ARM 全量未在本轮重跑，不沿用历史数字冒称当前双架构验收。

历史 ARM df60 首批三次 Timeout 保留。确定的有效预算预留缺陷已由正式反例区分并修复；固定同机 A/B/B/A 对照旧版 ARM 57/60、修复版 60/60，x86_64 两侧均 60/60。该结果不构成三次历史 Timeout 的排他根因证明，也不保证任意近界调度都成功。

本任务临时 ECS 删除回执 remaining=0，本地任务密钥和 known-hosts 已移入 Trash。M4/M5、真实 provider、镜像/发行版发布资格均不在完成声明内。本轮只请求评审，暂不合入，不启用自动合入。
