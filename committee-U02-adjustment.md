# inline 首版：已批准实施、U02 差异与验收

用户已确认 D1、D2、D3。#8028 实施整体撤出 #7333 worker/surface 集成，补回 K1–K5，不把仓库回到旧 main。新候选未冻结，委员会尚未批准范围调整，默认启用 No-Go。

## 必须保留的共用修复

| 项 | 必须保留的行为 | 验证 |
|---|---|---|
| K1 | 有界历史使用绝对游标与 base 完整传递，handoff 正确结算 | base0/非零、正常/缺 preexec 的有效 RED/GREEN |
| K2 | 不同 composer 请求清空旧草稿选择 | 同文本同光标不同身份的旧选择负控、新请求默认选择 |
| K3 | capture batch 在 mode 锁内发送；消费端同锁 drain/observe/mode 更新 | 双端锁序见证与真实分割/合并输入，不保留 worker 框架 |
| K4 | Core 构建前置及后续分层测试门禁 | 非零 targets、完整输出与 preflight，无删断言缩门禁 |
| K5 | 后续独立兼容/安全/数据修复 | 7489 inline RestorePrompt、6787 byte-exact、7421 gates 等逐条保留；6808 PATH 及 7628 候选正式评审另核 |

不采用 #7979 或未提交 worker 恢复代码，不新增 Bash/Readline 模块，不改 PS1 变量原文，不引入生产 CPR/sharedslot。原始失败与旧候选保持归档。

## 原 U02 合同逐项处置

| 原条款 | 首版实际边界 | 保留底线 | 决议状态 |
|---|---|---|---|
| U02a 单次失联、旧代次/后代持 IPC 迟到撤权及重建 | 无独立 worker，不提供独立 UI 故障隔离、进程重启或重建；不能以删除 IPC 将原业务义务记 PASS | Host 健康时旧请求/身份不匹配事件不得获得新批准权 | D2 用户批准调整送审；委员会待决 |
| U02b 持续失败、Running/Unknown 与归还 | 持续 TTY 故障、Host/UI 致命故障可结束会话，影响前台任务和作业；不保证旧 Bash/cwd/jobs 保活 | 不新增为恢复画面而 kill/replay 的行为；Unknown 不伪装成功/取消；真实效果与会话状态分别记录 | 原完整合同不 PASS；需委员记录影响、责任、补齐或复查条件 |
| U02c 用户显式接回及切换后新输入 | 不交付任意故障下的原终端接回。健康空行 Shift+Tab 或 `/mode routing shell-only` 只是辅助模式切换，不是 Core 关闭或取消 | 正常消费者正确、旧字节不得批准新操作、关闭后不自动恢复辅助 | 原完整合同不 PASS；默认启用仍独立批准 |

## U02-I01–I05 与最终验收

| 验证组 | 必需证据 |
|---|---|
| U02-I01 健康控制 | 安装版真实 Core/PTY，approve/deny/cancel、恰一次效果、迟到/身份错误负例、必需审计失败零 dispatch/effect |
| U02-I02 原生交互 | PS1 原文/文字/颜色/cwd/caret，首条新命令恰一次、read/PS2/heredoc/前台输入，chunk/paste/旧字节正负控 |
| U02-I03 故障事实 | Host 仍响应的呈现失败与 Running/Unknown 分开，实际效果/进程/会话状态；无新增自动 kill/replay；原平台阻断 C2/D 不重启 |
| U02-I04 健康切换 | 健康空行模式切换、草稿/卡片/前台边界，shell-only 不自动恢复；不得宣称故障接回 |
| U02-I05 故障域外恢复 | fresh 认证到可信 Bash、禁用/修复/回滚，恢复后续产品登录；明确旧会话/任务不保活 |

以上是待执行要求，不是通过结果。完整清单见[已确认验收合同](evidence/33-inline-validation.md)，其余 34 项原范围不因 U02 调整而缩减：同源原生双架构 RPM、五项 payload 且无 worker，安装/卸载/重装/升级回滚、真实 SSH/PAM、实际 VM、离线救援、AI-off 与真实 provider 完整闭环、S02 fd EFBIG/Bash 正控/恢复、N50/idle/完整 8h 及真实 10×3 tasks、有效归属、截图/cast、原始失败和独立清理零。

新源、工具、用例或 profile 改变即重新绑定冻结身份和适当回归；旧 v7 partial 不可升级为完整 8h。D03/D04/S03 按原底线与已批准延期收件，未索引为 Blocked。正式 code review/CI、产品验收、委员会范围决议、镜像/政策/灰度交接和默认启用分别留痕。

D03/D04/S03 已核到原人类批准 data:L987，并绑定当前源码 10 个文件；[脱敏收件表](evidence/37-DATA-D03-D04-S03-RECEIPT.json)区分批准范围、现有实现与待补最终用例，不代表这三项已 PASS。
