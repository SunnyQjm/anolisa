# Health UI evidence

After: production source matching current PR head, base cabcfe2f9, captured patch SHA256 901bd0683aee11768e5061e3e60cfff815459d79a3bc42881f9e2142cd663c87.
Binary SHA256: 5b4e3ed75040a329f4c6bafee26572e77c0881bdf263459fe4713f08bfa73697. See binary-provenance.json for matching source hashes.

Real Alibaba Cloud Linux 4 aarch64 container; current debug binary runs `health banner` against actual system facts. No simulated resources, fake adapter or provider call. Render width is 40 columns inside a 44-column by 22-row PTY to avoid full-line repaint drift. Both languages and color/NO_COLOR are separate canonical scripted-PTY cases.

Each after PNG and WebM is derived by cosh-lab from the matching sanitized .cast. All four runs passed evidence verify and full-size visual inspection. The status appears once and available load/memory/disk quantities remain visible. EN places the complete status in the body; ZH can fit the complete status in the title.

Before PNGs are explicitly labeled and come from the original installed ALinux4 x86_64 image, cosh-ng-0.29.1-1.alnx4.x86_64. They document the original defect only; they are not current-binary acceptance or a same-machine performance comparison.

This is a development UI acceptance result. No full crate/workspace, x86_64 after, provider or release acceptance claim is made by these visual assets.

The current PR head 13f7a5079807b3185946943cca7b0905ffba9f2d only regrouped private cfg(test) regression matrices after capture, with every assertion retained. health.rs and health/layout.rs are byte-identical to the captured source; default production binaries exclude health/tests.rs. The provenance records both the captured source commit and the production-equivalent current head.

Final local validation uses Rust1.93 and a target unique to this exact source (`/tmp/cosh-linux-preflight/ui-target-1.93`), independent from all other PR mirrors. verification-manifest.json binds host commit13f7a5079, exact full-index patch89c9db..., successful strict preflight/binary build, health16/library+16/binary, logic12 and both test ELF hashes. Each actual test ELF defines all three regression assert helpers; overlap693 is unchanged. The unit+logic+four-PTY development aggregate returns Go. Earlier shared-target runs are excluded from final acceptance. This terminal build is distinct from the independent visual-capture build recorded in binary-provenance.json; the production source bytes are identical.
