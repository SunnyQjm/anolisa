# Visual evidence — PR #10331 (issue #10319)

Read-inactivity timeout for the cosh-ng openai_compat streaming provider.
All media are derived from real-PTY terminal captures of the product TUI
(120x32 grid, rendered 1188x768) against a deterministic local SSE fake
provider, using the verified build artifacts of the fix and of the unmodified
baseline. PNGs are full-grid final frames taken at the cast event boundary
after the complete card redraw; GIFs are 12x time-compressed playbacks
(timestamps scaled uniformly, content unmodified).

## Files

| File | Point | Source cast SHA256 |
| --- | --- | --- |
| rr-before-card.png | baseline: 130s silence tolerated, complete answer, no error surface | see manifest.json |
| rr-after-card.png | fix: Governance card "provider stream stalled: no data received for 120 seconds (read inactivity timeout)", partial output preserved | see manifest.json |
| rr-t60-card.png | fix: 60s silence tolerated, complete answer | see manifest.json |
| rr-before-12x.gif | baseline playback, 12x | see manifest.json |
| rr-after-12x.gif | fix playback, 12x | see manifest.json |

manifest.json is the cosh-dev derived-set/1 manifest (media hashes, source
cast hashes, processing notes, review records). Review: agent visual
inspection of every full frame (card completeness, CJK glyph integrity, grid
size, no truncation), conclusion approved; independent human render
verification not performed and not claimed.

## Provenance

- Capture: real PTY (openpty + TIOCSCTTY), product argv
  `cosh-shell raw cosh-core --isolated --shell bash`, isolated HOME with
  provider base_url pointed at the local fake SSE server; prompt sent at t+5s.
- Raw PTY byte streams, per-chunk timing indexes and fake-server logs are
  retained in the task evidence archive (private); hashes below bind them.
- Before-fix binary: cosh-core sha256
  fa882014674444144f05d5128fa13bcd69e1ba40ae0ca2f661d8237a72d47fa2 (stripped
  debug build of the unmodified baseline artifact).
- After-fix binary: cosh-core sha256
  ca89c03ab6414596c9b6937edae7c07cd680d8487a77d5daf61116c68e8d2573 (stripped
  debug build of the fix artifact); cosh-shell identical on both sides
  (12c5e266cb97fc09befdde3bff5fbd609c96addbddbd3d1f0dd5f14d1ee8a0d7).
- The provider patch is byte-identical across the rebase onto origin/main
  6e62cff2e (git range-diff equality); upstream changes do not touch
  cosh-core.
- Timing: before-fix server silence 130.000s completed with no client
  disconnect; after-fix client disconnected before the 130s resume
  (client_gone), timeout surface at prompt+120.4s; 60s control completed.
- Renderer: cosh-dev-node/0.1.0 recording export (headless Chrome + ffmpeg).
