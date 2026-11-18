# Bash health banner independent review

Candidate: `9e092d16c4e10538747f429bf5d6454de012805c`.
Base: `f571226499ea08006f14b2eb9b63d2050aab9e2f`.

Three independent reviewers inspected the actual source and relevant owner contracts. The directions were runtime/lifecycle/security/performance, state/compatibility/selection, and code organization/test ownership/delivery rules. Repairs received follow-up review. The final reviewed source has no remaining verified P0/P1/P2 blocker. This is an internal static review result, not external approval or release qualification.

| Finding | Repair and formal regression |
| --- | --- |
| Cleanup reserve could consume a short command's effective work window | Reserve uses the effective budget; `command_cleanup_reserve_uses_the_effective_budget` and `a_clamped_short_check_keeps_a_command_work_window`. |
| Empty positive obligations could make the live acceptance matrix vacuously pass | Validate frozen sources, registered IDs, fault membership and a nonempty accessible non-fault set; nine `frozen_baseline_*` tests. |
| A cleanup test could leak its synthetic child when an assertion panicked | Retain the existing bounded child owner; `isolated_child_is_cleaned_up_when_assertion_panics`. |
| Later OOM reaper lines could change event identity, recency, count windows or latest-victim order | Use the definitive kill record for confirmed identity and occurrence time; parser tests and the actual candidate-to-GuideStore claim pipeline. |
| A bounded log window can retain only a reaper, or lose an OOM header | Preserve facts but require a confirmed event before reexposure; cover the real legacy journal filtering window, orphan-to-full enrichment and source/domain changes. |
| Event metadata could break old V2 readers or lose an old V2 writer's new entries | Keep an unchanged V2 mirror and separate V3 metadata; V2 is the complete entry set, with metadata attached only to exact matches. Cover old-writer preservation, stale metadata and V3 write failure. |
| Process names or cgroup text containing `Killed process` could forge a kill anchor | Parse the actual message prefix and numeric victim PID; cover comm/cgroup/diagnostic negatives and journal/dmesg caller-prefix positives. |

New event metadata is persisted only as digests and a bounded domain token. The existing private-state ownership, permission, symlink, byte and entry limits remain. No new dependency, lock-file edit, public production test hook or broad export was introduced. L3 source review found zero blocking findings.

The history contains four independently compiling existing-test fixes followed by one feature commit. Repairs introduced during this PR are folded into their originating feature commit. The four preceding commits were checked independently with Linux Rust 1.97.1, workspace/all-targets.

Historical v12 dual-architecture validation is recorded separately. Current-candidate native validation, sampling, installed terminal evidence and external CI must be read from the final validation summary; earlier focused passes and historical runs do not establish them.
