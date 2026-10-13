# 审批 UI 切片最终验证

最终 PR HEAD `b2e645ea42024ca1f583f52debbe57244af1080f`。实测 canonical HEAD `02e70598f4dd3ebedbe30f06580a4dcab5bef208`，最终 rebase 的 Cosh subtree 与 canonical YAML blob 均完全相等；原始运行元数据未改写。

- fmt、workspace all-targets Clippy、布局/库存/必要性及 commitlint 通过。
- Shell lib1606、bin2285通过，1既有ignored；共享重复696不重复统计。Logic9、protocol83通过。
- UI真实raw CLI：25通过、0失败/ignored。原先2条失败的oracle及窄屏fixture修正保留RED记录。
- Core lib184、非root bin1017通过；root权限fixture失败与非root复跑留证。其他workspace及raw/RPM packaging通过。
- FD close_range、持续TTY故障及staging窗口有实际编译执行的反例与恢复验证。
- 正式owned resize/fault canonical两条通过；8PNG目检与8视频帧像素核对通过；CJK、唯一完整卡、Deny、稳定Bash、一次效果、termios及进程清理通过。
- 标准聚合gate为Go，仅arm64/container/raw-cli/scripted-pty debug范围。owned环境cleaned；原借用环境保留。

验收工具resize渲染修正在独立skills仓库的三个owned文件中，未混入产品提交；6个针对原始cast的回归通过。包内保留精确patch与provenance，可复现视觉证据。

本轮模型为loopback fixture，不声明真实provider、双架构RPM、生产UI或默认Shell发布Go。
