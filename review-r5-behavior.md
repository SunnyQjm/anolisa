# #7891 R5 behavior and L3 source review

## Result and source identity

未发现阻塞问题。当前完整补丁的新增 actionable `P0=0/P1=0/P2=0; findings_count=0`。这是一份只读源码审查，未执行 cargo/构建/环境/清理；不代表完整测试、合并或 release验收通过。

WT `/Users/quejianming/vscode/cosh-shell-dev/anolisa/.worktrees/cosh-7891-ui-worker-production`；实读 HEAD `fd31f09b29e3a9a9fb617c9e404a7fa81c2e39bb`，仍dirty。当前完整 tracked diff共18文件554+/66-，binary diff SHA-256 `f010be7b3827d43a3df038e5f911f469683e7ad1df774f9006b91a61d6935f42`。另明确审阅未跟踪 `src/cosh-ng/docs/design/approval-worker-production.md`，SHA-256 `b594d42b5fb4e1a06ca6acc9afe27ed92bd53b476d3d9c46d12aded87c50aab6`。

将这19文件逐项与 `local-linux/current-r5-source.json` 的 full_source_manifest比较：18 tracked文件全部hash相等；仅design文档不同，其新增段落明确显示lease、二次物理故障及provider终态后prompt重画。故不把这个HEAD本身称作已冻结的R5完整提交，也不把旧文档hash当本报告身份。

审查沿 requesting-code-review / cosh-issue-fix reference/behavior-review 完整清单，读取完整diff及相邻调用者/状态/测试；组织规则由独立规则owner复核，本报告不代其作Go。仅访问本WT源码及指定非敏感验收产物，未扫描凭据、.env或旧安全事故文件。

## Production activation / trusted worker

`runtime/approval_ui.rs::for_current_process`的debug分支保留原from_lookup；release分支只从actual current_exe取得安装位置。test activation/key/worker-path/解析辅助函数仍cfg(debug_assertions)，没有release读取COSH_UI_TEST_*、COSH_UI_WORKER_PATH或parent-only COSH_ACCEPT_RELEASE_PROFILE的路径。production_ignores_debug_worker_path_injection故意保留invalid debug env作为release负控，不能因该case env非空就误认为产品读入了它。

Linux factory要求绝对Shell路径并canonicalize，以Shell实际文件uid为安装owner；worker必须同目录常规文件且非symlink、同uid、非set-id/非groupother writable、有执行位。祖先链以symlink_metadata核目录类型、root或同owner、非groupother writable。relative/missing/nonexec/writable/symlink/ancestor不可信均返回None保inline；非Linux亦保inline。没有PATH/current-directory/用户指定worker覆盖，也没有向上搜索任意worker。

该信任是安装owner边界，不是抵抗trusted owner替换安装文件的防篡改机制；按路径spawn也没有新增原子open+exec/hash-pinning承诺。没有发现本次diff引入的非owner写入绕过。此报告不将同uid worker描述为恶意代码sandbox，后代IPC等仍属broaderU02证据需求。

`controller/bootstrap.rs`保留file sink admission和actual current_exe sibling二次核对；失败只保inline。`logging.rs`仅移除ready static、reader、成功subscriber.init后store三处debug cfg。三个stderr fallback仍ready=false，不因一次无法写文件却激活worker；原预算/锁/权限/抑制IO语义没有改。

RPM `%install`与`%files`精确新增同libexec路径worker，既有release build产物复用；测试脚本增加结构锚点。结构通过不能替代实际两架构RPM安装/ELF身份或provider验收。

## Fixed bounds, geometry, eligibility and authority

production policy固定40列、24最大surface rows、1MiB payload/4096 drawops/16KiB text、5s handshake/render/backpressure、100ms heartbeat、3s heartbeat deadline、2s shutdown、3次failure、单pending revision。heartbeat已从R1有证据不适配1s relay tick的1s修至3s；原debug解析/真实fixture policy未被放宽来伪造修复。12s同workerPID idle正控是新增测试，结果不由源码推断。

既有Gate按physical viewport至少40列/足够行判断，worker surface仍40，不拿虚拟COSH_SHELL_WIDTH扩大真实几何。resize使claim失信；原fresh-input/invalid-generation/inline退化路径仍保留；failure budget沿原coordinator计数和terminate/reap，耗尽不会无界重建。没有新增CPR、shared slot或第二terminal writer。

唯一eligibility变化是注释；实际sole pending、Tool shell alias、provider ControlPermission、ids、active-run owner、HostResult capability、foreground handoff分类、标准高风险三动作、higher-priority capture ladder都未变。Bash指既有provider shell-tool predicate；该predicate不是raw ShellKind检查，release run_raw也不是新增raw Bash专用gate。未发现本diff默默扩大审批类型，但不能把真实Bash matrix通过写成所有raw Zsh/native形态已认证。

worker仍通过既有WorkerProcess：empty env、cwd `/`、setsid、null stdfds，仅IPC fd3；Host持有approval/input/audit/effect权威。projection无provider approval回调和执行权限；actual PTY emit仍要严格staging/register/origin与approved token。新pending位仅延长显示恢复lease，不能创建approval、重发命令或额外交付HostResult。

## Persistent display / R5 ownership and concurrency

`controller.rs:65–124`优先读取当前token真实完成事实、建ledger、交付结算；Running/pending维持Hold和既有bounded timeout/interrupt。tagged物理失败置唯一display_prompt_restore_pending，recover成功只清physicalfailed；settled+pending+healthy强制Restore位于新Emit/Capture及旧token退休之前。无损pending=false保原流程。

`observer.rs`持mode锁完成action映射后强制failed||pending→Hold；显示后更新亦同。raw prompt为空不清lease/债务，也不开放输入。`pty_emit.rs::RestorePrompt`的初末flush及所有物理写均通过PhysicalDisplayWriter；只有tagged+boundtoken可defer，parser/storage/PTY/staging错误仍严格传播。真实末flush成功才endlease，返回一次Hold让下一observer决定真实owner，不在恢复过程中抢跑Passthrough/旧ghost。merge在Hold可丢raw pending action，但共享pending位使controller每次健康settled pass重新发noneghost Restore；债务不依赖该临时payload存活。

R5受损forcedRestore分支设置 needs_prompt_after_run=true/native_prompt_after_run=false；它纠正了提前消费native prompt之后，provider终态CRLF仍用旧native-present优化抑制重画的问题。needs可由真实marker cwd设为false，故两字段缺一不可。这是显示意向，不是执行权限；写失败时pending/Hold仍阻止dispatch和输入，成功后既有render_owned_shell_prompt/trigger在provider终态后重画。未修改正常无损的prompt/ghost owner逻辑。

完成marker先于PS1时，OscParser precmd在生成completion前清空旧last_prompt_display，post-hook prompt_ready亦开始新capture；不会据旧cwd缓存直接退休。任意字节分片/ANSI半序列仍由原parser/replay处理，新产品代码没有新增字节流解析。既有has_prompt_painted_since_ready只说明ready后有display bytes，不能证明完整自定义PS1；动态cwd/ANSI分片仍需真实PTY验证，不能用非空代替currentcursorline。

新增pending的正常排空是末flush成功；失败重试不递增执行次数；Running超时沿原不确定/interrupt路径，不伪造成功。真实Bash退出/PTY传输失败仍走原退出严格路径，无法恢复已退出的Shell；EOF/退出没有被改成无界fake-success循环。模式/新capture在pending时受Hold和早返回阻止，恢复后交原owner重新决策。

## Tests, oracles and diagnostics

完整读取approval_ui unit新增边界、raw approval新增missingworker/3kill+3hang budget/12s idle/debug injection、真实output refault和两support文件及canonical脚本增量。原19默认debug用例保留；parent-only release profile选实际release Shell/Core/worker，child显式去parent变量；正常production launch去UI env，debug注入负控显式例外以测试忽略。HOME下私有profile适配祖先信任，既有TempDir/进程Drop清理继续适用，未新增依赖/lock/.env变更。

实际worker身份验证检查/proc exe/ELF hash、PPid/PGid/SID、cwd、env及fd；stat使用rsplit_once处理comm，不能拿malformed Python worker当真实ELF身份。missingworker仍要求实际Host approval/effect而非仅“没看到进程”。新interposer的第二故障须记录命中，原无输入PS1当前行/列/绿色/caret、effect=1/HostResult=1/sameBash、ordinary/第二request及forbidden input断言都保留。新增失败消息仅提供row/col/screen/fault/transcript，不换断言为历史substring、不增timeout或sleep。interposer新增匹配状态跨write保存；它是专门fixture标记，不是新的产品prompt parser。

已独立读取 `local-linux/r5-production-prompt-refault.json`：run `20261016T102516Z-af9e0160`，exit0、1 passed/626 filtered、test3.49s；其18 tracked源码与本次清单全相等。仅可称这个实际release refault用例首次GREEN，不能称完整矩阵/完整gate已绿；我没有重跑，也不独立view本轮cast/PNG。历史R4 `101931Z-f2ef4a15` exit101/空caret行仍保存在u02 audit，不抹除或重标为通过。

## Historical findings and acceptance limits

R1 heartbeat P1保留在review-r1.md；源码已改3s，仍应保有效compiled1s回退控制与实际idle证据。先前CPR怀疑明确撤回，未要求无依据产品变动。R4 nativeprompt/caret P1保留在u02-persistent-tty-audit.md；R5源码纠正和首个真实GREEN是后续证据，不把历史失败改写成成功或宣布所有动态关口关闭。

broader U02继续OPEN：U02a需真实旧generation/descendant IPC到Host consumer拒绝witness，kill/hang/malformed不等价；U02b需真实Running/Unknown/失marker及bounded行为witness，不能用effect=1的普通完成case泛替代；U02c需公开显式takeback与真实input consumer证据，局部write恢复/既有timeout并未新建该接口。本批准方案只沿既有bounded handoff/timeout，不要求再走G1，也不擅扩新协议。

最终仍需Root冻结exact commit/tree、双架构release RPM及六payload/contract/observer身份、installed real-provider/no-input prompt证据、有效编译变异、其余回归/完整gate、正式review/清理。当前未核这些终态，不把old v7/debug/首次focused GREEN升级为release Go。


## Final rebase equivalence binding — base 585d71fd

本轮只做等价增量审查，未重新执行测试或重评无变化算法；新增behavior/L3 findings_count=0。前述完整行为/L3结论继续覆盖最终candidate，broader U02a/b/c继续OPEN，未升级最终验收。

实读REBASE-585d-RECEIPT.json、CANDIDATE-TREE.json及Git对象，结果：

- 当前HEAD/base `585d71fd3f6a95a9d3fb5fec50ab721fcf767306`；staged candidate tree `cf23b75a2c151da8e85a16e44b3653422cbb4f7b`；Cosh subtree `f1dbd5bd1cee77ee311a9a104aa539dcdd692afc`。
- 完整19文件cached binary patch实算SHA-256 `df0d825fc8494d008e78c1152dd42d4a95b4819f5c7a82db61e5a9ea4135020c`。历史f010be7b…仅是design尚未stage前18tracked文件口径，不能代替当前19文件patch。
- 对19路径逐一读取旧candidate `ec6349fd690403b2e4003e846e3f8234daf1f6d0`、新candidate tree与当前WT内容，SHA全部等于CANDIDATE-TREE所列值；design仍b594d42b…，R5 controller仍0056f713…，support仍462c80a2…。无unstaged diff。
- 旧/新candidate Cosh subtree完全相等；旧base `2b4af68af60880790092011b96d204b33adb0c0b`→新base及旧tree→新tree的实际diff均仅四个Agentsight路径：token/extractor/openai.rs、analyzer/unified.rs、health/checker.rs、token_breakdown/cli.rs。没有Cosh产品/规则/本次owned路径交集，不引入新的approval、capture、lease或release-trust变化。
- receipt的1307 source hashes unchanged声明与实际整个Cosh tree相等相符；本轮未再读取/运行guest环境，不将receipt当新的执行验收。

旧验证run保留原base2b4/oldcandidate ec身份；rebase等价证明是源码关联证据，不把旧run重标为585d精确执行。最终preflight由其owner运行，未在此预宣称通过；正式commit/review/CI、broaderU02和installedRPM/provider接受边界保持原限定。

操作透明说明：本轮开始为取得staged tree曾误用一次git write-tree（返回上述已有candidate），未执行add/reset或源码/ref修改；该命令不符合纯读取命令约束，已向主任务说明，后续验证使用现有Git对象与diff/show读取。不以此宣称未触及Git内部缓存，也未回滚他人的index。
