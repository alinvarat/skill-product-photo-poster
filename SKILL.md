---
name: product-photo-poster
description: Build a PULSE product-photo poster with Thai text and logo. Square 1:1 by default; no video or carousel.
---

# Product photo poster

1. Use the user's 1-3 real photos and supplied product text; never invent specifications. Read [layout/spec](references/layout-spec.md) before writing JSON. Default 1:1; change ratio only on request. Keep the purple theme, fixed edge gradients and clear bottom-right PULSE logo. Do not rotate images or replace the crop with blur/extension.
2. Choose a matching example from that reference. Use `focus`/`vfocus` to preserve the subject. For photo-only work, one photo per output; do not merge unless asked. Keep supplied text/spelling and omit an unsupplied subtitle.
3. Run:
   `python3 -I "~/.claude/skills/product-photo-poster/scripts/make_poster.py" spec.json out.png`
   Write a new output, never over a source photo. The script uses a private Chrome/Chromium profile. If the browser is missing, report it; do not switch to unshaped PIL Thai text.
4. Open the PNG. Verify requested ratio, Thai tone marks, no clipped text, subject crop and logo/text separation. Adjust JSON and rerun when needed.
5. Return the verified PNG with the host's file attachment/link capability. Name anything unchecked; do not claim visual quality from a file exit code.
