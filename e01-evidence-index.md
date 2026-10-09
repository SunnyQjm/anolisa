# E01（#6787）真实 PTY 证据索引

执行日期：2026-10-09。执行者：本会话。状态：**已执行**（runbook 中"尚未做"一节作废，见文末勘误）。

## 候选身份（同版对照，差分仅 `fed53bf2d`）

| 标签 | commit | 二进制 sha256 | 大小 |
|---|---|---|---|
| prefix | `fa8442c82`（PR 父提交，即修复前 main 状态） | `1a5b2240abae984dacffa671b7f47e71112192a61946d5969bad662e6dad3f91` | 36652488 |
| postfix | `fed53bf2d`（修复） | `6aab9f76cefebb453f91714cb1b3225be9955ba74ce3df99922d7b592e4732a3` | 36659448 |

构建：各自 worktree 内 `cargo build -p cosh-shell --bin cosh-shell`（postfix 在
`anolisa/.worktrees/cosh-6782-trust-key-exact-command`；prefix 在临时基线
worktree `anolisa/.worktrees/cosh-e01-prefix-baseline`，target 目录用 APFS
clonefile 复用依赖产物，仅本地 crate 重编）。

## 案例与判别设计

案例文件 `e01-trust-key.case.yaml`（sha256 见各 result.json 的 `case.sha256`，
六格同源）。fake adapter 场景 `stream multiline tool approval` 提议的命令是
真换行的 `printf one\nprintf two`（`adapter/fake/stream_tool_approval.rs:216`
附近 `emit_bash_tool_after_short_delay(..., "printf one\nprintf two")`）。

两个预置 HOME 只差信任键拼写，写入后按字节回读核验：

- `/tmp/e01-pty-home`：`trusted_commands = ["printf one printf two"]`（单行，
  十六进制 `...6f6e65207072696e74662074776f`，空白为 0x20）
- `/tmp/e01-pty-home-exact`：`trusted_commands = ["printf one\nprintf two"]`
  （真换行，十六进制 `...6f6e650a7072696e74662074776f`，0x0a）

## 结果矩阵（2 二进制 × 3 案例，全部 exit_status=0）

| 案例 | 断言 | prefix `fa8442c82` | postfix `fed53bf2d` |
|---|---|---|---|
| E01-PTY-001 | 必须出卡（`contains: Allow once`） | **FAIL** `missing text: Allow once` | **PASS** |
| E01-PTY-001R | 必须不出卡（复现形） | **PASS** | **FAIL** `unexpected text: Allow once` |
| E01-PTY-002 | 精确键正控，不出卡 | **PASS** | **PASS** |

双向翻转 + 正控不变：修复只把"变体拼写"从免卡移到出卡，精确拼写的合法信任
行为一格未动。

## 截图等价类（sha256 前 16 位，979×694 全尺寸）

| 帧 sha256 | 画面 | 出现于 |
|---|---|---|
| `b631f6f121450ec9` | 无卡：`Deferred req-1` 直发多行命令，提示符已返回 | prefix/001 variant-card、prefix/001R、prefix/002、**postfix/002** |
| `351ef257467d4c78` | 出卡：`! Approval req-1 · Bash · medium risk · > [ Allow once ]` | postfix/001 variant-card、postfix/001R |
| `f5b2481a1db58310` / `c1b72601d0dbff43` | 按 enter 后的回执帧（Blocked 面板） | prefix/001 receipt / postfix/001 receipt |

关键读法：修复前的"变体"帧与"精确键正控"帧**逐字节相同**——这正是缺陷本身
（用户无法从画面上区分"我信任过这条命令"和"有人拿近似拼写冒充"）。修复后
唯一移动的是变体，正控原地不动。

两帧已目视核验（非仅哈希）：
`prefix-fa8442c82/E01-PTY-001R/screenshots/suppressed.png`（无卡直发）与
`postfix-fed53bf2d/E01-PTY-001/screenshots/variant-card.png`（出卡询问）。

## 产物位置

`runs/<candidate>/<case-id>/`：`result.json`（runner 判读）、`transcript.cast`
（回放）、`transcript.ansi/.txt`、`events.jsonl`（证据点偏移）、
`screenshots/<point>.png`、`screens/<point>.webm`（layout_sensitive 点的全程
回放）、`visual-evidence-index.tsv`。

渲染走 `render-evidence.py`，内部调用 `cosh_lab.evidence.render_point_screenshots`
（`--renderer resvg` 保 box-drawing 边框、`--idle-time-limit 3600` 保原始时间轴），
偏移一律取 result.json 记录值，不重算。

## 环境降级（如实记录，不影响判据）

六格 transcript 首行均为
`cosh-shell audit degraded; command execution continues: audit writer is unavailable`。
裸 HOME 下 `AuditSegmentWriter::create` 在启动即失败（预置
`COSH_AUDIT_DIR` 与 0700 目录后依旧），因此接受卡片后落到 `Blocked req-1`
（`blocked_audit_required`）而非真执行。该降级发生在审批决策**之后**，
E01 的判据是"是否被询问"（卡片），在审计之前，故不受影响；但不得把本组证据
表述为"批准后真执行"。

## 勘误（相对 RUNBOOK-e01.md 初稿）

1. 初稿的 E01-PTY-001 用 `wait_for "Allow once"` + `wait_for "Approved"`。
   两处都错：`Approved` 文本不存在（降级环境下是 `Blocked req-1`）；且任何
   `wait_for` 超时会触发 runner 软失败→kill→**EPERM 丢全部产物**（见下）。
   现改为 `wait_quiet` + 无条件 enter + `wait_quiet` + exit，两侧都能干净退出。
2. 新增 E01-PTY-001R：runner 会丢弃"触发事件未发生"的证据点，所以"断言无卡"
   的案例必须用 `wait_quiet` 形式才能在 RED 侧产出截图。
3. runner 缺陷（已定位未修）：`cosh-shell-run-case` 的 `terminate_and_reap`
   只 rescue `ECHILD/ESRCH`。cosh-shell 在卡片停留期间不响应 SIGTERM，2 秒宽限
   后第 542 行 `Process.kill("KILL", -pid)` 对"组长已是僵尸"的进程组在 macOS
   返回 **EPERM**，异常逃逸、在 `transcript.*` 落盘前中止。违反该函数调用点
   第 745 行注释"软失败：不中断产物落盘"。本会话不改共享 runner（同机另有会话
   正在用 cosh-lab，同步内嵌副本会打断它），缺陷与一行级修法登记在记忆与
   report.md，待无并发会话时落地技能源。
