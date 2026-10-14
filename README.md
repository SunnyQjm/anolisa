# Resource review candidate evidence

HEAD: fa885dcbe1491cf8c17af6a399fa9a1d354475bd
Base: 4a4961e419170a202487902819f05482eb961db9
cosh-ng tree: 2a9faeb3c6020256b0558fe708f58d871d115629

The second P1 (416a) is reproduced with compiled actual Store tests: 8 persistence controls pass while three resource bounds fail. Four resource regressions now cover 1024 short blocks, a long cross-token block, 1024 blocks in one string, dense reserved aliases, 32 nested sensitive parents and a near30MiB input with Unicode ordinary fragments. Instrumented actual visits/probes/parsed bytes are bounded. Final rendering still sorts M edits in O(M log M); no whole-function linear or peak-memory claim.

Seven mutations compile and are killed (two interval cursor resets, two alias cursor resets, covered-value skip removal, decoded key bypass and same-token outside masking bypass). Restored source passes16 boundaries. The first attempted cursor mutation did not compile and is preserved separately, excluded from effective proof.

Current HEAD final preflight and six focused scopes pass33 executions, including24 new regressions. Core lib4/component21/actual binary2; Shell actual facts+preview3/adapter2/real PTY1. Local rule/behavior/code-safety and new-upstream integration review finds0 issues. Upstream UI was rebased without changing the owned patch or source hashes; current component tests are rerun after rebase.

source-delta-resource.patch includes only the three Core paths relative to416a, excluding upstream UI. The alternate delta applies relative to44ee; candidate blob preconditions identify which to use. Previous candidates/RPM/full suites do not certify this tree. Root must intake/refreeze/rebuild.

previous-416a/ and its previous-44ee/ preserve historical evidence. Formal review, exact-HEAD CI, AK terminal, provider, installed RPM and release acceptance remain separate. No external provider, hook subprocess e2e, local full suites, visual/cast acceptance, x86_64 or release Go is claimed. No merge or scan risk waiver.
