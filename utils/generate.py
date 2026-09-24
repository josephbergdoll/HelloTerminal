#!/usr/bin/env python3
"""
Generate the ascii/ art for HelloTerminal from a directory of source
SVGs, one cursive "hello"-style wordmark per language.

Usage:
    python3 generate.py --svg-dir /path/to/svgs --out ../ascii

Source SVGs are expected to be named hello-<lang>.svg (e.g.
hello-fr.svg), single-color stroke paths, all sharing one consistent
unit system (this repo's set uses stroke-width="60" throughout) so
their viewBox widths are directly comparable across languages.

Requires `rsvg-convert` and `magick` (ImageMagick 7) on PATH.

See ../HINTING.md for the manual touch-up step this doesn't automate,
and ../utils/AGENTS.md for the conventions this script encodes.
"""

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys

QUAD_MAP = {
    (0, 0, 0, 0): ' ', (0, 0, 0, 1): '▗', (0, 0, 1, 0): '▖', (0, 0, 1, 1): '▄',
    (0, 1, 0, 0): '▝', (0, 1, 0, 1): '▐', (0, 1, 1, 0): '▞', (0, 1, 1, 1): '▟',
    (1, 0, 0, 0): '▘', (1, 0, 0, 1): '▚', (1, 0, 1, 0): '▌', (1, 0, 1, 1): '▙',
    (1, 1, 0, 0): '▀', (1, 1, 0, 1): '▜', (1, 1, 1, 0): '▛', (1, 1, 1, 1): '█',
}

# One tier = (suffix on the output filename, character rows, box margin,
# target column width for the naturally widest language in the set).
TIERS = [
    ('', 10, 5, 50),           # full
    ('-compact', 10, 2, 32),   # compact
    ('-mini', 8, 1, 22),       # mini
]

# Supersample factor: each character cell is a 2x2 quadrant grid, and
# each quadrant is itself averaged over a KxK block of rendered pixels
# before thresholding. A single pixel per quadrant is very sensitive to
# exactly where a thin curve lands on the pixel grid (it can make one
# side of a round letter, like the left of a "c", drop out while the
# other survives); averaging a KxK block is far less aliasing-prone.
SUPERSAMPLE_K = 4
INK_THRESHOLD = 160  # grayscale value (0-255); darker than this = ink


def check_deps():
    for tool in ('rsvg-convert', 'magick'):
        if shutil.which(tool) is None:
            sys.exit(f"generate.py: '{tool}' not found on PATH -- install it first.")


def read_pgm(path):
    with open(path, 'rb') as f:
        data = f.read()
    assert data[:2] == b'P5'
    idx = 2
    vals = []
    while len(vals) < 3:
        while data[idx] in b' \t\r\n':
            idx += 1
        start = idx
        while data[idx] not in b' \t\r\n':
            idx += 1
        vals.append(int(data[start:idx]))
    idx += 1
    width, height, _maxval = vals
    pixels = data[idx:idx + width * height]
    return width, height, list(pixels)


def viewbox_width(svg_path):
    with open(svg_path) as f:
        content = f.read()
    m = re.search(r'viewBox="([-0-9. ]+)"', content)
    if not m:
        raise ValueError(f"{svg_path}: no viewBox attribute found")
    return float(m.group(1).split()[2])


def render_glyph(svg_path, cw, ch, tmp_dir, tag):
    """Rasterize svg_path into a cw x ch character grid (as a list of
    strings), with the baseline-anchored period already placed."""
    sw, sh = cw * 2 * SUPERSAMPLE_K, ch * 2 * SUPERSAMPLE_K
    png_path = os.path.join(tmp_dir, f'{tag}.png')
    pgm_path = os.path.join(tmp_dir, f'{tag}.pgm')
    subprocess.run(
        ['rsvg-convert', '-w', str(sw), '-h', str(sh),
         '--background-color=white', svg_path, '-o', png_path],
        check=True,
    )
    subprocess.run(
        ['magick', png_path, '-colorspace', 'Gray', '-depth', '8', pgm_path],
        check=True,
    )
    sw2, sh2, pixels = read_pgm(pgm_path)

    def quadrant_ink(qx, qy):
        total = 0
        for dy in range(SUPERSAMPLE_K):
            y = qy * SUPERSAMPLE_K + dy
            row_base = y * sw2 + qx * SUPERSAMPLE_K
            for dx in range(SUPERSAMPLE_K):
                total += pixels[row_base + dx]
        avg = total / (SUPERSAMPLE_K * SUPERSAMPLE_K)
        return avg < INK_THRESHOLD

    grid = []
    for cy in range(ch):
        row = []
        for cx in range(cw):
            tl = int(quadrant_ink(cx * 2, cy * 2))
            tr = int(quadrant_ink(cx * 2 + 1, cy * 2))
            bl = int(quadrant_ink(cx * 2, cy * 2 + 1))
            br = int(quadrant_ink(cx * 2 + 1, cy * 2 + 1))
            row.append(QUAD_MAP[(tl, tr, bl, br)])
        grid.append(row)

    _solidify_tittle_dots(grid, cw, ch)
    _place_period(grid, cw, ch)
    return [''.join(row) for row in grid]


def _solidify_tittle_dots(grid, cw, ch):
    """A tittle (the dot over i/j) rasterizes as a tiny cluster of
    partial blocks at this resolution, reading as faint noise rather
    than a dot. Find ink cells that form a small connected blob
    separate from the main word body, and solidify the whole blob
    into full blocks."""
    ink_cells = [(cy, cx) for cy in range(ch) for cx in range(cw) if grid[cy][cx] != ' ']
    ink_set = set(ink_cells)
    visited = set()
    components = []
    for start in ink_cells:
        if start in visited:
            continue
        comp = []
        queue = [start]
        visited.add(start)
        while queue:
            cy, cx = queue.pop()
            comp.append((cy, cx))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    n = (cy + dy, cx + dx)
                    if n in ink_set and n not in visited:
                        visited.add(n)
                        queue.append(n)
        components.append(comp)

    if not components:
        return
    main = max(components, key=len)
    for comp in components:
        if comp is main:
            continue
        if len(comp) <= 3:
            for (cy, cx) in comp:
                grid[cy][cx] = '█'


def _place_period(grid, cw, ch):
    """Find the baseline row (bottom-up, the first row whose ink spans
    a wide fraction of the whole glyph's width -- the shared connecting
    stroke all the letters ride on; a pure descender only inks a narrow
    slice and gets skipped), then place a period a fixed 3-column gap
    after that row's rightmost connected stroke."""
    all_cols = [x for row in grid for x in range(cw) if row[x] != ' ']
    span_l, span_r = (min(all_cols), max(all_cols)) if all_cols else (0, cw - 1)
    total_span = max(span_r - span_l, 1)

    baseline_row = ch - 1
    for cy in range(ch - 1, -1, -1):
        row_cols = [x for x in range(cw) if grid[cy][x] != ' ']
        if not row_cols:
            continue
        if max(row_cols) - min(row_cols) >= total_span * 0.5:
            baseline_row = cy
            break

    def rightmost_connected_col(row):
        for x in range(cw - 1, 0, -1):
            if row[x] != ' ' and row[x - 1] != ' ':
                return x
        return -1

    last_ink_col = rightmost_connected_col(grid[baseline_row])

    gap = 3
    dot_w = 2
    dot_start_col = last_ink_col + 1 + gap
    total_w = max(cw, dot_start_col + dot_w + 1)
    for row in grid:
        row.extend([' '] * (total_w - cw))
    grid[baseline_row][dot_start_col] = '█'
    grid[baseline_row][dot_start_col + 1] = '█'


def box_centered(lines, margin, content_w):
    inner_w = content_w + margin * 2
    out = ['╭' + '─' * inner_w + '╮']
    out += ['│' + ' ' * inner_w + '│'] * margin
    for line in lines:
        extra = content_w - len(line)
        left = extra // 2
        right = extra - left
        out.append('│' + ' ' * margin + ' ' * left + line + ' ' * right + ' ' * margin + '│')
    out += ['│' + ' ' * inner_w + '│'] * margin
    out.append('╰' + '─' * inner_w + '╯')
    return '\n'.join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--svg-dir', required=True, help='Directory of hello-<lang>.svg source files')
    parser.add_argument('--out', default='../ascii', help='Output directory for the generated .txt files')
    parser.add_argument('--pattern', default='hello-*.svg', help='Glob pattern for source SVGs within --svg-dir')
    args = parser.parse_args()

    check_deps()

    svgs = sorted(glob.glob(os.path.join(args.svg_dir, args.pattern)))
    if not svgs:
        sys.exit(f"generate.py: no SVGs matched {args.pattern!r} in {args.svg_dir}")

    langs = {}
    for path in svgs:
        stem = os.path.splitext(os.path.basename(path))[0]  # "hello-fr"
        lang = stem.split('hello-', 1)[-1]
        langs[lang] = path
    print(f"Found {len(langs)} language(s): {', '.join(sorted(langs))}")

    vb_widths = {lang: viewbox_width(path) for lang, path in langs.items()}
    widest_lang = max(vb_widths, key=vb_widths.get)
    print(f"Widest word: {widest_lang} ({vb_widths[widest_lang]:.0f} units) -- anchors the scale")

    os.makedirs(args.out, exist_ok=True)
    tmp_dir = os.path.join(args.out, '.generate-tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        for suffix, ch, margin, target_cw in TIERS:
            all_lines = {}
            for lang, svg_path in langs.items():
                scale = target_cw / vb_widths[widest_lang]
                cw = max(3, round(scale * vb_widths[lang]))
                all_lines[lang] = render_glyph(svg_path, cw, ch, tmp_dir, f'{lang}{suffix}')

            shared_w = max(len(line) for lines in all_lines.values() for line in lines)
            for lang, lines in all_lines.items():
                out_path = os.path.join(args.out, f'hello-{lang}-ascii{suffix}.txt')
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(box_centered(lines, margin, shared_w) + '\n')

            tier_name = suffix.lstrip('-') or 'full'
            print(f"  {tier_name:8s} box width {shared_w + margin * 2 + 2:3d}  ({len(all_lines)} files)")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f"Done. Wrote {len(langs) * len(TIERS)} files to {args.out}")
    print("Remember: check the new/changed glyphs by eye -- see ../HINTING.md")
    print("for the manual touch-up a letter sometimes needs at these sizes.")


if __name__ == '__main__':
    main()
