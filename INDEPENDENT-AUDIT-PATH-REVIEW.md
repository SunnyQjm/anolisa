# PR #6808 audit PATH 独立评审

无阻断意见。findings_count=0；blocking_findings_count=0。

HEAD: 058e145ea161f61760dbdf8be77c36d3db411cdd

源绑定：

- src/cosh-ng/crates/cosh-shell/src/slash/audit.rs: f77c2146c92d5d732151000316f11657e75e331db7afb1c8e656446315c520c6
- src/cosh-ng/crates/cosh-shell/tests/raw_cli/native.rs: f5a92750be93fcd7a7385790e1b94ef35536ba3e7b308b72f6c2e87c0aa2eb9a

核查：

- 三个/audit status/trace/export入口经render_audit_command -> resolve_arguments -> audit_program -> run_audit_cli -> run_audit_cli_with_timeout，统一替换一个Command构造点，不漏并行分支。
- 新构造器仍Command::new(program)，仅在OnceLock已有可信startup PATH时对单个child设置PATH；未修改全局环境，未重新source profile，未启动shell解析audit参数。与mcp及compact使用相同入口。
- 可信来源为managed Bash login startup observer；OSC handle_marker先校token/session，StartupEnvironmentGate只接受首prompt前首个有效report；PATH限8KiB/无控制字符、去relative/empty entries并去重，缺失/被禁用时保持继承PATH。
- COSH_CLI_BIN仍由audit_program优先选择，helper不改变program值；绝对路径继续直接执行，相对裸命令按可信child PATH查找。覆盖的是路径解析，不是审批/身份提权。
- args(arguments)、stdin null、stdout pipe、stderr null、3s deadline、256KiB上限、process_group(0)、timeout killpg/wait及output redaction全部未变；含空格destination保持单个Vec参数，不引入命令注入。
- 新真实PTY测试将父PATH固定/usr/bin:/bin并unset COSH_CLI_BIN，cosh-cli stand-in仅在login profile追加目录；调用3次、各自PATH前缀、profile-hits=1可判别旧ENOENT与新可执行路径。fixture RAII Drop清理自有home。
- fixture从真实Bash login/raw shell调用/audit，适合既有raw_cli/native层；不使用fake PATH注入为产品结果，CLI stand-in仅限定PATH/入口合同。无新依赖、公开API、module或production大文件增长。
- 读取GREEN-FOCUSED-RECEIPT确认目标1/1与10个startupPATH控制各1/1，source hashes与当前两文件一致；本review不重新执行。
- latestmain3a245从共同祖先到该main在audit.rs/launch_path.rs/native.rs无交集增量；最终rebase/fold后的exact diff仍需复核。

局限：

- 仅当前HEAD1a8fc942加dirty两文件的增量审查；未运行Cargo、容器、网络、真实provider或RPM验收。
- 测试stand-in记录$*会丢失argv分隔，且trace/export用starts_with，不能独立证明空格path为单argv或session identity精确；现有resolve_arguments单测与未改Command::args静态链路支持此边界，未作为新增阻断。
- 新PTY测试未在同一profile场景另测显式COSH_CLI_BIN覆盖；原audit fixtures设显式路径且helper保持program原值，本次不声称新增该动态正控。
- 可信PATH表示用户管理shell的启动PATH，不表示其中目录为root-owned；该补丁复用现有同用户执行边界，不提供更高权限安全认证。
- 本轮仅人工安全检查，无工具扫描；规则镜像一致性未核实。
- 源focused GREEN不能升级为真实provider、RPM、默认登录或release通过；后续同步main/fold后须新HEAD门禁。

完整diff及hash见JSON。本轮仅写评审产物。

## 最终提交增量复评

无新增阻断。HEAD 5632512832600f5efef47f658d7e015ec732e48a，tree 099224aa3d762306d613e87005959d7dae79277a。

- 最终HEAD单commit以latestmain3a245为父，clean。最终相对fold前HEAD058e的完整diff与初审dirty两文件patch逐字节相同。
- 058e干净commit tree不是受测dirty源码tree，二者不能直接等同；FINAL-COMMIT-BINDING记录受测dirty tree保留，且本review独立验证最终内容=058e+原已审patch、受测三文件hash全部一致。
- 原两提交作者SunnyQjm保留，最终AuthorDate保留初始fix时间；Qoder/Codex Assisted-by和Signed-off-by保留。
- Fixes指向base main已有祖先3b2bd186，非intraPR提交；原两提交和P2 fold成一个原子修复，符合§13。
- 同字节test编译变异raw receipt SHA核对成功：退回旧Command构造编译成功1FAIL，恢复后编译成功1PASS。
- 读取最终记录：新PTY1/1、audit status/export各1/1、audit bin unit6/6；source preflight成功，不等同全workspace测试。

- 增量历史与source绑定复审，无重新Rust、容器、正式scanner、provider或RPM验收。
- 未重新全面审查原PR42文件；本次无额外新源码的结论通过058e+已审patch精确比对成立。
- 新HEAD CI、approval及未解决threads仍须核查，COMMENTED不等于APPROVED。
- 初审argv/显式override动态测试盲点及规则镜像未核实限制保留。
