阶段：本轮必要修复、最终验证与清理已完成；PR保持草稿，发布/合入仍No-Go。

PR https://github.com/agentic-os-org/ANOLISA/pull/7489
HEAD 60b68369eb0d573b0c9ba61106e04cab7ba56f0f
Tree 0f29bc0fbe6d068dc99d53bb955b788bdbb05277
Base b75eff716d8c42ba17b8355b47373430d25d2505
Cosh subtree6a25f82f406beb0ce72af9c6f38a63dc44a43e97
10文件、5提交；追踪源码干净，1188个Rust/Cargo文件前后均匹配。原始gitstatus仍有自有.cosh-lab运行元数据未跟踪，未修改公共Git忽略配置或删除其他会话记录。

最终Rust1.97.1/ALinux4 arm64/自有2CPU6GiB环境：四线程raw_cli621PASS/0FAIL/1ignored，共622项、709.66秒、exit0。准确HEAD preflight内层data.ok=true：fmt/workspace all-targets Clippy/layout/inventory/commit lint/无upstream drift。准确HEAD controller11与真实Core+Bash+PTY故障3项focused全部通过。Final-source full日志与精准binding独立保存，不借旧631/621结果。

逐项处置：
1. 原auth request2等待期间却出现同token未来3/4，单writer不能产生。等壁钟驱动的旧目录构造与原auth用例已编译复现future4；排他TempDir修复请求身份/生命周期。原事故的具体clock调用没有保留，等时来源仍为基于别名signature与实验机制的推断。
2. 原超时PS1空行，在3故障并发第二轮再现。原始字节证明原绿色PS1之后又输出延迟timeoutnotice；idle notice原返回None，新增既有RestorePrompt动作恢复原生提示符。
3. 前一版12ee完整621/0/1通过，但原PTY字节显示Gate撤销故障后的caret仍隐藏。强化原before-input !hide_cursor断言得到实际2/1 RED；物理恢复仅补DECSET25h，同组件与真实3故障GREEN，删25h编译变异101。

最终3个原始PTY记录与补充tmux回放均证明：在下次输入前owner@host:~$、绿色Idx2、目录~展开、row31/col14与visible caret恢复；原Bash/job/cwd保留，effect正常1或timeout0、HostResult1、approval1，禁止输入不泄漏。PNG仅为原始字节的补充回放，时间合成，原始offset/geometry/二进制hash/源码绑定均保留。

旧e315 full618/2/1，旧12ee full621/0/1（未检查caret）、混杂whole-process clock positive101、所有有效RED/编译变异及诊断均保留，未弱化断言/增加sleep或timeout/删除用例/增加依赖/改.env或lock/引入CPR或shared slot。

当前60b CI全部SUCCESS，正式reviewRequired，独立静态评审无源码阻断。旧12eeCI Platform peer-helper spawnETXTBSY日志保留，其源blob463d7f7360e1ae4a917a26e3776b2f99ad9b5868在base/head一致；没有据当前CI通过标flaky或宣称旧根因消失，也未修改Platform。

历史recommendation request4仍按已知边界保留为未归因，不借本次full通过关闭。PR7489仍draft/issue7484仍open；无merge/release/deploy/采购。完整workspace/real-provider/双架构installed-RPM及产品发布验收不属于本轮。

自有容器codex-raw-cli-main-20261015、run853b65b0已清理，独立container inventory确认不存在；Root容器和target未操作，共享cache保留。私有回放tmux随脚本finally清理。
