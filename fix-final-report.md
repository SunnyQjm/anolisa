工具源码已可交付；Root 仍需新目录标准 CLI 8 点渲染、verify 和目检。未修改 Cosh 产品源码、3ELF、原 cast、pass/index、dirty CLI、快照、依赖或锁文件；没有 env/cargo 运行。

有效 RED：原 cast 的 resize 前后 PNG 都宽 787，1 case 实际失败（original-red.txt，2.509s）。最终 GREEN：6 cases 实际通过（final-green.txt，20.089s），覆盖原始录制实际尺寸变化/不可变、Deny cutoff 与后续 Allow、ED3 历史清除、最后 PTS<=651ms 的视频像素与 PNG 一致、来源 head 反控、无序/非法 cast、constructor 清理，以及 kill 失败不虚报清理成功。

原始 o/r 顺序进入隔离 tmux 的真实 TTY；每个 cutoff 取得实际 grid，再用明确标注的临时 derived projection 交 agg 静态栅格化。PNG 保持当时 native viewport。WebM 使用最大 native 图幅固定 canvas 并在右下留白，帧 PTS 对原 source time 向上取整到毫秒，同毫秒保留最后状态，不提前后续事件。每点附原 cast SHA、source head/event/cutoff、viewport、图幅、编码 PTS/map、产物 SHA、renderer 版本及清理证明，既有 verify 对其校验。视频依旧是完整 cast-replay，有 3 秒尾帧；不是单点 clip。无 resize 原 agg 分支保持。

只需运行 owner runtime 的现有 evidence CLI，不需同步 snapshot：

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/quejianming/vscode/cosh-shell-dev/skills/runtime/cosh-lab/src python3.11 -m cosh_lab evidence render <existing arguments>
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/quejianming/vscode/cosh-shell-dev/skills/runtime/cosh-lab/src python3.11 -m cosh_lab evidence verify <existing arguments>
```

仅 evidence.py 和新的 resize_render.py 是运行时同步单元；测试文件不需分发。具体 SHA 和全部边界见 final-report.json。工具已退出，源码/host 测试槽已交还 Root。

模型测试证明 terminal/media 合同，不代表真实 Core/Bash 业务链；no-resize 本轮仅源码确认原路径保留，未声称旧测试全量已跑。原 cast 测试依赖当前 workspace 的既有绝对 acceptance artifact 路径。Root 的 8 点目检才确认实际 Worker/Role/CJK/bottom/Deny 时序。
