# Persistent TTY 后续收口：Rust1.97.1

当前终态证据在persistent-r4；旧persistent/report为早前快照，不应混作终态。

已关闭本轮四个问题：timeout动作后的输入Passthrough窗口、failed重复observer的audit重复、Gate直写fd1错误来源丢失、readyApproved已知失败到actual master之间的输入窗口及permit Emit被吞。

## 反例与修复

- 80946b42：compiled/ran3，原正控1过，observer/postresolve均Passthrough≠Hold；实际0700 audit JSONL8≠2，dispatch cursor始终0。修后独立audit cursor，不粗推进dispatch。
- 009baf71：真实Core/Bash/PTY，liveworker1；实际approval.resolved audit写后首个withdraw CUP注入EIO，Approved回执尚未出现，effect0≠1。TtySurface仅实际fd1 write/非空zero标记物理来源，通用stdError source链保留；ioctl/geometry/storage/IPC不泛吞。
- 09ba47a9：actual decision component已提交但failed=false；cf3c724d：获本轮permit的Emit被failed通用分支改成Hold。
- e6500c22：同一真实链中暂停实际shell-handoff-request首次文件write；真实新stdin echo在400ms准备窗口写出forbidden-effect。不是模式setter或伪成功writer证据。

最小修复仅fact-bound readyApproved+TaggedError在stage前记failed；observer保留当前one-shot许可的Emit，同时同锁强Hold。token绑定与通用物理延期仍须actual master write成功；命令校验/暂存/master错误严格。

## 变异与恢复

7e1fa036仅禁用pre-master失败记录：compiled/ran1，真实stage新输入重新写出forbidden-effect。精确hunk恢复SHA等于原GREEN（见ready-mutation-plan/restore），没有整文件覆盖他人改动。

## 最终验证

最终final-green.json exit0：actual decision bin1 + 既有physical bin3 + strict emitter lib1 + real raw3，全部GREEN。实际real3耗时45.94s，包含原Approved文本故障正控、旧2s timeout（坏期持续新输入）和post-audit first-CUP故障（actual stage pause新输入）。各自liveworker1；正常effect1/timeout effect0、actual HostResult1，同Bash PID/startticks/cwd/后台job保持；坏期新输入不产生effect，恢复后ordinary/second request成功，timeout notice保留，无worker残留并正常退出。

bin组件没有新shared testcase count；emitter已迁socket/FD，仅实际raw3称PTY/Core/Bash。首hold-audit-red.json audit目录非0700被安全门拒绝，不算P2行为RED。

## 范围与交接

Source/env/cargo已明确归还Root；无mutant/scaffold，最后唯一session13847已exit0。本轮仅已批准bounded token域；不承诺precommit/no-token坏TTY通用保活，不新建交互/无OSC supervisor。

Root负责final fmt/amend/rebase、Core/Shell/worker候选构建、layout/inventory/preflight、最终UI矩阵与canonical验收。report-source.json是报告时源观察，不替代Root最终候选code-SHA；本文不宣布release/provider/RPM/performance Go。

精确runID、原命令、原JSON哈希、阶段来源和15个源码文件列表见report.json。
