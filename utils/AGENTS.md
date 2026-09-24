# AGENTS.md (utils/)

This folder holds the tooling that produced `../ascii/`. The rest of
the repo (`hello-banner.zsh`, `../ascii/`) is the shipped product and
has no dependency on anything here at runtime -- this is
maintainer/generation-time tooling only.

## generate.py

Rasterizes a directory of source SVGs (one cursive "hello"-style
wordmark per language, named `hello-<lang>.svg`) into the block-element
`.txt` files in `../ascii/`.

```sh
python3 generate.py --svg-dir /path/to/svgs --out ../ascii
```

Requires `rsvg-convert` and `magick` (ImageMagick 7) on PATH. No other
dependencies -- it parses PGM output by hand rather than using PIL, so
there's nothing to pip install.

Source SVGs must share one consistent unit system across the whole set
(this repo's SVGs all use `stroke-width="60"`) since each language's
column width is derived by comparing viewBox widths directly against
each other -- see "Design conventions" below.

## Design conventions the script encodes (don't relitigate without reason)

- **Never stretch a language wider than its natural proportion.** Each
  language's column width = its source SVG's viewBox width, scaled by
  one constant factor shared across every language being generated in
  that run (anchored so the naturally widest word reaches the tier's
  target width: 50/32/22 columns for full/compact/mini). A short word
  being narrower than a long word is correct, not a bug -- it gets
  centered in the shared box width, not stretched to fill it.
- **The period sits on the baseline, not the canvas edge.** It's
  placed a fixed 3-column gap after the rightmost point of whichever
  row's ink spans the widest fraction of the glyph (that's the shared
  connecting stroke / baseline), not a fixed offset from the canvas
  edge and not the literal bottom row -- a descender (e.g. French
  "bonjour"'s j) drops a whole row below the actual baseline.
- **Box widths must match across every language within a tier**,
  since `hello-banner.zsh` picks a language at random at runtime. The
  script already handles this: it renders every language in a batch
  before centering any of them, so run it once across the whole set
  rather than one language at a time, or you'll get mismatched box
  widths.
- **A single lone half-block character reads as chopped/thin**, and
  two adjacent half-blocks only read as connected, gap-free ink if
  they face toward each other's filled side. The auto-generation
  doesn't always avoid this on its own at these tiny resolutions --
  see `../HINTING.md` for the manual fix.

## Workflow for adding or regenerating a language

1. Get (or draw) a `hello-<lang>.svg` in the same style/unit system as
   the rest of the set.
2. Run `generate.py` across the *entire* source SVG directory (not
   just the new file) so box widths stay consistent across all
   languages -- the shared-width computation needs every language in
   the same run.
3. Copy the output into `../ascii/`, overwriting the old files.
4. Eyeball the new language (and re-check a couple of others you
   didn't touch, in case the shared box width shifted) for any glyph
   that reads as chopped or gappy, and hand-fix per `../HINTING.md`.
5. Update `_HELLO_BANNER_ALL_LANGS`, the width thresholds (if the box
   width changed), and the plain-text fallback greeting in
   `../hello-banner.zsh`.
