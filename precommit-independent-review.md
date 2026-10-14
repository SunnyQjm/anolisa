# #7545 提交前独立验收

结论：批准补丁 bytes 的提交前测试 Go；最终提交 HEAD 与清理尚待验收。

环境为独占 ALinux4 arm64 容器 `cosh-7545-shell-host-20261015`，ENV RUN_ID `20261014T201027Z-0e0298e5`，Rust 1.97.1。源为 `b75eff716d8c42ba17b8355b47373430d25d2505` 加批准 dirty `termios.rs`（SHA256 `8522f486157117ddae6d16d00dcc5b1f649de8731f067aac89b27feb8aa25f83`），不称为已提交 HEAD。

Bundled cosh-issue-fix preflight（run `20261014T201749Z-88ce7769`）的内层 `data.ok=true`：fmt、workspace/all-targets Clippy、layout、inventory、drift 均通过；该命令明确不覆盖 tests。四原路径 exact 分别 running 1 / 1 passed。完整 shell_host（run `20261014T202745Z-e63ec483`）原生命令含 `--test-threads=4`，running 220，219 passed / 0 failed / 1 ignored / 0 filtered。唯一 ignored 为原默认排除的 fullscreen TUI smoke，没有将其算为通过。

有效负控位于独立 `/tmp/cosh-7545-mutant-source`；未写 `/work/repo` bind，顺序复用本任务独占 target 的编译依赖。1,294 文件实际 manifest 与归档预期逐项一致。`oldchildren-oldtimer` 和 `oldchildren-newtimer` 都实际编译成功，测试 ELF SHA 分别为 `bb1dfe4467c5e5e97d1e2819fdc30c41f8d8bc0b8dcf0ca7ba9034af686f956f` 与 `7ca46792acdc20b030910c19a11e7d7f4feaf585ec6bae366ad4d8e777a6607b`。原两 case、2 线程、原 10 秒 held-lock driver 下，前者 0 passed / 2 failed，分别触发 child Bash 未发现与原 8 秒 timeout 断言；仅恢复 timer 的后者 1 passed / 1 failed，timeout 通过而 child discovery 仍失败。后者的原 thread-child exact running 1 / failed，明确触发 worker-thread child 未发现。没有增加测试 sleep 或放宽断言。

完整标准 CLI result、原 argv、stdout/stderr、源 manifest 和编译 ELF SHA 见 `dirty-four-exact-results.json`、`dirty-full-shell-host-result.json`、`compiled-controls-result.json` 与 `cache/cosh-7545-evidence/controls/`。初始化 Rust/tool/Git 失败原 run 均保留；它们为环境准备失败，不是产品测试失败。宿主 doctor 有竞争，本验证为独占环境的功能/固定断言验证，耗时不作为性能结论。

未运行 release、provider、双架构、完整 crate/workspace tests 或被默认忽略 fullscreen smoke。下一步仅最终准确提交 HEAD 的 preflight、四 exact、完整 shell_host 4 线程及 owned cleanup/readback。
