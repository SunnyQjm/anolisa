# S2 FAIL 基线 — issue #2597 调用透明合同

- Worktree: `anolisa/.worktrees/cosh-2597-invocation-transparency`
  （branch `fix/cosh-2597-invocation-transparency`，base_commit
  `2e7d69f1eb52cb08943853cfb39246a757e10e29`，`cosh-lab ws up` 创建于 2026-08-17）
- S1 摸底报告: `.cosh-lab/issue-2597/s1-audit-report.md`

## 基线等价豁免（isolation-baseline.md 条款，实测留证）

S1 复现证据 = 2026-08-14 直连集 65 原子案 paired 差分矩阵
（`artifacts/cosh-login-shell-full-execution-20260811/direct-terminal-run-20260814/`，
双架构 21 PASS / 44 FAIL / 0 BLOCKED，独立评审 GO）。

豁免判据实测：候选 RPM 构建时刻（artifact 时间戳 20260812T025033Z）
对应 main commit 与 worktree base_commit 在全部涉事路径 diff 为零：

```
$ git rev-list -1 --before="2026-08-12T02:50:33Z" origin/main
491d553cfbf960030dfbb25e475d6352263b5080
$ git diff --stat 491d553c 2e7d69f1 -- \
    src/cosh-ng/cosh-ng.spec.in \
    src/cosh-ng/crates/cosh-shell/src/runtime/startup.rs \
    src/cosh-ng/crates/cosh-shell/src/runtime/cli_args.rs \
    src/cosh-ng/crates/cosh-shell/src/main.rs
（空输出，exit 0 —— 零 diff）
```

辅助佐证：`git log --since=2026-08-01 origin/main -- <涉事路径>` 仅
`7c50a87b`（2026-08-03，noauth 启动提示，非分派逻辑）一条；spec.in
最后变更 `f650bd06`（2026-07-28）。

结论：**2026-08-14 矩阵直接充当本 worktree 的 FAIL 基线，免重跑。**

## FAIL 基线内容（验收对照锚点）

- 复现命令口径: `pty-ssh/paired_executor.py` + `pty-ssh/cases.json`
  （123 case 定义，直连集 65 case），oracle `/bin/bash` vs candidate
  `/usr/bin/cosh`，真实 ALinux4 ECS + RPM + strace。
- FAIL 集合（44/arch，双架构同构）: 见 S1 报告分组表（A 组 19 nonpty、
  B 组 16 pty+bash 旗标、C 组 8 pty+login 旗标、ABI-004 strace 链）。
- 每 case 证据: `direct-terminal-run-20260814/{x86_64,aarch64}/cases/<id>/compare.json`
  （status 字段 fail/pass）+ 各 cycle driver.log / evidence.tar.gz。
- SSH-004（#2545）: `ssh-formal-dualarch-20260813/v7-terminal/*/…/trace-correlation.json`
  candidate `exec_count:2` + script-interpreter-handoff。

## S5 验收对照口径（FAIL→PASS）

同一 harness（paired_executor + cases.json）、同一环境类型（ALinux4
ECS、双架构）、修复后 RPM：本合同覆盖 case 全部转 PASS，非目标 case
显式列出且不回退既有 21 PASS。本地开发迭代用容器
（`COSH_LAB_CONTAINER_RUNTIME=container`，Apple container 运行时，
不用 docker——用户 2026-08-17 明确口径）。

## 附注：base 存量测试失败（2026-08-17 实测，非本 diff 引入）

worktree base `2e7d69f1`（未打本修复 patch）在 macOS 宿主上
`cargo test -p cosh-shell` 即有 lib 5 / bin 7 个 hooks 相关失败
（hooks::engine external/project 执行类 + runtime::controller
hook_tests 两例）；打上修复 patch 后失败集合逐条恒等
（`diff` 为空，清单见 `2597-{bin,lib}-fail-base.txt`）。
归因：上游/环境存量问题，与 #2597 修复无关；PR 侧以 Linux CI
结果为准。

## 附注 2：全量语境串行对照（2026-08-17，macOS 宿主）

同机、无并行干扰、逐 target 串行（protocol/logic/raw_cli/shell_host/
cosh-core bin）：
- base `2e7d69f1`（旧代码+旧断言）：raw_cli 31 failed、protocol 2、
  shell_host 3、cosh-core bin 2（`serial-full-base.log`）。
- with-diff（本修复）：raw_cli 26 failed、其余逐条相同
  （`serial-full-withdiff.log`）。
- `comm -23 <withdiff> <base>` = 空：**with-diff 无任何 base 之外的
  新增失败**；base 失败含全部三个 passthrough 信号测试（旧实现同样
  失败），family 为 external_hook/failed_command/prompt_replay/
  session/heavy/mode/cancellation——macOS 宿主全量语境存量环境性
  失败，抖动集在两次运行间漂移。
- 过滤/单独运行时上述用例全绿（passthrough 26/26、shell_host 153、
  invocation 17/17）。权威判定以 Linux CI 与容器/真机为准。

## 容器验证结果（2026-08-18，alinux3 arm64，Apple container，RUN 20260817T065300Z-4df04e20）

- 测试 scope（cosh-lab test run）：
  - unit(--lib) 1312/2 failed —— 2 例 readonly_compound reaping，base 同容器
    逐一复现（存量容器环境性，无 init 的孤儿 reaping），非本 diff。
  - logic 9/9、protocol 71/71（macOS 上失败的 2 例 session_management 在
    Linux 过 → 佐证 mac 环境性）。
  - raw-cli 443/9 failed —— 9 例逐一 base 复现（含逐字节未动的 `--` 旧断言
    测试）：SIGINT/SIGQUIT 被后台作业链路置 SIG_IGN 的驱动环境效应 +
    heavy/cosh_core 超时族；本 diff 新增 5 测试（cosh_entry×4 + PS1）全绿。
  - shell-host 155/3 failed —— 3 例 base 同容器复现（存量）。
  - 未运行 scope：bin 单测（cosh-lab 无独立 scope；macOS 全量已跑且失败集
    与 base 恒等，Linux 全量由 CI 承接）。
- raw packaging gate（GNU tar + shellcheck + tests/test-package-raw.sh，
  含 launcher 薄 shim 重锚定断言）：PASS（`raw-packaging-gate.json`）。
- 探针 FAIL→PASS 对照（同容器、同 harness、RPM 布局 + su 登录链）：
  - base 完整现场（脚本 launcher + base 二进制）：**9/11 FAIL**
    （`probes-base-launcher.json`：B1/B2/B3/B4/B5/B7 TUI 劫持、
    B8 `$0=bash`、B9b SIGPIPE IGN 丢失、B10 PS1 被吞）；
    base 二进制 + symlink 布局的中间对照 4/11 FAIL（`probes-base.json`）。
  - 修复后：**11/11 PASS**（`probes-fixed-final.json`），并在重装后复验
    11/11（B6 bare TUI 与 B9a 为双侧 PASS 零回退锚点；B7 transcript
    `cosh-4.4#` 即 argv0 透传可视证据；B8 `-cosh`＝SC5；B9b＝SC4；
    B10＝SC6）。
