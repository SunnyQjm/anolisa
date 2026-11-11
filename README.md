# Trial access localization evidence

Real cosh-shell and cosh-core binaries ran in an isolated Alibaba Cloud Linux 4
ARM64 container, using a 100-column, 42-row PTY. IMDS and SysOM were simulated
locally. This is scripted PTY evidence, not real-provider or release acceptance.

The before/after PNG and WebM pairs show the English suppression confirmation
and Chinese model setup error. The cancellation pair verifies the unchanged
ordinary cancellation notice.

`evidence.zip` preserves the full original directory layout, sanitized casts,
all screenshots and WebM replays, acceptance points, and CLI-generated visual
evidence indices with source and output hashes. The session cases verify no
persisted preference and no additional model request after suppression.

The after recordings were refreshed after rebasing onto main ca7dfc79b.
Only the existing raw CLI test expectations changed since the first review;
the production localization behavior is unchanged. The final source revision
is 150021933e4fa4659be3ab3289e92e68944699b7.
