# #7545 independent precommit review

结论：源码/规则阻断项 **0**；单文件 diff 的 L3 安全阻断项 **0**，findings_count=0。规则镜像存在已核实的无关漂移，不能称全部一致。当前未提交补丁可评审，但组合树 GREEN 不等于这个独立候选已验收。

## Snapshot and scope

工作树 `/Users/quejianming/vscode/cosh-shell-dev/anolisa/.worktrees/cosh-7545-shell-host-fixture`，HEAD/base `b75eff716d8c42ba17b8355b47373430d25d2505`。唯一 tracked dirty 为 `src/cosh-ng/crates/cosh-shell/tests/shell_host/termios.rs`，16 additions/9 deletions，SHA256 `8522f486157117ddae6d16d00dcc5b1f649de8731f067aac89b27feb8aa25f83`。只读审查源码、指定历史归因/验收材料与规则镜像，不执行测试，不改代码/index/环境，不访问Root冻结树，不扫描任何凭据、token、旧安全事故材料。

## Itemized blocking assessment

| Item | Blocking | Evidence and boundary |
| --- | --- | --- |
| `/proc/stat` parsing | No | 使用 rsplit_once(") ") 取得最后一个comm终结分隔符，故comm含内部`) `不会截断PPid；尾字段state为0、PPid为1，nth(1)正确。只枚举/proc数字顶层条目，按实际PPid匹配wrapper TGID。 |
| Thread child ownership | No | 顶层/proc列进程TGID；线程spawn的child stat PPid为其父进程TGID，保持按wrapper/process id发现。既有 worker-thread child测试仍保留。指定focused evidence实际观察/proc/task/*/children缺失而stat父TGID匹配，不依赖CONFIG_CHECKPOINT_RESTORE。 |
| Process races | No | 遍历中消失/不可读条目继续跳过，失败仍由原有限deadline+10ms polling拒绝，不把一次snapshot空视作成功。没有引入全局进程kill；PID重用/可见性是既有Linux测试边界，补丁不声称加强它们。 |
| Lock and timer | No | 先取得现有shell_host_run_guard，再准备既有shell_host_test_config，随后started计时。等待其他测试锁不再误算产品8秒界；计时仍包含实际产品启动/退出。 |
| Reentrant deadlock | No | 锁内调用的是shell_run_scripted_bash产品alias，tests/shell_host.rs明确导入该alias；没有再次调用会获取同一mutex的fixture run_scripted_bash wrapper。产品scripted.rs本身不获取test lock。 |
| Original test contract | No | TimedOut、elapsed<8秒、真实descendant PID、最多20次50ms gone/zombie检查、最后失败SIGKILL与panic均逐字保留，未删断言/增超时。原5秒产品exit timeout未修改。 |
| Layout and growth | No | 测试仍在shell_host integration目标，非production/src；1083→1090行仅+7，不适用production>1000“新功能”禁令。没有新测试、属性或inventory变化，原220 baseline inventory边界保留，独立HEAD实际220仍需主任务执行核对。 |
| L3 safety | No | 只读/proc数字PID的stat，不读environ/密钥，不新增shell执行内容或外部传输。PPid选择只影响既有测试发现，signal/foreground cleanup断言不变；无审批/capture/auth权限修改、公共API/依赖/.env/lock变化。 |

## Rules and review mirror

已读取当前repo根/组件AGENTS、documentation-standard、independent-review-guide、repo decisions/large-file inventory、shell-test-organization heavy-test inventory，以及工作区cosh standard/review与现有 `/Users/quejianming/vscode/anolisa-auto-review/rules/cosh-ng-code-organization` 对应副本。镜像只读，未更新。镜像自身AGENTS的review-only规约仅作为其工作区背景，不把其中工具禁令扩成修改本task授权的规则。

当前b75仓内没有 standard.md/review.md 同名文件；标准位置实际为工作区 `/Users/quejianming/vscode/cosh-shell-dev/specs/cosh-ng-code-organization`。这两份与镜像逐字节一致。b75仓内现行decisions和inventory优先，镜像也分别用于审本补丁；差异不涉及本次termios fixture或220 inventory，没有适用条款冲突。具体身份如下：

| Rule | Current source SHA256 | Mirror SHA256 | Delta mirror→current |
| --- | --- | --- | --- |
| standard.md (workspace) | 80506e5e038cbccebf624a10a526d2ff0fb6f05095cfe09823f9a0f7f1844a76 | same | 0/0 |
| review.md (workspace) | 1717bf588e8a05cfe7b86e9890011c0e0289e67838b2c442cf161191b93837a1 | same | 0/0 |
| decisions.md (b75 repo) | 10e6e7b6af9dc8e29769809d4486920e2bc92a2825e5c0ab700b6b9edaea85ee | f696e7aa766748f4eedc3b68efa84c0d9e9c331d222752286a98c4d3145627ce | +84/-0; D18 sentinel/D19 path routing/D20 Gateway/D21 Task ownership |
| large-file-inventory.md (b75 repo) | 08db78a574d91585e8f3a861773e1b83f56ab6ddc9a9f9768fb214f44efa1659 | 27b0cf73e287fea216c21fbd8b1bce0565ce5b198a86496d97fbfa1d35b5c493 | +2/-3; state1000→1003、OSC805→987 owner说明、移除已拆marker/bash.rs生产记录 |

后三类production owner差异不指向tests/shell_host/termios.rs，也未改变测试分层或允许修改的文件scope，故是非阻断的镜像维护事实，不计入此test-only源码findings。不能把无关库存漂移当本补丁缺陷，也不能声称镜像完全同步。

## Attribution and validation limits

实际git show确认6e680c31cf14e05a19ff9583c81b299e9822c518引入按task/children枚举及其worker-thread控制；04b5d02b47f492fcf89596cfe1b1cb3b3b62a275引入该scripted timeout fixture与原8秒断言。给定归因与本次两处修正来源相符。

指定原始focused-results保留真实2 FAIL/218 filtered：child Bash未发现及elapsed<8断言失败，证据不是0匹配或构建失败。同组合树的修正GREEN只支持方案/行为，不借为b75独立branch的fresh build、focused、220/full shell_host或preflight结果。提交/PR前应在确切独立HEAD记录Rust1.97.1对应focused与恰当审计；本评审无执行结果，不宣布全部通过或发布Go。

## Exact committed-head binding

已独立读取 git rev-parse/show/stat/status：最终 HEAD `52745f8b3f5eb79ec75b70493f860417accf7a0e`，tree `6cb94baf9b89b28e7c79f0a300cdbe8037ee3d63`，提交 `test(cosh-ng): [shell] fix lifecycle fixtures`。唯一提交diff仍为termios.rs，16+/9-；status输出为空，源码实际SHA仍 `8522f486157117ddae6d16d00dcc5b1f649de8731f067aac89b27feb8aa25f83`，与此前评审逐字节相同，无新的算法或scope变化。因此此前提交前规则/行为/L3审查绑定至该精确HEAD仍有效，findings_count=0，无新增阻断项。

first restore的mutant cachemask失败保留，owned clean重编译后新test ELF269ae…与mutant bb1d/7ca4不同，不能把缓存失败删掉或当无效证据；compiled controls只证明相应夹具机制，不能替代finalHEAD完整验证。最终验证读取更新如下。

## Final execution and cleanup readback

实际读取 final-head-test-results.json 五项执行均exit0：四项exact各1 PASS，最终独立52745f8b的full shell_host **219 PASS / 0 FAIL / 1 ignored（220 total），206.01秒**。分别保持worker-thread发现、child signal/termios、wrapper lifecycle及scripted exit超时原行为；没有借组合树结果或旧mutant ELF为该独立HEAD认证。

实际读取 fresh S6 `runs/20261014T203632Z-341b4aef/result.json` 为ok=true；前后 final-host-source manifests实际均1294项且逐项相同，HEAD52745f8b、status为空。未修改Root是主任务的scope记录，本评审没有访问Root冻结树。

实际读取 final-cleanup-readback.json 与 final-container-inventory.json：owned `cosh-7545-shell-host-20261015` 不在独立真实inventory中，source_unchanged=true、host_clean=true。独占环境清理/source回读已完成，不再pending；未把其他container当本task残留或要求额外清理。

最终实际读取 pr-7551-watch-06.json 和 pr-ready-readback.json：PR #7551 HEAD52745f8b、OPEN、isDraft=false，已ready；27项check全部COMPLETED且SUCCESS/SKIPPED，无pending/failure，包含Test cosh-ng aggregate。正式review仍REVIEW_REQUIRED，请求zkl123，未merge。

pr-review-threads-ci-pending.json 是此前draft阶段、同一HEAD的线程readback：nodes为空、pageInfo.hasNextPage=false，因此该完整快照未解决线程为0；不把旧snapshot里的isDraft=true覆盖新的ready状态，也不把无线程等同正式approval。

源码及L3 findings_count仍0，exact本地focused/full/S6与CI支持测试夹具修正；无关规则镜像drift和首次cachemask失败保留。旧142779e资产快照也按主任务保留，最终immutable assets将另行发布。正式审批未批，此结果不是生产release/RPM或Root整体验收Go，不替代其他候选的未归因问题。评审者只读日志/manifest/源码身份并更新自有报告，未执行测试或环境修改。
