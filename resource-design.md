# Resource contract rebuild after second same-domain review

Baseline416a: O(P*T) private/token scans are a real resource bug. Session io.rs MAX_SESSION_FILE_BYTES is32MiB, not a fixture-only assumption. Rebuild the domain invariants instead of applying an isolated short-input fix.

Privacy: original text coordinates and global PEM scopes are immutable; Unicode/duplicate key classification remains; markers in classified values cannot erase another field's scope; same-token ordinary/secret before/after fragments remain; Schema/live context are unchanged.

Resources: two ordered disjoint interval streams use monotonic cursors, with each token/range advanced once and intersecting pairs O(P+T). A whole classified value covers its internal keys/tokens; skip repeated IgnoredAny parsing, so parsed classified-value bytes are disjoint and at most input bytes. Original PEM intervals are collected before skipping these tokens. Per-base alias suffix cursors avoid repeated occupied suffix probes in both normal JSON and PEM JSON. Range emission still sorts/merges M edits in O(M logM); do not call the whole function linear. Existing serde parsing/regex tokenization remain input-byte passes and O(N) storage.

Tests measure actual loop visits, suffix probes and consumed value bytes through cfg(test) thread-local counters, not wall time. Actual Store persist/load controls verify masking, ordinary fields/values and live copy. Baseline fixtures:1024 short PEM fields;1024 shape-key aliases;32 nested sensitive parents with ~90KiB leaf and a cross-parent PEM. Additional matrices cover long PEM across tokens, multiple PEM within one token, dense reserved suffixes and near32MiB/UTF8 after the bounded implementation. Effective mutations deliberately reset monotonic/alias cursors and remove covered-value skipping while retaining functional masking; they must fail resource bounds.

Implementation remains in Core's existing owner. Extract only PEM internals to private redaction/private_key.rs to keep parent below700; pub(super) functions only, no new dependency/platform/public API. Root tree untouched;416a candidate must again refreeze/rebuild after new HEAD. No scan-clean/risk waiver.
