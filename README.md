# PR 7551 / Issue 7545 immutable execution evidence

Final HEAD52745f8b / tree6cb94baf: Rust1.97.1 exact-four cases each1PASS; complete shell_host threads4=219PASS/0FAIL/1ignored; fmt/workspace-all-targets-Clippy/layout/inventory/commitlint/drift pass;1294source files match before/after;owned container independently absent. No provider/full-workspace/RPM/release acceptance.

Original v3 logs use original-v3 prefixes and remain distinct. Both source mutations compile successfully and fail the original assertions as documented. Initial restoration ran a cached mutant ELF and failed; source and actual ELF hashes prove artifact contamination. That failure is preserved, not labeled flaky. Owned package clean and fresh exact-HEAD compilation then passed all final scope.

native-execution-evidence.tar.gz contains full native argv/stdout/stderr, controls manifests/ELF hashes and guest readbacks. final-head-test-results.json contains the five final raw CLI execution outputs. See final-report.md for scope and boundary, final-acceptance.json for structured gate, review.md for independent code/L3 review.
