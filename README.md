```
╭──────────────────────────────────────────────────────────────────╮
│                                                                  │
│                                                                  │
│                                                                  │
│                                                                  │
│                                                                  │
│           ▗█▀█▄                 ▟▛▜█▖   ▗█▀█▄                    │
│          ▗█▘ ▐█                ▟▛  █▌  ▐█▘ ▐█                    │
│          ▟▛ ▗█▘               ▐▛  ▐█   █▘  █▌                    │
│          █▌▄█▙▖      ▄▄▄▄     █▌ ▗█▘  ▐█  ▟▛    ▗▄▄▄▄▖   ▗▄      │
│         ▐██▛▀▀▜▙    ▟▛▘ ▜▙    █▘▄█▘   ▐▛ ▟▛    ▟▛▀  ▀██▙▟█▘      │
│       ▗▄██▘   ▐▛   ▐█  ▗█▌    ██▛     ▐▙█▀    ▟█     ▐█          │
│     ▟█▀▘█▛    █▌   ▝█▄▟▛▘   ▄▟█▙     ▄▟█▌    ▟██    ▗█▘          │
│         █▘    ▀█▙▄██▀▀█▄▄▄█▛▀  ▀█▙▄█▛▀ ▝▜▙▄█▛▀ ▀█▄▄█▛▘   ██      │
│                                                                  │
│                                                                  │
│                          HelloTerminal.                          │
│                                                                  │
│                                                                  │
╰──────────────────────────────────────────────────────────────────╯
```

Requires a terminal at least 123 columns wide to show the full banner
(narrower terminals fall back to smaller tiers, then plain text -- see
`hello-banner.zsh`). The preview above is rendered with universally-
supported block characters for GitHub's sake; the actual banner uses
Unicode sextant characters for extra detail, which need decent Unicode
symbol support in your terminal/font -- see "Font support" in
`utils/AGENTS.md` if it renders oddly.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A random-language "hello" banner for your terminal. Obviously inspired by Apple's welcome screens.

## Use

```sh
source /path/to/HelloTerminal/hello-banner.zsh
```

Add that line to your `~/.zshrc`. Works from wherever the repo is cloned.

## Configure

Restrict which languages can show up by setting `HELLO_BANNER_LANGS`
before the `source` line:

```sh
HELLO_BANNER_LANGS=(en fr es)
source /path/to/HelloTerminal/hello-banner.zsh
```

37 languages ship in `ascii/`. Leave it unset to use all of them.

See `HINTING.md` for how the art is hand-touched-up when a glyph
renders too small to read cleanly.
