# PR #10345 visual evidence

Terminal frames for issue #10336 (cosh-shell silent reply truncation).

Provenance: PTY transcripts captured by the task's external driver against the
real `cosh-shell`/`cosh-core` binaries (ALinux4 arm64 container, 100x32, loopback
SSE fixture), exported through `cosh-dev collect`/`pull`. Frames rendered with
`agg` (external asciicast renderer) from those transcripts; PNGs are the final
GIF frame. cosh-dev native product-terminal recording of a custom provider is
unavailable on this host (development-image identity and local recipe version
constraints), so these are external renders of cosh-dev-collected originals.

- `before-big.png` / `before-big.gif`: base `de59dd679`, 1 MB single chunk.
  Card width collapses, tail marker and notice absent (the defect).
- `after-big.png` / `after-big.gif`: head `29e39869`, 1 MB single chunk.
  Full card width, explicit truncation notice, session record keeps full text.
- `after-many.png` / `after-many.gif`: head `29e39869`, 101 small chunks.
  Full render including the `MANYTAIL` marker, no notice.

Reviewed visually for content, size and absence of sensitive data before upload.
