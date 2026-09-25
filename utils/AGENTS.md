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
  target width: 105/86/54 columns for full/compact/mini). A short word
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
- **A single lone half-filled character reads as chopped/thin**, and
  two adjacent partially-filled characters only read as connected,
  gap-free ink if they face toward each other's filled side. The
  auto-generation doesn't always avoid this on its own at these tiny
  resolutions -- see `../HINTING.md` for the manual fix.

## viewBox padding

Every source SVG's `viewBox` is fit to its path *control points*, not
to the rendered ink -- a stroke's ink extends `stroke-width / 2`
beyond the path in every direction (more at round caps/joins), and SVG
clips anything outside the viewBox by default. `generate.py` pads the
viewBox by half the stroke width before rasterizing (`padded_viewbox`/
`write_padded_svg`) specifically to stop this from silently chopping
off stroke ends -- e.g. the lead-in stroke of "hello"'s h, or the tail
after the o. This relies on `stroke-width` being a literal attribute
on the SVG (not set via CSS/a class), same as the unit-system
assumption above.

## Aspect ratio

Terminal character cells are roughly twice as tall as wide. A source
SVG's viewBox is proportioned normally (equal x/y units), so
rasterizing it into a `cw x ch` character grid 1:1 -- treating a
column and a row as equally "wide" -- stretches every glyph taller and
narrower than its true shape once actually displayed. This is why the
art looked "condensed" before this was addressed: a `cw:ch` ratio that
looks reasonable in raw character counts is only around half that once
you account for the cell shape.

The fix has two parts, and both matter:

1. **Rasterize at each tier's `target_cw`/`ch` ratio, not 1:1.** The
   `TIERS` column/row combinations were chosen so `cw/ch`, times the
   terminal's own cell-aspect correction (~0.5), lands close to the
   *source* SVG's true `viewBox` aspect ratio for the widest language
   in the set. `full` is close to true proportions; `compact` and
   `mini` are deliberately left more condensed than true (see below),
   since correcting them fully would need a much wider minimum
   terminal than a "compact"/"mini" tier should require.
2. **Use a 2x3 sextant subgrid per character, not 2x2 quadrants.**
   Quadrants (`SUB_ROWS = 2`) only give 2 sub-rows of vertical detail
   per character row; fixing the aspect ratio means fewer character
   rows are available for a given tier, so more vertical detail per
   row is needed to avoid losing fidelity. Sextants (`SUB_ROWS = 3`,
   `SUB_COLS` unchanged at 2) give 50% more vertical resolution per
   row, which is what makes `compact`/`mini` still read cleanly at a
   deliberately-condensed aspect ratio, and what makes `full` densely
   detailed at true proportions instead of needing an impractically
   wide column budget to get there through columns alone.

Don't relitigate the exact `TIERS` numbers without re-testing by eye
-- they're a judgment call balancing proportion correctness against
minimum terminal width, not a formula with one right answer. If you
do change them, recompute `hello-banner.zsh`'s column thresholds from
the actual generated box width (the `generate.py` output prints it
per tier) rather than reusing the old ones.

### Font support

Sextant block characters (U+1FB00-1FB3B) are from Unicode 13.0 (2020).
Support is inconsistent: as of this writing, no font actually shipped
with macOS has real glyphs for them (checked via each font's own
cmap, not `fc-match`, which reports misleadingly-optimistic fallback
candidates that don't actually contain the glyph) -- yet they still
render correctly in at least some real-world terminal/font
combinations, apparently via the OS's own per-glyph symbol-font
fallback rather than the terminal's primary font. Practically: test
any change in an actual terminal, not just by reading the raw
characters in a file, and don't assume a font's advertised coverage
(or lack of it) predicts what a user will actually see.

## render_readme_preview.py

GitHub renders README code blocks with its own fixed font, with no
per-glyph fallback the way a real terminal app gets -- it doesn't have
the sextant characters `generate.py` uses, so embedding the real
`ascii/hello-en-ascii.txt` there shows up broken. This script
re-renders "en" at the same full-tier proportions using the older,
universally-supported quadrant block characters instead, and splices
the result into `../README.md` in place of the existing banner code
block.

```sh
python3 render_readme_preview.py --svg-dir /path/to/svgs
```

Run it whenever the full tier's dimensions change, or "en"'s source
SVG changes. It renders every language (not just "en") at quadrant
resolution to get the correct shared box width -- same reason
`generate.py` does that -- so it takes a similar amount of time to run
as the real generation pass.

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
