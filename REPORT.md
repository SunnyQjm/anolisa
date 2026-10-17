# Current-main login PATH integration validation

Source HEAD: `66aee7e7df16648a5dd6cbeae4e9abd9a32117a4`
Source tree: `d878164285d35552c4db38d339bdb7a976790503`
Base: `7828cc3a9f0de40e185ad1b4b26e28d39043ba28`

The existing atomic login-PATH fix is rebased onto the merged inline withdrawal.
The existing Core-probe eligibility expression moves into startup_auth; bootstrap
is 696 lines under the unchanged 700-line gate. The original author, attribution,
Fixes reference and login-PATH behavior are retained. No locks or dependencies change.

ALinux4 ARM64, Rust 1.97.1: standard preflight passes (commit lint, fmt,
workspace/all-target Clippy, layout/source-layout/test-inventory gates).
Eight named raw-CLI controls each pass exactly 1/1 without retries: first Core/tool
lookup, audit profile-once PATH, startup-auth readiness, forged/late PATH rejection,
unset profile PATH fallback, approval input isolation, input-wait evidence, and
slash-bearing Han routing. Raw envelopes and source SHA/mode manifest are attached.

The earlier 607/0/1 fullraw result belongs to combined tree f4d1ae31 (also #7628),
not this PR exact-head full suite. A prior combined unit-run registry fixture
failure is still unexplained; later green runs do not establish a repair or flaky
classification. The product release gate remains No-Go. This evidence does not
claim installed/real-provider, final dual-architecture RPM, eight-hour or VM acceptance.
