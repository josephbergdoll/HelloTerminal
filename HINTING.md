# Manual hinting for chopped letters

At these tiny character-grid resolutions (as few as 1-2 columns per
letter), the auto-generated art in `ascii/` sometimes renders part of
a round letter (the "c" in "ciao", the "a" in "ahoj") as a single lone
half-block. On its own that reads as thin/chopped; if a second lone
half-block ends up next to it, it can look actively broken -- a visible
gap -- rather than just thin.

## The bug this causes

Each character cell is 2x2 subpixels. A half-block character (`▌` left,
`▐` right, etc.) only fills half of those subpixels; the other half is
transparent background. Two adjacent cells that are *both* only
half-filled toward each other's blank side produce an alternating
ink/blank/ink/blank subpixel run, which reads as a gap slicing through
the stroke -- even though the two characters are sitting in adjacent
cells with no actual space between them.

## The fix

1. Insert one new column immediately to the left of the weak spot,
   for every row of that glyph (not just the affected row), so nothing
   else in the word shifts out of vertical alignment. Trim one
   trailing blank column from the same rows (there's always slack in
   the box's right-hand padding) so the file's total width, and the
   box border, don't change.
2. Fill the new column, in the affected row only, with a **right-half
   block** (`▐`) -- its ink sits on the side touching the next column,
   so there's no blank subpixel between them. (A left-half block here
   would recreate the same bug one column over.)
3. Upgrade the original weak character (now shifted one column right)
   from a half-block to a **full block** (`█`), so it has no blank
   half left to create a gap with anything.
4. Leave every other row of the glyph as just a shift (a blank
   character in the new column) -- only patch the row(s) that were
   actually thin.

Rule of thumb: two block characters only read as touching, gap-free
ink if, at their shared edge, both sides are filled. A full block
touching anything is always safe; two half-blocks only work if they
face toward each other's filled side, not away from it.

This was done by hand-editing the saved `.txt` files directly --
no need to rerun the SVG-to-ASCII generation pipeline for a
single-glyph touch-up like this.
