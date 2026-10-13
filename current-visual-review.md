独立视觉复核结论：Go，限最终候选的两条canonical CI case及其八个证据点；模型端为loopback fixture，不扩称真实provider或RPM安装验收。

绑定HEAD `2e7fc1720511479c25374246b0ff50a38596aee4`、tree `da56e154adf7b3c953948580c84f49de62dbaed2`。正式RESIZE run `20261013T210121Z-962f7310`、FAULT run `20261013T210137Z-149480a9` 均实际exit0、failures为空，修正ownerRuntime标准evidence verify独立复跑均通过。

三份正常ELF SHA精确核对：

| 产物 | SHA256 |
| --- | --- |
| cosh-shell | 790f049fc20f863dbf8c37de0d393d456cac020d9d1f5adb22cfa8f6c7488b36 |
| cosh-core | 9c73f00310b66dea10302e101009edc6dfffa425fe36f3703c6f8d1b80cc2ee9 |
| cosh-ui-worker | cfe30b7de19165edd0883cd9f2aa1b9b993e8659f0a73d0c2bc7dac8c2127787 |

逐八点核对原cast SHA、SourceHead、point ID/时间、原始事件、resize geometry、PNG/WebM/provenance哈希。实际视频PTS与provenance精确一致；选择最后PTS≤point的帧，并按当前PNG尺寸裁切，八点逐RGB像素最大差均≤2，整体最大2。

已实际目检八张正式PNG和八张解码关键帧：CJK字形可读，卡底完整，resize后仅一张当前卡，Deny确实选中，普通Bashready可见。provenance logical_history保存完整左右sentinel夹住的16次CJK长行，screen_text的唯一完整卡、Deny与Bashready均通过独立断言。FAULT current与resized截图byte-identical，经哈希确认，内容完整。

两份精确sidecar `resize-102158`、`kill-frame-102494` 均正常三SHA一致，真实Host与outer观察80x30→47x20；effect1、requests2、Host result、稳定Bash、termios复原、remaining_pids为空。FAULT同一worker完整Allow→Deny→Allow三帧身份一致，三次不同worker实际Kill，全部日志段SHA重算通过。

owned环境cleaned状态从实际environment_ref的本地run独立readback，记录于review.json。本次只读取源码及正式产物，在新outputs目录保存review.py、review.json、report.md和八张解码关键帧；没有source/原artifacts/env/cargo修改，也没有覆盖旧候选复核证据。
