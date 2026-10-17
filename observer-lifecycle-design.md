# Unified consumer lifecycle design — review before implementation

Status: DESIGN_REVIEW_PENDING. Baseline clean tool 411bf26, product/RPM/source
84db0a6 unchanged. No implementation or product replay authorized by this file.
Root requested this design after two consumer-domain failures: external-session
ENOTTY in e5f34a7 and normal Bash exit racing a cached descendant row in 411bf26.
Both immutable failure runs remain FAIL, including incomplete media and monitor.

## Contract and alternatives

The observer samples evidence; it does not own or acquire the target terminal.
It never sends input, changes termios, adopts a session, or signals a target.
Recommended: bounded strict procfs observation with explicit termination proof.
Rejected: catch-all None (hides invalid evidence); stopping monitoring after
exit-ready (loses late activity); keeping all disappearance errors (normal exit
is falsely failed). No timeout, canonical input or aggregate threshold changes.

Three outcomes only:

1. LIVE_VALID: same PID/start/session/process-group/controlling-tty before and
   after observation, fd0 is a character device matching tty_nr, stable fd0
   device and path, actual kernel tpgid. Return actual consumer sample. A
   background process returns its actual unequal tpgid/pgrp; cannot be ready.
2. TERMINATED: strict kernel stat proves absent or same-start Z/X, including
   transient absence after a failed observation operation. Return None, which
   means no consumer evidence and can never satisfy prompt/readiness checks.
   Zombies are not called cleaned: cleanup must still prove retirement.
3. INVALID: observed reused PID/start mismatch, live changed session/group/tty,
   nonterminal/wrong device, missing live fd, access denial, malformed/short
   stat, or another unexplained read failure. Raise; do not certify readiness.

A returned sample is point-in-time evidence, not proof of future liveness.
Unobserved reuse after an absent sample cannot produce a readiness verdict.

## Bounded observation sequence

Use a small strict stat reader for consumer observation. It reads only proc
stat fields, validates PID and field count/integers, and propagates access,
I/O and parse failures. Do not reuse process_info's broad OSError-to-None
behavior as proof of death. Keep process_info/cleanup ownership semantics.

Open the proc PID directory once (O_DIRECTORY/CLOEXEC); fd-relative stat,
fd0 open, metadata/readlink operations stay anchored to that incarnation.
If directory open fails with ENOENT/ESRCH, perform one strict fresh stat
classification. A different start fails even when its state is Z/X.

Sequence: enumerate cached row -> open proc directory -> first strict stat
-> verify against row PID/start/session/pgrp/tty -> open fd0 with NOCTTY,
NONBLOCK and CLOEXEC -> fstat -> readlink fd0 -> path-device revalidation
-> final strict stat -> compare stable identity and controlling tty/device
-> return actual final tpgid. tty_nr uses Linux documented bit decoding.
Do not compare tpgid across samples: foreground jobs can legitimately change.

A disappearance at any step is classified once, without retry loops or sleeps:
strict fresh kernel stat absent or same-start Z/X permits None; observed
reuse or still-live identity/read/device problem raises. Even on a successful
operation, final stat can prove exit and suppress the sample. EBADF from our
owned fstat/close is a tool error, never termination proof. All owned directory
and terminal descriptors close in finally on success, absence and error.
No repeat-until-success observation and no lifecycle extension of deadlines.

## Caller integration and aggregate outcome

consumer's public result remains sample-or-None. original_prompt and native
read readiness still require nonempty actual consumer plus existing exact
PS1/color/current-row/caret/cwd predicates. An enumerated row alone must not
update a current consumer observation after TERMINATED. Historical before/
after records remain history, never substitute for current readiness.

Inspect both inline_fixture and inline_native_fixture call sites. Native
fixture currently performs /proc/exe identity/hash reads after consumer and
therefore has the same exit boundary. It must not bypass binary binding.
Preferred bounded integration: add optional expected executable path/hash to
the same anchored observation, before final stat; pass native binding there.
Native caller records proven sample identity only when a sample exists.
If reviewer considers this beyond necessary scope, keep native unchanged and
explicitly mark its exit boundary unresolved; do not claim domain closure.
Do not alter legacy production_takeback.py or historical cases.

Premature product exit still fails unchanged verify_outcome: startup stages,
PS1 bytes, same original Bash, command/tool/effect identity, fresh once, actual
Agent responses, routing, termios, child exit and owned cleanup all remain
mandatory. None never changes error/monitor/result to PASS. Normal exit after
all required facts may finish observation without falsely claiming PID reuse.

## Complete input and verification matrix

| Boundary/input | Expected | Evidence type |
| --- | --- | --- |
| Live foreground in another session | actual in-session tpgid equality | actual Linux PTY |
| Live background same controlling tty | unequal groups, never ready | actual Linux PTY |
| Alive stale start / nonterminal stdin | fail closed | actual Linux PTY |
| Normal exit, unreaped zombie, reaped process | None, no ready; separate cleanup retirement | actual Linux PTY synchronized by pipe/wait |
| Exit after enumeration, before directory open/first stat | None only after strict death proof | controlled phase injection |
| Exit after first stat, before fd0 open | same | controlled phase injection |
| Exit after open, before/after fstat | no sample after final death proof; EBADF fails | controlled phase injection |
| Exit before/after readlink and path stat | None only with death proof | controlled phase injection |
| Exit before/after optional exe read/hash and final stat | same | controlled phase injection |
| PID reused at each acquisition/recheck stage | fail when different start observed, even Z/X | controlled proc snapshot injection |
| Live SID/pgrp/tty changes at each read boundary | fail | controlled snapshot injection |
| Live fd closes/moves to another device/path | fail | controlled fd metadata injection |
| Permission denied/short malformed stat/I/O | fail, never None | controlled failure injection |
| Foreground changes while identity remains stable | return actual final tpgid, no fake readiness | controlled snapshot injection |
| Every success/None/error branch | all acquired descriptors closed | descriptor accounting |
| Fake tpgid := pgrp | compiled mutant detected by background assertion | actual Linux PTY |
| Remove start/tty/death-proof rejection | compiled mutants caught by exact assertion controls | controlled injection, labelled as such |

Phase injection is a unit boundary control, not claimed as actual kernel PID
reuse or real scheduling. Test mocks must be at proc/OS read boundaries, never
mock the consumer verdict. Actual Linux tests compare observation against
child's in-session tcgetpgrp, synchronize exit, reap children and verify no
leftover owned PID/fd. Existing positive/negative prompt tests remain intact.

## Implementation and freeze gate

Root independent design review first. Then a fresh exclusive tool tree from
411bf26; tests first with effective assertion RED (not exception-only), then
minimal unified observer/caller change. Capture actual Linux and controlled
phase suites separately, all existing tool tests, compiled mutations and diff
check. Independent code review, clean commit/tree, full archive/manifest and
new dependency bindings are required. Root stages/revalidates identity and
explicitly resumes minimal ALLOW. Subsequent four cases stay stopped until
ALLOW passes. Any new failure is preserved and returned to Root; no patch loop.
