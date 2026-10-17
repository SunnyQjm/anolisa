# Gateway login PATH review resolution

Current atomic PR HEAD: `f557b5f4721270218214157878ec6b405626eebc`
Base: `7828cc3a9f0de40e185ad1b4b26e28d39043ba28`

The existing Task Gateway child now uses the same trusted startup-PATH builder as
Core/provider/audit children. Executable override/sibling priority, arguments,
socket selection, stdin and output handling are unchanged. No worker integration,
PS1 wrapping, dependency/lock or threshold change is introduced.

The real Bash login PTY runs a copied actual Shell with no sibling Gateway and no
executable override. A protocol-fixture Gateway exists only in the profile PATH.
Queries prove list/show arguments, profile once and trusted absolute PATH; typed
submission proves exact goal bytes, one submission and fresh input once without
running goal text as shell input. This fixture is not a real-provider acceptance.

The old production builder produces compiled exact-query RED with Gateway ENOENT.
One compilable production-line mutation produces the same RED with unchanged test
bytes; restoring the fix gives GREEN. The original timeout attempt and corrected
direct assertion baseline are both preserved in raw archives. Root independently
verified native stream SHA/counts, source identity and cleanup after handback.

Combined-source c2eadb530/tree5ffc628ad (also #7628) passes fullraw 609/0/1 and
native Rust1.97.1 standard preflight. That fullraw identity is retained explicitly.
The current atomic PR removes only the separate #7628 test-order patch; its own
Rust1.97.1 standard preflight and four exact query/submission/override/forged-late
controls each pass 1/1. Raw envelopes and source SHA/mode manifest are attached.

The older registry-unit first failure remains unexplained and No-Go; this Task
fix does not close it. Final installed/dual-architecture/provider/8h/VM acceptance,
remote current-head CI and formal approval remain pending. No release or default
enable approval is implied.
