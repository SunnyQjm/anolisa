# T1 机制交互预检报告 — issue #2598（Gate：PASS，2026-08-17）

环境：Apple `container` + registry.openanolis.cn/openanolis/anolisos:23.5
（bash 5.2，aarch64），真实 PTY。

## 流水线

```
rcfile-full.sh（worktree base 组装）
  → prototype_patch.py（M4 行执行期 trap 退场，2539 原型）→ rcfile-m4.sh
  → t1_combined_patch.py（M2 守卫化 + M1 errexit wrapper）→ rcfile-t1.sh
```

## 结果

| 验证 | 结果 | 证据 |
| --- | --- | --- |
| SEM-019 翻转 | ✅ candidate 会话退出码 1→0，payload 帧不变，oracle=0 | `sem019-t1/summary.json` |
| NS-009 翻转 | ✅ 转录级 10/10 并发（`[1][2][3]` 互异）；summary 判 9 CONCURRENT + rep1 PARTIAL 为分类器伪影（见下） | `ns009-t1/summary.json`、`candidate-rep1.txt` |
| V-B s1 exit-parity | ✅ `set -e; false` → 两臂 exit 1（交互 bash 5.2 errexit 本就杀会话，实测钉死） | `vb-probe/s1_false_exit-*.txt` |
| V-B s2（=2541 V-B4） | ✅ `false && :` → `$?`=1 不退出；候选存活、errexit 保持、干净 exit 0，与 oracle parity | `vb-probe/s2_vb4_prompt_chain-*.txt` |
| V-B s3（=2541 V-B7/B8） | ✅ set -e 下未知命令 → 两臂 exit 127 parity（veto/cnf 链无额外破坏） | `vb-probe/s3_unknown_cmd-*.txt` |

## 实测新结论（回写 spec）

1. **交互 bash 5.2 + set -e 会在顶层命令失败时退出会话**（oracle
   `--norc -i` 输入 `false` → exit 1）。SEM-019 类断言必须用两臂
   parity 口径，不能用「绝对存活」口径。
2. **2541 开放边 B-2 已闭合**：prompt 链「先恢复 errexit 再
   `return "$status"`（非零）」不复现杀会话（s2 格绿）——M1 的
   prompt wrapper 可用统一出口恢复，无需把恢复挂到下一次 wrapper
   入口。preexec veto 路径维持延迟恢复（D4 原样）。
3. **NS-009 分类器伪影**：修复后首行 `[1] pid` 与 preexec OSC
   marker 同行导致 job_starts 漏计首项 → PARTIAL 误判；方向保守
   （不会伪造 PASS）。T7 验收判读口径：无 SERIALIZED + 转录人工
   复核 PARTIAL 项作业号互异即 PASS；同时保留 summary 原始判定。

## Gate 结论

M1×M4 组合无冲突，SEM-019/NS-009 双翻转、V-B 组合格 parity 全绿
→ 进入 T2 实现。
