# PR7979 immutable evidence

Source: [PR7979](https://github.com/agentic-os-org/ANOLISA/pull/7979), native commit `b353d6185b2abe0b99460430ccd7954bd4ce21ad`, tree `cf23b75a2c151da8e85a16e44b3653422cbb4f7b`, Cosh subtree `f1dbd5bd1cee77ee311a9a104aa539dcdd692afc`.

[Complete evidence bundle](evidence-bundle.tar.gz) contains all248 original files with directory structure, native RPM/SRPMs, original failures, both complete raw runs, compiling controls, all runtime sidecars and canonical PNG/WebM provenance. [Bundle content hashes](SHA256SUMS.json) describe the unpacked original tree. The fixed assets CLI uploads only top-level files, so this archive preserves nested proof without modifying that tool. [Published top-level hashes](ASSET-SHA256SUMS.json) describe the flat export.

[Final report](FINAL-REPORT.md) · [Acceptance JSON](FINAL-ACCEPTANCE.json) · [Exact native commit preflight](FINAL-PREFLIGHT.json) · [Cleanup](OWNED-CLEANUP.json) · [Original aggregate gate Go](LOCAL-GATE.json) · [Source equivalence](REBASE-585d-RECEIPT.json) · [RPM payload proof](ROOT-RPM-PAYLOAD-VERIFIED.json).

[Installed prompt-refault native test](INSTALLED-PROMPT-REFAULT.json) and [actual runtime identity](INSTALLED-PROMPT-IDENTITY.json) support the original before-input PS1 text/color/current-line/caret assertion. Same Bash, one approved effect and one HostExecutedResult continue through the second physical write failure. The canonical bash-returned screenshots are after an explicit UI_BASH_READY/exit; they are not idle-prompt-before-input proof.

Actual casts: [baseline](baseline.cast) · [installed resize](installed-resize.cast) · [installed fault](installed-fault.cast). Captures contain fixture commands and loopback output; no credential input/output was found in publication review. Bytes match verified render provenance.

The baseline canonical capture was incomplete after two reached points, not a full canonical RED. Its legacy card screenshot is real, while definitive activation RED is the actual expected1/observed0 worker test in the bundle. Both full raw outcomes (first610/16/1; corrected-environment626/0/1) remain preserved.

Both RPM NEVRAs are local transaction VERSION overrides, not formal releases: pristine a37 baseline0.27.0-2.alnx4 has no worker, reviewed candidate0.27.1-2.alnx4 owns the worker. Real install/upgrade/reinstall/rollback/uninstall were verified. Actual post-strip installed binaries are distinct from earlier R5 unstripped binaries. Canonical repo.commit=null remains honest; Source0/ELF and rebase equivalence bind the source externally without relabeling original runs.

This is measured ARM64 local Go. Integrated dual-architecture, real-provider, default-login and release acceptance remain ParentRoot-owned. U02a/b/c stay open for the expressly missing broader witnesses/interfaces; see [production interfaces](PRODUCTION-INTERFACES.json).
