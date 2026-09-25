# Manual hinting for chopped letters

At these tiny character-grid resolutions, the auto-generated art in
`ascii/` can still render part of a round letter (the "c" in "ciao",
the "a" in "ahoj") as a lone sliver of ink. On its own that reads as
thin/chopped; if a second weak spot ends up next to it, it can look
actively broken -- a visible gap -- rather than just thin.

## The bug this causes

Each character cell is a 2-column x 3-row sextant subgrid, rendered
with the Unicode block sextant characters (see "Aspect ratio" in
`utils/AGENTS.md` for why). A sextant character only fills whichever
of its 6 cells have ink; the rest are transparent background. Two
adjacent cells that are each only filled on the side *away* from each
other produce an ink/blank/ink/blank run at their shared edge, which
reads as a gap slicing through the stroke -- even though the two
characters are sitting right next to each other with no actual space
between them.

Rule of thumb: two block characters only read as touching, gap-free
ink if, at their shared edge, *both* sides are filled. A full block
(`█`) touching anything is always safe. A half block (`▌`/`▐`) is
safe if its filled side faces the neighbor. Any other sextant shape
needs checking edge-by-edge for the specific row(s) that touch the
neighbor.

## The fix

1. Insert one new column immediately to the left of the weak spot,
   for every row of that glyph (not just the affected row), so nothing
   else in the word shifts out of vertical alignment. Trim one
   trailing blank column from the same rows (there's always slack in
   the box's right-hand padding) so the file's total width, and the
   box border, don't change.
2. Fill the new column, in the affected row only, with a sextant shape
   whose ink sits on the side touching the next column (e.g. a
   right-half shape if the neighbor is to the right) -- so there's no
   blank cell between them at the shared edge.
3. Upgrade the original weak character (now shifted one column right)
   to a shape with full ink coverage on its left edge (a full block
   `█` is always safe), so it has no blank side left to create a gap
   with anything.
4. Leave every other row of the glyph as just a shift (a blank
   character in the new column) -- only patch the row(s) that were
   actually thin.

This is done by hand-editing the saved `.txt` files directly -- no
need to rerun the SVG-to-ASCII generation pipeline for a single-glyph
touch-up like this. Sextant characters are Unicode 13.0+ codepoints
(U+1FB00-1FB3B); type them by codepoint (e.g. via your editor's
Unicode input) rather than trying to eyeball similar-looking glyphs,
since many are visually close to each other at a glance.

Since these are unfamiliar characters, always **view your edit in an
actual terminal** (not just your editor) before considering it fixed
-- see "Font support" in `utils/AGENTS.md` for why rendering can vary.
