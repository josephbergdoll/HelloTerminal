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
# Available codes: en de fr es da it sv nl fi ro sk
# Unset it, or leave it unset, to use all of them.

# Resolve this file's own directory at source-time. Using $0 inside
# the function below would instead resolve to the CALLER's $0 when
# the function runs, so it has to be captured here, at the top level,
# while ${(%):-%x} still refers to this file.
typeset -g HELLO_BANNER_DIR="${${(%):-%x}:A:h}/ascii"

# All languages this repo ships art for. Also doubles as the allowlist
# used to sanity-check a user-supplied HELLO_BANNER_LANGS below.
typeset -ga _HELLO_BANNER_ALL_LANGS=(en de fr es da it sv nl fi ro sk)

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
  [ -z "$cols" ] && return

  local -a langs=("${HELLO_BANNER_LANGS[@]}")
  local lang=${langs[$((RANDOM % ${#langs[@]} + 1))]}

  if [ "$cols" -ge 67 ] && [ -f "$dir/hello-$lang-ascii.txt" ]; then
    cat "$dir/hello-$lang-ascii.txt"
  elif [ "$cols" -ge 44 ] && [ -f "$dir/hello-$lang-ascii-compact.txt" ]; then
    cat "$dir/hello-$lang-ascii-compact.txt"
  elif [ "$cols" -ge 32 ] && [ -f "$dir/hello-$lang-ascii-mini.txt" ]; then
    cat "$dir/hello-$lang-ascii-mini.txt"
  else
    case "$lang" in
      de) echo "hallo." ;;
      fr) echo "bonjour." ;;
      es) echo "hola." ;;
      da) echo "hej." ;;
      it) echo "ciao." ;;
      sv) echo "hej." ;;
      nl) echo "hallo." ;;
      fi) echo "hei." ;;
      ro) echo "salut." ;;
      sk) echo "ahoj." ;;
      *)  echo "hello." ;;
    esac
  fi
}

hello_banner
