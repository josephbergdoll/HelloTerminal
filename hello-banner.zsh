# hello-banner.zsh
#
# Prints a random-language "hello" banner, rendered in Unicode block
# elements from cursive SVG wordmarks, sized to fit the current
# terminal width. Falls back to plain text on very narrow terminals.
#
# Usage: source this file from your shell startup file, e.g. in
# ~/.zshrc:
#
#   source /path/to/HelloTerminal/hello-banner.zsh
#
# It works no matter where the repo is cloned to -- it locates its
# own ascii/ directory relative to this file, not a hardcoded path.
#
# Configuration: to limit which languages can show up (picked at
# random each time), set HELLO_BANNER_LANGS *before* the source line,
# as either a zsh array or a comma/space-separated string:
#
#   HELLO_BANNER_LANGS=(en fr es)
#   source /path/to/HelloTerminal/hello-banner.zsh
#
#   HELLO_BANNER_LANGS="en, fr, es"
#   source /path/to/HelloTerminal/hello-banner.zsh
#
# Available codes: en de fr es da it sv nl fi ro sk ar bg ca cs el he
# hi hr hu id ja kk ko ms nb pl pt pt_BR ru th tr uk vi zh_HK zh-Hans
# zh-Hant
# Unset it, or leave it unset, to use all of them.
#
# Live resize: while you're still at the very first prompt, resizing
# the terminal window redraws the banner in place at the new size.
# This stops the moment you run your first command.

# Resolve this file's own directory at source-time. Using $0 inside
# the function below would instead resolve to the CALLER's $0 when
# the function runs, so it has to be captured here, at the top level,
# while ${(%):-%x} still refers to this file.
typeset -g HELLO_BANNER_DIR="${${(%):-%x}:A:h}/ascii"

# All languages this repo ships art for. Also doubles as the allowlist
# used to sanity-check a user-supplied HELLO_BANNER_LANGS below.
typeset -ga _HELLO_BANNER_ALL_LANGS=(
  en de fr es da it sv nl fi ro sk
  ar bg ca cs el he hi hr hu id ja kk ko ms nb pl pt pt_BR ru th tr uk
  vi zh_HK zh-Hans zh-Hant
)

if (( ! ${+HELLO_BANNER_LANGS} )); then
  HELLO_BANNER_LANGS=("${_HELLO_BANNER_ALL_LANGS[@]}")
elif [[ "${(t)HELLO_BANNER_LANGS}" != array* ]]; then
  # Accept a plain string too, e.g. "en,fr,es" or "en fr es".
  HELLO_BANNER_LANGS=(${=${HELLO_BANNER_LANGS//,/ }})
fi

# Drop anything that isn't actually a language we have art for (a typo
# shouldn't silently mean the banner never renders again).
typeset -ga _HELLO_BANNER_VALID_LANGS=()
for _hb_lang in "${HELLO_BANNER_LANGS[@]}"; do
  if (( ${_HELLO_BANNER_ALL_LANGS[(Ie)$_hb_lang]} )); then
    _HELLO_BANNER_VALID_LANGS+=("$_hb_lang")
  else
    print -u2 "hello-banner.zsh: ignoring unknown HELLO_BANNER_LANGS entry '$_hb_lang'"
  fi
done
unset _hb_lang
if (( ${#_HELLO_BANNER_VALID_LANGS} == 0 )); then
  _HELLO_BANNER_VALID_LANGS=("${_HELLO_BANNER_ALL_LANGS[@]}")
fi
HELLO_BANNER_LANGS=("${_HELLO_BANNER_VALID_LANGS[@]}")

hello_banner() {
  local dir="$HELLO_BANNER_DIR"
  local cols=${COLUMNS:-$(tput cols 2>/dev/null)}
  typeset -g _HELLO_BANNER_LINES=0
  [ -z "$cols" ] && return

  local -a langs=("${HELLO_BANNER_LANGS[@]}")
  local lang=${langs[$((RANDOM % ${#langs[@]} + 1))]}
  local output=''

  if [ "$cols" -ge 123 ] && [ -f "$dir/hello-$lang-ascii.txt" ]; then
    output="$(<"$dir/hello-$lang-ascii.txt")"
  elif [ "$cols" -ge 98 ] && [ -f "$dir/hello-$lang-ascii-compact.txt" ]; then
    output="$(<"$dir/hello-$lang-ascii-compact.txt")"
  elif [ "$cols" -ge 64 ] && [ -f "$dir/hello-$lang-ascii-mini.txt" ]; then
    output="$(<"$dir/hello-$lang-ascii-mini.txt")"
  else
    case "$lang" in
      de)      output="hallo." ;;
      fr)      output="bonjour." ;;
      es)      output="hola." ;;
      da)      output="hej." ;;
      it)      output="ciao." ;;
      sv)      output="hej." ;;
      nl)      output="hallo." ;;
      fi)      output="hei." ;;
      ro)      output="salut." ;;
      sk)      output="ahoj." ;;
      ar)      output="مرحبا." ;;
      bg)      output="здравей." ;;
      ca)      output="hola." ;;
      cs)      output="ahoj." ;;
      el)      output="γεια." ;;
      he)      output="שלום." ;;
      hi)      output="नमस्ते." ;;
      hr)      output="bok." ;;
      hu)      output="szia." ;;
      id)      output="halo." ;;
      ja)      output="こんにちは。" ;;
      kk)      output="сәлем." ;;
      ko)      output="안녕하세요." ;;
      ms)      output="helo." ;;
      nb)      output="hei." ;;
      pl)      output="cześć." ;;
      pt|pt_BR) output="olá." ;;
      ru)      output="привет." ;;
      th)      output="สวัสดี." ;;
      tr)      output="merhaba." ;;
      uk)      output="привіт." ;;
      vi)      output="xin chào." ;;
      zh_HK|zh-Hans|zh-Hant) output="你好。" ;;
      *)       output="hello." ;;
    esac
  fi

  print -r -- "$output"
  _HELLO_BANNER_LINES=${#${(f)output}}
}

hello_banner

# --- Live resize -----------------------------------------------------
# While you're still at the very first prompt (before running any
# command), resizing the terminal window redraws the banner in place
# to fit the new size, debounced to a second after you stop dragging
# (dragging a window edge fires a burst of resize events, not just
# one). This detaches permanently the moment you run a command --
# redrawing after that could erase output that has nothing to do with
# the banner. It also backs off for that one resize if you've started
# typing something (so it never clobbers unsubmitted input), and never
# activates at all if something else in your config already defines
# TRAPWINCH.
if (( _HELLO_BANNER_LINES == 0 )); then
  : # nothing was shown, so there's nothing to live-resize
elif (( ${+functions[TRAPWINCH]} )); then
  print -u2 "hello-banner.zsh: not enabling live-resize -- TRAPWINCH is already defined elsewhere"
elif ! zmodload -i zsh/sched 2>/dev/null; then
  print -u2 "hello-banner.zsh: not enabling live-resize -- zsh/sched module unavailable"
else
  typeset -g _HELLO_BANNER_ARMED=1
  typeset -g _HELLO_BANNER_RESIZE_GEN=0

  # Every resize bumps the generation counter and (re)schedules a
  # redraw a second out, tagged with that generation. A redraw only
  # actually happens if its tag still matches the counter when it
  # fires -- if a newer resize came in first, this one's just stale
  # and skips itself, so a burst of events collapses into one redraw.
  TRAPWINCH() {
    (( ${+_HELLO_BANNER_ARMED} )) || return 0
    (( _HELLO_BANNER_RESIZE_GEN++ ))
    sched +1 _hello_banner_redraw $_HELLO_BANNER_RESIZE_GEN
    return 0
  }

  _hello_banner_redraw() {
    (( ${+_HELLO_BANNER_ARMED} )) || return 0
    (( $1 == _HELLO_BANNER_RESIZE_GEN )) || return 0
    [[ -z "$BUFFER" ]] || return 0
    # A plain "move cursor up N lines" doesn't work here: narrowing the
    # terminal reflows the previously-printed (wider) lines into more
    # physical rows than were originally printed, so N under-shoots and
    # leaves stale fragments on screen. A full clear sidesteps needing
    # to know how many physical rows the old banner currently occupies.
    print -n "\e[H\e[2J"
    hello_banner
    zle && zle reset-prompt
  }

  _hello_banner_disarm() {
    unset _HELLO_BANNER_ARMED
    add-zsh-hook -d preexec _hello_banner_disarm
  }
  autoload -Uz add-zsh-hook
  add-zsh-hook preexec _hello_banner_disarm
fi
