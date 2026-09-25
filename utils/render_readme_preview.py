#!/usr/bin/env python3
"""
Regenerate the "hello" banner example embedded in ../README.md.

The shipped ascii/ art (see generate.py) uses Unicode sextant block
characters for extra vertical detail, which GitHub's fixed README
code-block font doesn't render (no per-glyph fallback like a real
terminal gets) -- they show up as broken boxes there. This script
renders the same "en" full-tier proportions with the older, always-
supported 2x2 quadrant block characters instead, just for the README
preview. The real ascii/ files are unaffected.

Usage:
    python3 render_readme_preview.py --svg-dir /path/to/svgs

Uses the same --svg-dir set generate.py was last run against, so the
preview's proportions match the current shipped art.
"""

import argparse
import glob
import os
import re
import shutil
import sys

import generate as g

README_PATH = os.path.join(os.path.dirname(__file__), '..', 'README.md')
LABEL = 'HelloTerminal.'
FULL_SUFFIX, FULL_CH, FULL_MARGIN, FULL_TARGET_CW = g.TIERS[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--svg-dir', required=True, help='Directory of hello-<lang>.svg source files')
    args = parser.parse_args()

    g.check_deps()

    svgs = sorted(glob.glob(os.path.join(args.svg_dir, 'hello-*.svg')))
    if not svgs:
        sys.exit(f"render_readme_preview.py: no SVGs found in {args.svg_dir}")

    langs = {}
    for path in svgs:
        stem = os.path.splitext(os.path.basename(path))[0]
        lang = stem.split('hello-', 1)[-1]
        langs[lang] = path
    if 'en' not in langs:
        sys.exit("render_readme_preview.py: no hello-en.svg found in --svg-dir")

    # Only viewbox_width (cheap: just a regex over each file) is needed
    # for every language, to get 'en's cw correctly scaled relative to
    # the widest word -- same as generate.py's main() loop. Only 'en'
    # itself needs to actually be rasterized.
    vb_widths = {lang: g.viewbox_width(path) for lang, path in langs.items()}
    widest = max(vb_widths.values())
    scale = FULL_TARGET_CW / widest
    cw = max(3, round(scale * vb_widths['en']))

    tmp_dir = os.path.join(os.path.dirname(__file__), '.readme-preview-tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    try:
        en_lines = g.render_glyph(langs['en'], cw, FULL_CH, tmp_dir, 'en-readme',
                                   sub_cols=2, sub_rows=2, char_fn=g._quadrant_char)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # Boxed snugly to 'en's own width here, deliberately not the shared
    # width used across the real (multi-language) ascii/ tier -- this
    # is a standalone README illustration, not part of that shared-
    # width set, so there's no reason to carry hr's much longer word's
    # padding into it.
    content_w = max(len(line) for line in en_lines)
    box = g.box_centered(en_lines, FULL_MARGIN, content_w).split('\n')
    inner_w = len(box[0]) - 2
    extra = inner_w - len(LABEL)
    left, right = extra // 2, extra - extra // 2
    label_line = '│' + ' ' * left + LABEL + ' ' * right + '│'
    # Put the label in the middle of the bottom margin block: box rows
    # are [border, margin blanks, ch content rows, margin blanks, border].
    box[1 + FULL_MARGIN + FULL_CH + FULL_MARGIN // 2] = label_line
    new_block = '\n'.join(box)

    with open(README_PATH, encoding='utf-8') as f:
        readme = f.read()
    new_readme = re.sub(r'```\n╭.*?╯\n```', f'```\n{new_block}\n```', readme, count=1, flags=re.DOTALL)
    if new_readme == readme:
        sys.exit("render_readme_preview.py: couldn't find the existing banner code block in README.md to replace")
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(new_readme)
    print(f"Updated {README_PATH} ({inner_w + 2} columns wide)")


if __name__ == '__main__':
    main()
