# #7489 history-only independent review

结论：阻断项0。已实读Git对象，新历史为4个逻辑commit；仅合并前两个互补修正，最后三个独立patch未变，最终源码零差。未push状态由主任务维护，本评审没有操作远端。

## Exact identity

工作树实际HEAD `c0658e0d8519c52b2ecb1cae5cc5662eef1362b7`，tree `0f29bc0fbe6d068dc99d53bb955b788bdbb05277`，base `b75eff716d8c42ba17b8355b47373430d25d2505`。旧HEAD60b的tree与新HEAD逐字相同；`git diff 60b68369eb0d573b0c9ba61106e04cab7ba56f0f HEAD` 输出为空。tracked clean，仅.cosh-lab未跟踪。

已读取mapping、range-diff和实际commit/tree/message/metadata对象，不仅依赖mapping宣称。未改source、refs、index或环境，未访问Root f81冻结树。

## Commit and tree preservation

| Old | New | Actual check |
| --- | --- | --- |
| d2964b8 + 4e5d79f | 7bea0cada3b0edc9da07921bcd88691c0761891b | 合并后的tree精确等于旧第二项4e5d79f结束tree；第一项旧中间tree不再作为独立节点保留，这是要求的squash。两段正文及两个Fixes均包含于新正文。 |
| 74e74e0b | b4d268c718e35dbe863aab2eeae49f09c456b3a6 | tree相等；parent→commit diff逐字相同；author/committer含日期时区及整条message逐字相同。 |
| 12eeef01 | 97ed670781795952560a653525ffc17e742b4521 | tree、patch、author/committer及整条message逐字相同。 |
| 60b68369 | c0658e0d8519c52b2ecb1cae5cc5662eef1362b7 | tree、patch、author/committer及整条message逐字相同。 |

新第一项author/committer原始metadata精确取旧d2964b8；没有虚称被折叠第二项的独立timestamp还能同时成为单个Git commit timestamp。旧两项Author/Commit身份信息、各自正文与Fixes归因未丢失；原Assisted-by/Signed-off-by均完整保留且去重后顺序正确。其余三项metadata保持原值。

range-diff准确表现第一项增加旧第二项fixture hunk与message段，旧第二项不再独立，余三项均`=`。实际patch/tree比较同样确认，未借range-diff相似度隐去产品差异。新第一项同时包含predicate+unit与同步fixture，使该互补修正作为一个逻辑commit评审；剩余idleprompt、exclusiveprobe、caret保持分立。

## Message rules

四条subject均英文、conventional cosh-ng scope/[shell]，长度分别43/41/43/46，均≤50，无句末句号。正文最大行长分别80/71/70/68，均≤100。首项保留 `Fixes: d4874256e235` 与 `Fixes: b3eebe231447` 两条原归因/subject；其余三项Fixes不变。Assisted-by在Signed-off-by之前，实际版本字符串/身份未改。没有新增version bump、lock、依赖或无关生产更改。

本次仅history hygiene，既有规则/行为/L3源码评审因tree一致仍适用，不重新证明运行或安全验收。旧60b测试/PTY/变异/CI证据身份应明确标作旧HEAD但相同tree，重写后远端CI和正式review状态须主任务新readback，不能把history整理当正式approval或发布授权。
