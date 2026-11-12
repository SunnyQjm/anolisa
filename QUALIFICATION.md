# Default login delivery qualification

Go for the named official ALinux4 x86_64 target and source-matched natural default RPM. Installation preserves Bash accounts. Set/Restore and new SSH logins were exercised against the installed release package, with AI disabled.

- Source revision and immutable package hashes: [PR revision](pr-revision.json), [source](source-provenance.json), [RPM artifacts](artifact-provenance.json).
- All scenarios, exact results and historical failures: [qualification matrix](qualification-matrix.json).
- Strict native Rust1.93.1 gates and 83 selected tests: [preflight](native-preflight.json), [verification manifest](native-verification-manifest.json).
- Actual management-parent death, inherited vipw locks, commit and Restore: [raw result](parent-exit-v2.json).
- Actual native RPM writer held before Set: [raw result](rpm-first.json).
- Actual stop-job refusal preserves the package and running Gateway: [raw result](stop-job-refusal.json).
- Unrecorded aliases are refused without guessing an original shell: [raw result](alias-no-record.json).
- SSH command output/exit parity: [raw result](ssh-command-parity.json).
- Fresh no-command SSH default entry: [provenance](ssh-default-entry.json).
- Named feature aggregate: [Go](feature-gate.json); full crate/workspace execution and real-provider calls were not run.
- Task ECS, accounts, policy and key cleanup: [final receipt](cleanup-final.json), [system readback](task-cleanup-result.json).

Visuals are genuine PTY captures. [New SSH enters Cosh](images/sshd-default-entry-cosh.png), [Restore returns new SSH to Bash](images/sshd-default-entry-bash.png), [existing Bash after Set](images/old-bash-after-set.png). [Cosh video](recordings/sshd-default-entry-cosh.webm) and [raw cast](recordings/20261112T181147Z-f6fbac99.cast).

The original failed driver attempts remain in the local evidence bundle and are described in the matrix. ExecStopPost77 was a fully stopped service, not a failed stop job; the original erroneous rejection expectation is retained, and a fresh real stop-job-refusal case passed. No source change was made to hide that result.

Supported rollback uses the controlled lifecycle route after Restore. Arbitrary old packages lacking compatible preflight remain outside that route's guarantee. Runtime platform, exact native tools, asset and authorization checks are retained. This is not an all-platform or full-release claim.
