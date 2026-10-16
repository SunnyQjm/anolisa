# #7489 history-only Linux preflight

结论：**必要 Linux preflight Go**。没有执行任何测试 body；不替代既有功能验收、newHEAD CI 或发布关口。

准确 HEAD `c0658e0d8519c52b2ecb1cae5cc5662eef1362b7`，base `b75eff716d8c42ba17b8355b47373430d25d2505`，实际范围4 commits。新旧 HEAD `60b68369eb0d573b0c9ba61106e04cab7ba56f0f` 的完整 tree 都精确为 `0f29bc0fbe6d068dc99d53bb955b788bdbb05277`。host before、guest before/after、host after 的1,294文件 manifest逐项一致，tracked WT clean，原有未跟踪 `.cosh-lab` 保留。私有 Git 快照/index只在 owned输出和 guest `/tmp`，未改真实 WT/common index。

独占 ALinux4 arm64容器 `cosh-7489-history-20261016`，profile声明2CPU/6G，ENV RUN `20261016T004839Z-9cd0060f`。guest实际 aarch64，Rust `1.97.1 (8bab26f4f 2026-07-14)`。只对原UI缓存的 cargo-home、rustup、target `4d276cc998ef5796e462` 做 `cp -cR` 到本任务cache；抽查源/副本inode不同，原settings/Rust ELF/target元数据关键文件hash before/after一致。没有硬链接再写；原cache只读seed，Root58/f81未写入、未挂载为本任务cache。owned Rustup `auto_self_update=disable`，显式1.97.1、禁自动安装，未安装工具链/依赖/宿主工具；rg用已有Linux ELF，经标准CLI上传。

实际 preflight run `20261016T005037Z-1a22f512`（固定 cosh-issue-fix bundled CLI）：

```
python3 -m cosh_lab pr preflight --base b75eff716 \
  --cargo-root src/cosh-ng \
  --gate crates/cosh-shell/scripts/check-layout.sh \
  --gate scripts/check-test-inventory.sh --output json
```

`GIT_DIR=/tmp/cosh-history-git`、`GIT_WORK_TREE=/work/repo`；`CARGO_TARGET_DIR=/cache/cargo-target/4d276cc998ef5796e462` 位于本任务独占cache。内层 `data.ok=true`：fmt、workspace/all-targets Clippy `-D warnings`、layout、inventory、upstream drift通过，4 commits的 commitlint findings=0，未改base/rebase。原生成功stdout/stderr也保留在 `evidence/cargo-native/`。

独立审计没有只信 inventory脚本exit0。实际7条Cargo命令（version、fmt、clippy和4条list）全部exit0。4条真实 `cargo test --locked -p ... --lib|--bin ... -- --list` 输出非空名称清单和完整summary：

| package | lib | bin | 独立计算 exact overlap |
| --- | ---: | ---: | ---: |
| cosh-core | 189 | 1100 | 4 |
| cosh-shell | 1625 | 3062 | 696 |

观察wrapper保持原argv/退出码，仅允许带`--list`的Cargo test并记录完整stdout/stderr；任何test body调用会被阻止。原生argv与清单逐项核对，没有test body。preflight的tests字段明确not-run。本次没有重跑621/0/1等功能套件，旧精确tree证据保持原历史口径，未改标为新运行。

首个host辅助wrapper启动将artifact-root放于`--`后，环境查找在guest执行前被拒；原始stderr保留 `preflight-launch-arg-error.stderr`。仅修owned脚本参数位置后运行上述唯一实际preflight，非源码失败/flake。没有修改源码、依赖、lock或.env。

末态 readback run `20261016T005505Z-0e8c6243`：guest manifest匹配，Cosh/cargo/rustc进程0。标准 `env down` run `20261016T005540Z-6b75da13` 返回cleaned；独立status run `20261016T005600Z-5b0f328c` 返回completed/cleaned、backend已不存在（exit1）。实际只读container inventory确认exact owned name present=false，原始JSON为 `container-inventory-after.json`。独占cache/evidence保留，不动Root容器。

宿主doctor contended=true（load约43/CloudShell），已记录；本次为隔离编译/固定静态关口，无性能耗时结论。plan因b75以来原产品改动与原未跟踪artifacts提示wider crate；按history-only显式范围仅执行必要preflight，不扩展test body。未运行focused/full/crate/workspace tests、PTY/canonical/provider、双架构、RPM/release或newHEAD CI；截图/WebM不适用于本预检。

结构化结果为 `result.json`，原生逐命令exit/清单/overlap审计为 `native-cargo-audit.json`，cache种子证明为 `cache-seed-proof.json` 和 `original-seed-hashes.json`。`evidence/`保留完整原生输出与guest绑定；`runs/`保留标准CLI run/commands/checksums。源码before/after与关键证据SHA见 `source-before.json`、`source-after.json`、`sha256sums.txt`。
