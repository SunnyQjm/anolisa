# PR #1959 v2 evidence (argv executor rebuild)

Evidence for the v2 rebuild of #1959 (issue #1882), after the R3 review
veto retired the v1 handoff route. Head under test: `e791a9d5`
(`fix/cosh-1882-compound-readonly-route` on top of `origin/main`
`76fa95da`).

## Environment

- Backend: container `cosh-lab-arm64-1882` (alinux3
  `sha256:4d5988ed…818d`, arm64, 4C/8G), env-up run
  `20260728T050634Z-4262dee7` (retained-by-policy, cleaned up after the
  runs).
- Auth preflight (`env auth check`): `registry_ok=true`,
  `resolved_provider=dashscope`, `model=qwen3.7-plus`,
  `adapter_type=dashscope`, `effective_auth_required=false`,
  private copy unchanged.
- Binaries built in-container from the head tree:
  - `cosh-shell` sha256 `77f2ae2ca7a67a2d03ee4ce8e9f6bd4e874244910b00d0c5dac978f71633ed43`
  - `cosh-core`  sha256 `f6e5b0a16ef570e32ebffe2dfe1251cd9b1d469e795a73653bcea60019379233`
- Runner: real cosh-core adapter + real provider, scripted PTY
  (PTY 100x30, `COSH_SHELL_WIDTH=96`), approval mode `auto`,
  `--gate feature-acceptance`, canonical cases from
  `specs/shell-e2e-validation/cases/interaction-cards.yaml`.

## Runs (all PASS, `gate evaluate --require acceptance` → Go)

| Case | Run | Scenario | Key frames |
|---|---|---|---|
| CARD-026 | `20260729T102005Z-e4666bf5` | `pwd && df -h` auto-executes, no approval card; aggregated output returned | auto-approved, compound-output |
| CARD-027 | `20260729T102050Z-d89b0645` | newline-separated compound (v1 hang scenario) auto-executes under the executor, both segments run | auto-approved (card shows the two-line command), compound-output |
| CARD-028 | `20260729T102133Z-5fd0c789` | custom `histchars='@^#'`: `echo @-1 && df -h` prints the literal `@-1` (no history expansion, no parsing layer) | auto-approved, compound-output (`@-1` literal) |

Each run directory holds the sanitized cast, per-point PNG screenshots,
a cast-replay WebM for the layout-sensitive `auto-approved` point, and
`result.json` (`execution_evidence=scripted-pty`, `failures=[]`).
`evidence verify` passed for all three runs; this bundle carries the
same files (see `v2-evidence.sha256`).

## Semantic deltas of the v2 route (recorded as-is)

- Executor output is injected through the shell-tool result channel
  (rendered inside the Agent card): auto-executed compounds do not
  enter the terminal history and produce no direct terminal echo.
- Tokens are passed verbatim to `execve` — no glob/tilde/history
  expansion (`echo @-1` above; `ls ~` reports “No such file or
  directory”; covered by unit test `executor_passes_tokens_verbatim`
  and the integration control group
  `shell_expands_globs_so_verbatim_token_assertions_are_not_vacuous`).
- Connector semantics: `&&`/`||` short-circuit like a shell, exit code
  is the last executed segment's; per-stage timeout and output
  truncation match the single-command readonly pipeline.

## Notes

- Base-side (fail-closed card) evidence is unchanged from the v1
  bundle on this branch (`fail-approval-card.png`,
  `pass-newline-failclosed-card.png`); the v1 PASS-side assets are kept
  for history and no longer describe the merged behavior.
- The first CARD-026 attempt on 2026-07-29 stalled on a container NAT
  outage (host network fine, container egress dead; Apple container
  service restart fixed it) and was superseded by the run above.
