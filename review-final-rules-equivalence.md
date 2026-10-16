# Final rebase rules equivalence review

结论：原 `review-r5-rules.md` 仍覆盖本候选；本次 rebase 等价规则增量核对未发现新增 P0/P1/P2。镜像 baseline drift 原样保留，无新增例外。

## 实际绑定

- Worktree：`/Users/quejianming/vscode/cosh-shell-dev/anolisa/.worktrees/cosh-7891-ui-worker-production`。
- 当前 HEAD / native base：`585d71fd3f6a95a9d3fb5fec50ab721fcf767306`。
- staged candidate tree：`cf23b75a2c151da8e85a16e44b3653422cbb4f7b`；index 与该 tree 无差异，worktree 无 unstaged 差异。
- Cosh subtree：`f1dbd5bd1cee77ee311a9a104aa539dcdd692afc`。
- 完整19文件 staged binary patch SHA256：`df0d825fc8494d008e78c1152dd42d4a95b4819f5c7a82db61e5a9ea4135020c`。
- 原规则报告 SHA256：`97755300e6cdbb1797702c44434c73af91ba73c862dfafa1cf9be777e3fb7f18`。

## 独立核对结果

1. 读取 `REBASE-585d-RECEIPT.json` 与 `CANDIDATE-TREE.json`，逐项用实际Git objects/index/worktree验证，而非只转述收据。
2. 19个文件的worktree、index、candidate blob内容SHA全部与CANDIDATE-TREE及原规则报告相符。原untracked设计文档现已staged；此状态变化没有改变内容或审查范围。
3. 旧base `2b4af68af60880790092011b96d204b33adb0c0b` → 旧candidate `ec6349fd690403b2e4003e846e3f8234daf1f6d0` 的完整patch，与当前staged完整patch逐字节一致。历史18文件patch f010be7b…不含当时untracked doc，最终应使用上述19文件 df0d825f…，两者不能混称。
4. 旧/新candidate整个 `src/cosh-ng` subtree object相同，因而其全部路径、mode和blob相同。进一步比较Shell `src/` 的 682 个Git tree entries逐项一致；682是本次另外枚举的Shell src子集计数，不冒称为收据1307项计数。收据1307 source逐项manifest未在本次重放，但整个Cosh subtree对象相同提供更广的仓库内容等价保证；不需要重复行为测试。
5. 旧base到新base及旧candidate到新candidate仅四个agentsight路径变化，没有Cosh owned文件、root/scoped AGENTS、specs或文档标准交集。
6. 原规则报告列出的全部规则输入文件SHA重新核对一致，包括实际评审镜像standard/review/decisions/large-file-inventory。D18–D21缺失、state1003/1000、osc987/805、镜像独有marker/bash934仍属预存drift；未改镜像。

上游四路径：

- `src/agentsight/src/analyzer/token/extractor/openai.rs`。
- `src/agentsight/src/analyzer/unified.rs`。
- `src/agentsight/src/health/checker.rs`。
- `src/agentsight/src/token_breakdown/cli.rs`。

## 范围与验证边界

原报告关于授权production wiring与用户批准局部persistentTTY修复、owner/dependency/root API、行数、测试分层、无依赖/lock/.env/新waiver的结论均沿用。本次只做内容/规则等价核对，不重新展开全review，不执行cargo、容器或验收环境。没有改源码/index/共享镜像；只新增本报告。该结论不代表真实TTY、installed-RPM/provider、merge或production Go，原报告保留的行为验收缺口没有因rebase被关闭。
