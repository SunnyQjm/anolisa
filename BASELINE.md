# S2 FAIL 基线 — issue #2598 [Umbrella] 宿主注入非破坏合同（U2）

- 日期：2026-08-17
- Worktree：`anolisa/.worktrees/cosh-2598-host-injection`
  分支 `fix/cosh-2598-host-injection`，base_commit
  `385a098b136b8fb3e2ddc414ae83e71258ab50bd`（origin/main）
- 容器运行时：Apple `container` CLI 1.0.0（用户指定，不用 docker；
  cosh-lab 0.7.0 runtime 探测序 `container→docker→podman` 本就优先 container）

## 基线构成（四个子项）

### 1. SEM-019（#2541-B）— 本轮新固化 ✅ FAIL 基线成立

- 镜像：`registry.openanolis.cn/openanolis/anolisos:23.5`（bash 5.2，aarch64）
- rcfile：`rcfile-full.sh`，由权威副本 `extract_rcfile.py`（继承自 2539 基线）
  从本 worktree 源组装（marker/bash.rs + input_intent.sh 忠实复刻）
- 复现命令：

```bash
python3 extract_rcfile.py anolisa/.worktrees/cosh-2598-host-injection rcfile-full.sh
container run --rm -v $BASELINE_DIR:/exp \
  registry.openanolis.cn/openanolis/anolisos:23.5 \
  python3 /exp/sem019-repro.py /exp/rcfile-full.sh /exp/sem019-run
# 实际退出码 0 = FAIL 基线成立
```

- 结果（`sem019-run/summary.json`）：

| 臂 | payload 帧 | payload rc | 会话退出码 |
| --- | --- | --- | --- |
| candidate（cosh marker rcfile, ISOLATED=1） | `errexit-context` | 0 | **1（污染）** |
| oracle（bash --norc -i） | `errexit-context` | 0 | 0 |

- 与 formal 证据（core-formal-first-result-20260813T005909Z-1a3414c5
  SEM-019__interactive-login，candidate exit code=1 / oracle=0，双架构）
  事实同形：framed 输出两臂一致、唯一差异为会话退出码。
- 机制确证：payload 后 `set -e` 持续生效，DEBUG trap 内
  `_cosh_begin_attempt` 裸调用 `_cosh_utf8_han_status`（纯 ASCII 输入
  return 1）污染 errexit 语义下的会话退出状态。

### 2. NS-005（#2540）— 基线等价豁免（#1753 条款）

- 引用基线：`artifacts/cosh-2540-prompt-export-attr-baseline/`
  （base f0d47ea0，容器内真实 cosh-shell+cosh-core，candidate
  `declare -a`（-x 丢失）exit 1 / oracle `declare -ax` exit 0）
- 等价实测（2026-08-17，anolisa 主克隆）：

```bash
git diff --stat f0d47ea0 385a098b -- \
  src/cosh-ng/crates/cosh-shell/src/shell_host/marker/bash.rs \
  src/cosh-ng/crates/cosh-shell/src/shell_host/input_intent.sh \
  src/cosh-ng/crates/cosh-shell/src/shell_host/adapter.rs
# 输出为空 = 涉事路径零 diff
```

### 3. NS-009（#2539）— 基线等价豁免（同上零 diff 实测）

- 引用基线：`artifacts/cosh-2539-ns009-jobcontrol-baseline/`
  （base f0d47ea0，candidate 9/10 SERIALIZED / oracle 10/10 CONCURRENT，
  假设矩阵 v0–v6 + M1–M8，复现脚本权威副本 `repro_ns009.py`）
- 等价实测命令同 NS-005（同批零 diff）。

### 4. termios（#2537-RC-4）— 基线等价豁免

- 引用基线：`artifacts/cosh-2537-prompt-contract-baseline/baseline.md` B3
  （PTY-013：lflag 35387→2608 raw 残留，timeout+SIGKILL 路径，双架构）
- 等价实测（2026-08-17）：

```bash
git diff --stat f7b0485b 385a098b -- \
  src/cosh-ng/crates/cosh-shell/src/shell_host/raw_runner.rs \
  src/cosh-ng/crates/cosh-shell/src/runtime/terminal.rs
# 输出为空
```

- 注：termios FAIL 复现依赖真实 cosh 二进制（Rust raw runner），S5 验收
  时在容器内以修复代码构建真实二进制做 FAIL→PASS 对照（沿用 2537 基线
  的最小探针组口径）。

## S5 FAIL→PASS 对照计划锚点

| 子项 | 对照命令（同环境同驱动） | PASS 判据 |
| --- | --- | --- |
| SEM-019 | `sem019-repro.py`（修复后 rcfile 重组装） | candidate 会话退出码 = 0，payload 帧不变 |
| NS-005 | `ns005-repro.py`（真实二进制臂） | `declare -ax`，exit 0 |
| NS-009 | `repro_ns009.py` 10 轮 | candidate 10/10 CONCURRENT（判定口径：无 SERIALIZED/PARTIAL） |
| termios | PTY-013 口径 termios 前后对比 | 可拦路径全恢复；raw 持有窗口按 G1 裁决口径验收 |

## 文件清单

- `extract_rcfile.py`：rcfile 组装（权威副本，继承 2539）
- `rcfile-full.sh`：本 worktree base 组装产物
- `sem019-repro.py`：SEM-019 复现/判定脚本（权威副本，S5 对照同款）
- `sem019-run/`：candidate/oracle 转录（.txt/.raw）+ summary.json
