```
╭──────────────────────────────────────────────────────────────────╮
│                                                                  │
│                                                                  │
│                                                                  │
│                                                                  │
│                                                                  │
│                    ▗▛█        ▟▜▖ ▟▜▌                            │
│                    ▐▘▟       ▗▌▐▌ ▛▗▌                            │
│                    ▟ █       ▐▌▐▌▐▌▐▌                            │
│                    █▗▌       ▐ ▟ ▐▘▐▘                            │
│                    █▟▄   ▟▄  ▟ ▛ ▐ █  ▗▄▖ ▗                      │
│                    █▛▜▌ ▐▌▐▖ █▐▌ ▐▗▌ ▗▛▝▜▙▟                      │
│                   ▗█ ▗▌ ▟ ▐▘ ██  █▟  ▟  ▐▛▘                      │
│                  ▗█▌ ▐▌ █ █  █▘  ▐▌  █  ▐▌                       │
│                  ▛▐▌ ▐▘ ▐▟▘ ▗█  ▗█▖ ▐█  ▟                        │
│                   ▐▌ ▝▙▄██▄▟▛▝▙▄█▀▙▄▛▐▙▟▛   ██                   │
│                                                                  │
│                                                                  │
│                        HelloTerminal.                            │
│                                                                  │
│                                                                  │
╰──────────────────────────────────────────────────────────────────╯
```

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
