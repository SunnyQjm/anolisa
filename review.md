# #7608 staged fixture独立评审

未发现阻塞问题。findings_count=0；blocking_findings_count=0；人工L3 findings_count=0。

HEAD: 3d84c7001bf7e81351761e025b978812c8b70955

HEAD tree: 2567369c805dc16e5182bcc9eb07a6e54ea25ef0

Index tree: 67260901b1b874d3f2b1de7ac2091d6f9b7bf857

heavy.rs SHA256: 09f95fe0fd594baa6120eb97ce1ed8ba071c0f8605fe98e0980af132f969675d

核查：

- 仅Linux raw_cli input-wait fixture shell分支修改；不改产品控制协议、执行引擎或序列化。
- 六个字面谓词完整保留：behavior=host_executed_shell、exit_code=130、input_wait对象以detected=true开头、interrupted=true、reason=input-wait-timeout、status=timed_out。取消的是这些谓词之间的顺序耦合，不是值要求。
- for循环所有expected为单引号常量；case使用*"$expected"*按字面匹配，中途失败清空response并break。成功只在六次匹配全部通过且response非空时发出原assistant/result并exit0，否则原错误结果exit1。
- IFS= read -r仍按单行读取，未eval response、未引入动态shell代码/命令替换/外部依赖；无凭据、权限、破坏性动作或新文件操作。
- 从该测试let old_path起的全部后续正文与HEAD逐字节相同，保留handoff timeout30s、input-wait timeout1s、不得输入救援自动interrupt的输入序列及所有输出断言/cleanup。
- 既有raw_cli文件与测试分层匹配，无新增module/public API/依赖或production大文件增长。
- 03bc30b5b49de42947435b104615a93cfc67e2b3及5abfdd9930bed237c451cc162f518274dd3bf31a的heavy.rs与staged内容逐字节一致。
- 读取控制JSON确认candidate_fixed 2正控exit0、12负控exit1；两种sort_keys各对六字段逐一破坏，控制记录fixture_sha256等于staged heavy.rs完整文件SHA256。main原始失败/成功顺序对照未被覆盖。

局限：

- 本轮不构建、不执行shell控制或真实PTY动态测试；上述正负控是读取既有记录，不是本review新执行。
- 匹配器仍是原有compact JSON字面片段匹配，不验证完整JSON结构/重复键/类型/跨对象归属，也不承诺支持任意空白或input_wait内部字段顺序；这些为既有fixture边界，不把它描述为通用JSON语义parser。
- 字段分离后有意允许六个已要求片段之间顺序变化；未覆盖恶意构造重复字段/跨对象payload，本fixture由测试驱动产品输出，不是产品信任边界解析器。
- 未读取旧token或wire内容；只读取staged代码和指定合成控制摘要。
- 人工L3源码检查，非安全工具扫描；所查脚本目录未发现专用L3入口。
- 规则镜像未核实；使用现有适用AGENTS、pr-submit/behavior-review及已读组织规范，不宣称镜像一致。
- 本次未执行fmt/clippy/layout/inventory/PR-head preflight，提交与验收门禁由Root承担。

完整staged diff及源绑定见review.json。仅新增评审产物，不修改源码、资源或外部系统。
