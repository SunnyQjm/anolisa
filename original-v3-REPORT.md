# v3 shell_host 隔离诊断

结论：四项首败支持两项测试 fixture 原因。前三项共用不可用的 proc children 接口；第四项把全局 fixture 锁等待计入8秒产品超时断言。没有据此确认产品进程回收/termios缺陷。原全workspace仍exit101/No-Go；私有修复提案未应用、未编译，不能称四项已修复。

精确源码9259918118e9577edb23e1e426294f0cb26ef611；termios.rs SHA=d82aa6ebad29cb4f16d77d5fb5d3a425923bf1d5fa4f0d8cb7986f911c1b7abc，guest实读前后相同。原首败结果路径与SHA/命令在source-identity.json，完整stdout/stderr保留。本轮不覆盖原始JSON。Rust原二进制shell_host-1a7ad722502e9928，SHA=0d86d6240773abc1dab31775314b47a04c9f114b104b1280d467e99fb5910206，前后未变；来自Root原1.97.1 workspace构建，220 case inventory。未重新编译或写缓存。

## 环境与 /proc 断点

Root授权container RUN=20261013T131137Z-a28e769c；所有环境/传输操作通过 .agents/skills/cosh-test-debug-accept/scripts/cosh-lab CLI 0.8，artifact-root使用真实环境元数据位置 /Users/quejianming/vscode/cosh-shell-dev/anolisa/.worktrees/cosh-6770-scheme-a/.cosh-lab/runs。工具输出在本目录，实际CLI原生命令在*.command.json；本轮没有采购或env up/down。

Linux6.18.15/aarch64，UID0。Rootrunner只把cosh_core-*切为UID65534，shell_host保持UID0，见runner-readback.json。proc mount rw/relatime且没有hidepid；父子PID namespace均pid:[4026532180]。不是缺权限或跨PID namespace。

实际kernel /proc/config.gz：CONFIG_PROC_CHILDREN和CONFIG_CHECKPOINT_RESTORE均未启用。现代children文件由PROC_CHILDREN决定（不要仅凭CHECKPOINT_RESTORE归因）。主线程与worker线程的children读取均ENOENT2；worker真实sleep子进程stat PPid等于父进程TGID，同namespace，保持存活时stat正控可发现，children负控永远空。kernel-and-cleanup.json与focused-results.json为原始证据。接口说明可核 [Linux man-pages primary source](https://kernel.googlesource.com/pub/scm/docs/man-pages/man-pages/%2B/refs/tags/man-pages-6.11/man/man5/proc_tid_children.5)：该接口还可能在未freeze子进程时漏项。

精确fixture direct_children读/proc/<pid>/task全部tid的children，把ENOENT静默continue，于是始终返回空；三个consumer分别在termios.rs576/277失败。真实wrapper已启用raw mode不等于Bash不存在。

## 必要有界复现与正负控

| 原二进制 scope | 实际结果 | 可确认内容 |
| --- | --- | --- |
| direct_children_scans_every_wrapper_thread，exact/1线程 | 0pass/1fail，10.01s，exit101 | 原fixture稳定读不到存在的worker child；首败未被复跑成功覆盖 |
| scripted_shell_exit_timeout_kills_foreground_group，exact/1线程 | 1/1pass，5.39s，exit0 | 原8秒约束在不等待fixture锁时通过；包含原终止检查 |
| raw_cli_restores_parent_termios_after_child_shell_signal + scripted timeout，原二进制2线程，仅2case | 0pass/2fail，15.46s，exit101 | child_shell探测持锁失败约10s；timeout计时先于锁，锁等待+约5.4s产品退出导致8秒断言失败 |
| Python真实PTY产品正控，同缓存cosh-shell raw fake --shell bash | stat发现Bash393250，children文件缺失；Bash SIGHUP后wrapper exit0，termios+flags完全恢复，Bashgone | 该信号场景的产品恢复/回收有效；不是provider证据或原Rust修复通过 |

scope命令完整记录于focused-results.json：Root既有runner + 原cachedbinary + exact filter或原termios过滤/逐项skip + --test-threads=1/2，未运行Cargo。每个子命令25秒硬界，首个worker机制也有限等待并kill/wait。未加测试sleep、重试spawn、加大8秒、删case或整体串行套件；两线程组合主动构造原fixture锁相互作用，不能归为宿主负载或flaky。

test helper全局锁在tests/shell_host.rs154；原timeout计时在termios.rs685，调用run_scripted_bash后才入锁。产品SCRIPTED_SHELL_EXIT_TIMEOUT=5秒（scripted.rs14）；io_loop.rs120后超时杀PTY foreground及shell process group并wait。源码链+原串行/组合对照定位的是计时边界。未直接记录原首次全套锁等待的时间戳，因此原首次第四项的因果链由同二进制有效组合复现与精确代码支持，不伪造原首次锁trace。

未单独重跑foreground_group_signal：它同样依赖已证明为空的helper；仍需Root实施后实际跑此case，不能用SIGHUP正控代替它。

## 最小 test-only 提案

[test-only-proposal.patch](test-only-proposal.patch)只改tests/shell_host/termios.rs，16 additions/9 deletions：

1. direct_children枚举/proc数字PID，按stat最后一个") "后的PPid过滤，覆盖其他父线程创建的子进程；BTreeSet排序和现有断言保留。不要求更换内核/包/依赖，也不改产品进程枚举。
2. timeout测试先获得既有shell_host_run_guard，原shell_host_test_config准备后再开始计时；直接调用已有shell_run_scripted_bash产品别名，避免重复获取非重入锁。原8秒、TimedOut和descendant终止断言逐字不变。只排除无关fixture排队，不扩大产品时限。

独立review无阻塞发现，确认PPid解析/其他线程覆盖、无二次锁死锁和证据边界。git apply --numstat校验patch语法；没有实际应用、rustfmt/cargo或产品源码写入。Root负责在私有实现树应用并取得新源码身份，需要：四项exact各1匹配（零匹配不是通过）+ 新shell_host --test-threads=4（220 total / 已有ignored保留），随后按原workspace门禁验证；失败与串行对照记录保留。不能以原timeout串行绿升级原workspace绿，8h仍暂不启动。

## 清理与未运行 scope

worker392902/392907已kill+wait；pair超时descendant393168已gone；真实PTYwrapper393242/Bash393250已gone。pair首败留下本次fixture /tmp/cosh-scripted-exit-timeout-393016-1792006348148701293，按精确descendant.pid绑定且确认进程gone后移除。两上传probe.py已移除，PTY临时HOME已移除；final-readback.json确认这些PID/本次parent-fixture cwd无残留、脚本0，kernel-and-cleanup.json确认fixture root0。没有碰原Root失败的历史目录。Root共用container保持运行，不把它env down，资源采购数0。

未执行补丁后Rust、完整shell_host、workspace、RPM安装、VM、provider、截图/WebM、8h或aggregate gate。本轮只有诊断与一个PTY信号正控，无UI验收截图索引。release仍No-Go，下一门禁是Root实际应用和同新源码完整测试。
