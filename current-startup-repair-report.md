# Startup 与 fresh-region repair 收口

修复以真实占区/部分写入来源决定是否需要 fresh-region repair，geometry_required 继续单独绑定几何。缺失或不可执行 worker 在 acquire/present 前失败，仅 inline fallback，不 CAN/全 viewport scrollout。已占区或故障 publication 后的 helper 与 direct panel retry 都先建立 fresh viewport，完整 publication 成功才清 repair；无 Pending 时成功 scroll/flush 清标志，下一张不重复 scroll。

新增 private session query 只读当前 rectangle 或当前 GateWrite error 的 accepted>0，不把 session 存在或旧 successful withdraw accepted 当占区来源。

有效 RED：startup-red.json（actual1，missing worker 的无 CAN 断言失败；首次 RED 未执行到0600第二分支）；repair-source-red.json（actual1，partial acquisition accepted=2/rect=None 漏判）；direct-retry-red.json（actual1，direct panel retry 缺失 CAN）。原 retry RED/GREEN 保存在本目录旧报告，未覆写。

GREEN：startup-repair-green.json，Rust1.97.1，实际144 passed/0 failed/0 ignored。同测试执行 missing 与 chmod0600 unexecutable 两个启动失败分支，正常 inline 卡片可见且无 CAN；present/direct 与 repaint/helper 故障重试均有 CAN32、39列几何绑定；noPending 完成后下一张无 CAN。session component 覆盖零接受/部分接受、TooTall、已 acquire 但未 live、successful withdraw 后旧计数反控。

这是私有 surface/publisher 组件与真实 worker 启动路径验证；透明 viewport/缓冲输出不是真实 PTY 或 Core/Bash 视觉验收。coordinator 未暴露 spawn errno，本报告不宣称已直接断言 ENOENT/EACCES。未重跑 full units/UI/canonical，待 Root 冻结后执行。完整命令、原 evidence hash、当前 dirty source hash 见 JSON。

质量链 startup-repair-quality.json 实际 exit0：cargo fmt --all -- --check、workspace all-targets Clippy -D warnings、test inventory、source layout、shell layout 全部 PASS。原 run20261013T204804Z-302b9639，在 set -e 下串行执行。source/env/cargo slot 已明确归还 Root，无运行 session，无 mutant；随后仅更新 outputs 报告，不再修改源码。
