# PR #6892 P2 fallback增量独立复审

未发现阻塞问题。findings_count=0；blocking_findings_count=0。

HEAD: b811c9742c80ff781be34293d12f073a3a433d88

HEAD tree: e2866588aa9ea39fcf8a7e20c33eceed90fc9cf5

源文件绑定：

- src/cosh-ng/crates/cosh-shell/src/agent/intercept.rs: SHA256 d555355a1e76b2613d3854d3a4e7cef8f4e642b413a5dae49295a28853bf7293
- src/cosh-ng/crates/cosh-shell/src/agent/intercept_tests.rs: SHA256 b4867e9ebe17aa026a777a0edebbee90590bd7473f5978a48162aa7e6a207f38

核查：

- 新增调用层门控位于已处理事件 key 插入之后、compaction poll 之前；被消费事件不会进入 helper None -> generic fallback，也不会消费 pending question 或触发 compaction 恢复副作用。
- 消费条件精确要求 ai_disabled、pending Insight、有效 prompt_ghost marker，并匹配 suggestion id；legacy 无 id marker消费当前 Insight。AI-on、非匹配 id、natural_language 与 Health 不进入新门控。
- 匹配事件清空 pending_input_ghost_binding 并 continue；handled key 记账防同一 event 重放，既有 active run 和队列不由该分支停止、追加或清空。
- AI-on 正控验证 bound InsightPrompt 请求入队及原 command block/user_input；非匹配 ghost/natural_language 正控验证 Standard/FreeForm；Health 正控验证 StartupHealthFollowUp。
- idle 负控覆盖带 id 与 legacy 无 id，断言 active None、queue empty、output empty；busy 负控验证已有 run id、既有 queue id/route/index保持。
- 新增测试直接调用 render_intercept_agent_guidance，覆盖维护者指出的外层 fallback，较旧 helper-only 测试有效。测试均为无spawn private component tests，未新增依赖、public API、module或owner边界。
- 生产文件本轮从568增至583行，低于700/1000门槛；测试文件从696增至891行，production阈值不应用于独立测试文件。
- 人工L3：无新增 shell命令执行、动态参数拼接、凭据读取/日志、文件/权限/资源修改；门控收窄非用户新增请求，不放宽审批或执行权限。
- 共享作者分支按本轮明确约束禁止force/rewrite；正常followup commit保留他人历史。一般AGENTS同PR fixup规则与该明确要求有冲突，以本轮要求优先，需在PR/commit说明历史保留理由。

局限：

- 未重复运行构建、Rust tests、变异、fmt/clippy、preflight或真实provider。RED-READY.json来自原验收owner，本review只读取其2FAIL/3PASS与源码hash绑定，未复核其全部raw内容。
- FakeAdapter/component状态断言不是provider proof；不能宣称零真实HTTP请求或端到端真实模型验收。
- 未添加compaction活动/完成、pending question及事件重放的动态测试，本轮对这些路径结论来自门控位置和直接continue的静态检查。
- 非匹配ghost继续旧fallback，旧helper在AI-off情况下可清空未匹配pending Insight；本轮承诺保持其路由，不宣称修复所有陈旧ghost状态。
- 只消费本次匹配提交，不停止或清空已运行/已有排队请求；busy保持是预期合同。
- 工作树另有untracked .cosh-lab/验收产物，未读取/修改其内容；tracked dirty仅指定两文件。
- 未发现可定位的anolisa-auto-review/rules镜像，因此镜像与台账逐字节一致性未验证；适用AGENTS和仓库台账相对本review初始b811一致，JSON记录其hash。
- 未找到指定L3扫描脚本，执行的是人工源码L3 review，非工具扫描。

完整diff与规则hash见 fallback-review.json。人工L3 findings_count=0，不是工具扫描。仅新增评审产物，不改代码、环境或资源。
