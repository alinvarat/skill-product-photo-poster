# Poster layout and spec

Read before building or adjusting a poster spec.

- Default 1500x1500 (`ratio: "1:1"`); `3:4` means 1500x2000 and needs a request. Never rotate photos.
- Purple accent `#a66bff`; plain white text/shadow, no text boxes/frames. No subtitle unless supplied.
- Photos cover cells edge to edge by cropping, not blur/extension. Use `focus`/`vfocus` percentages to keep pads/tips visible and subjects outside text.
- Clear PULSE logo at bottom-right, about 13% width; `assets/logo/pulse_logo.webp`. Disable only on explicit request. Keep bullets clear of it.
- Fixed gradients: top 20% of width at rgba(10,8,16,.7); bottom 32% at rgba(10,8,16,.8). Do not retune per poster or scale by height.
- Font `noto`: Inter Latin + bundled Noto Sans Thai. `prompt` is an alternative. Do not use Leelawadee or bundle Apple SF. Render Thai through Chrome, not PIL without shaping.

JSON fields: `photos[]` (1-3), `title?`, `subtitle?`, `bullets[]?`, `focus[]?`, `vfocus[]?`, `ratio?`, `split[]?`, `layout?` (`cols` or `rows`), `bullet_size?`, `font?` (`noto` or `prompt`), `accent?`, `width?`, `logo?`, `logo_size?`, `logo_opacity?`. Photo paths are relative to the spec file; arrays have one value per photo.

Use supplied product text verbatim, dropping only leading bullet markers; do not silently correct its spelling. For a text poster, gather the title and short supplied bullets; ask if necessary text is absent. Do not invent specifications.

Examples: `examples/pulse16mux.json` and `examples/pulsemini_v22.json`. For 7+ long bullets, the approved Mini example uses rows, unequal split `[43,57]`, bullet size about `.022`, and vfocus to put the seam between boards. This is a starting point, not a guarantee of no clipping.

Photo-only request: omit title/bullets, use one source per output with normal gradients/corner logo; see `examples/pulse_set_1.json`. Do not merge separate photos unless asked.
