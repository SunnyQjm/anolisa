# ALinux4 issue evidence — 2026-11-12

Real installed image: ALinux4 x86_64, cosh-ng-0.29.1-1.alnx4.x86_64. Captured via a real PTY on the existing authorized ECS. No fix deployed. Screenshots were rendered from original ANSI asciicast v2 streams with agg --renderer resvg at 18 px and extracted losslessly with ffmpeg. No synthetic health card was created.

| Issues | Screenshot | Raw terminal recording | Scope |
|---|---|---|---|
| #9978, #9980 | [kernel and coverage](9978-9980-kernel-coverage.png) | [cast](9978-9980-kernel-coverage.cast) | Current 24-hour bounded kernel journal exceeds 16 KiB, contains pre-existing cgroup OOM; current health banner remains green while diagnostics export reports kernel_signal parse_error and no kernel facts. No OOM injected for this capture. |
| #9979 | [login gate](9979-login-gate.png) | [cast](9979-login-gate.cast) | Package lifecycle proof unavailable; login set refuses, root remains /bin/bash. |
| #9981 | [EFI findings](9981-efi-critical.png) | [cast](9981-efi-critical.cast) | Actual df plus filtered fields from actual diagnostics export JSON. /boot/efi at 4% is critical. This is diagnostic data, not a rendered /health card. |
| #9982 | [PROMPT_COMMAND replacement](9982-prompt-slot-trap.png) | [cast](9982-prompt-slot-trap.cast) | Real temporary account with owned HOME and valid XDG_RUNTIME_DIR. Hook starts active; replacing slot 1 leaves the original ERR trap. Account and runtime removed. |
| #9984 | [40 columns and NO_COLOR](9984-compact-no-color.png) | [cast](9984-compact-no-color.cast) | Actual PTY width 40, colored and NO_COLOR output in one image; duplicates/truncation remain visible. |
| #9983 closed | [startup](9983-startup.png), [ask](9983-ask.png) | [startup cast](9983-startup.cast), [ask cast](9983-ask.cast) | Reused original ANSI recheck from the same existing image. The earlier duplicate-prompt conclusion was withdrawn. [Startup GIF](9983-startup.gif), [ask GIF](9983-ask.gif). |

New recordings wait for explicit completed shell prompt markers before each next command. The final empty output event only adds a playback pause. This is manual image reproduction evidence, not canonical cosh-lab acceptance or a release gate. No wider build/test gate was run. Temporary users, runtime directories and all remote evidence directories were removed; existing ECS is retained.
