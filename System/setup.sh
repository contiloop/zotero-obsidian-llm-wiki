#!/bin/bash
# Rebuild this vault's setup on a machine. Safe to run again at any time.
#
#   System/setup.sh            everything below, in order
#   System/setup.sh base       tools check, ZotLit plugin files, local-only files
#   System/setup.sh telegram   .env for the Telegram bot, token check
#   System/setup.sh schedule   launchd job that fetches Telegram every 6 hours
#   System/setup.sh check      report what works and what is still missing
#   System/setup.sh unschedule remove the launchd job
#
# Steps a person must do by hand (the script lists them at the end):
# open the vault in Obsidian, install the two Zotero plugins, create the bot with @BotFather,
# allow Full Disk Access for Python when the vault is inside ~/Documents.

set -u
VAULT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$VAULT" || exit 1

ZOTLIT_VERSION="2.1.4"
ZOTLIT_DIR=".obsidian/plugins/zotlit"
ZOTLIT_URL="https://github.com/aidenlx/zotlit/releases/download/$ZOTLIT_VERSION"
ENV_FILE="System/Telegram/.env"
LABEL="com.jebi.telegram-ingest"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG="$VAULT/System/.cache/telegram/ingest.log"
# The .app inside Apple's command line tools: macOS can grant it Full Disk Access (a python3 symlink cannot).
PY_APP="/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app"
PY_BIN="$PY_APP/Contents/MacOS/Python"

ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
fail() { printf '  \033[31m✗\033[0m %s\n' "$*"; }
head1(){ printf '\n\033[1m%s\033[0m\n' "$*"; }
TODO=()
todo() { TODO+=("$*"); }
is_tty() { [ -t 0 ] && [ -t 1 ]; }

# ------------------------------------------------------------------ base
do_base() {
  head1 "Tools"
  for t in git python3 curl; do
    if command -v "$t" >/dev/null 2>&1; then ok "$t: $(command -v "$t")"; else fail "$t not found"; return 1; fi
  done
  if [ ! -x "$PY_BIN" ]; then
    warn "Apple command line tools Python not found at $PY_APP (needed only for the schedule). Install with: xcode-select --install"
  fi

  head1 "ZotLit plugin files ($ZOTLIT_VERSION)"
  mkdir -p "$ZOTLIT_DIR"
  local have=""
  [ -f "$ZOTLIT_DIR/manifest.json" ] && have="$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$ZOTLIT_DIR/manifest.json")"
  if [ -f "$ZOTLIT_DIR/main.js" ] && [ -f "$ZOTLIT_DIR/styles.css" ] && [ "$have" = "$ZOTLIT_VERSION" ]; then
    ok "already installed"
  else
    for f in main.js styles.css; do
      if curl -fsSL "$ZOTLIT_URL/$f" -o "$ZOTLIT_DIR/$f.tmp"; then mv "$ZOTLIT_DIR/$f.tmp" "$ZOTLIT_DIR/$f"; ok "downloaded $f"
      else rm -f "$ZOTLIT_DIR/$f.tmp"; fail "could not download $f from $ZOTLIT_URL"; fi
    done
  fi
  todo "Obsidian: File → Open folder as vault → $VAULT. Settings → Community plugins → turn off Restricted mode. ZotLit is then enabled; point it to your Zotero data folder if it is not ~/Zotero."
  todo "Zotero: install Better BibTeX and ZotLit Companion (Tools → Plugins → Install Plugin From File), plus the browser connector. See System/SETUP.md §Zotero."

  head1 "Local-only files"
  mkdir -p References/Zotero References/Telegram Wiki Writing/Drafts Writing/Published Assets/Telegram System/.cache/telegram
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git update-index --skip-worktree Wiki/Index.md System/ingest-log.md 2>/dev/null && ok "Wiki/Index.md and System/ingest-log.md: local changes stay out of git"
  else
    warn "not a git checkout; skipped skip-worktree"
  fi
}

# ------------------------------------------------------------------ telegram
env_get() { sed -n "s/^$1=//p" "$ENV_FILE" 2>/dev/null | head -1 | tr -d '"'"'" ; }
env_set() {  # key value
  if grep -q "^$1=" "$ENV_FILE"; then
    local tmp; tmp="$(mktemp)"; sed "s|^$1=.*|$1=$2|" "$ENV_FILE" > "$tmp" && mv "$tmp" "$ENV_FILE"
  else printf '%s=%s\n' "$1" "$2" >> "$ENV_FILE"; fi
}

do_telegram() {
  head1 "Telegram bot"
  [ -f "$ENV_FILE" ] || { cp System/Telegram/.env.example "$ENV_FILE"; ok "created $ENV_FILE"; }
  local token; token="$(env_get TELEGRAM_BOT_TOKEN)"
  if [ -z "$token" ] || [[ "$token" == *replace-with* ]]; then
    if is_tty; then
      echo "  In Telegram, message @BotFather, send /newbot, then paste the token here (Enter to skip)."
      printf '  token: '; read -r token
      if [ -n "$token" ]; then env_set TELEGRAM_BOT_TOKEN "$token"; ok "token saved"; fi
    fi
  fi
  token="$(env_get TELEGRAM_BOT_TOKEN)"
  if [ -z "$token" ] || [[ "$token" == *replace-with* ]]; then
    todo "Telegram: create a bot with @BotFather (/newbot) and put the token in $ENV_FILE, then run: System/setup.sh telegram"
    return 0
  fi
  if python3 System/Telegram/ingest.py --whoami 2>&1 | sed 's/^/  /'; then
    ok "token works. Open the chat with the bot in Telegram and press Start."
  else
    fail "token rejected; fix TELEGRAM_BOT_TOKEN in $ENV_FILE"; return 1
  fi
  if [ -z "$(env_get TELEGRAM_ALLOWED_USER_IDS)" ]; then
    if is_tty; then
      echo "  Your Telegram user id keeps strangers out of the bot (forward any message to @userinfobot to see it; Enter to skip)."
      printf '  user id: '; read -r uid
      if [ -n "$uid" ]; then env_set TELEGRAM_ALLOWED_USER_IDS "$uid"; ok "allowed user set"; fi
    fi
    [ -z "$(env_get TELEGRAM_ALLOWED_USER_IDS)" ] && todo "Telegram: set TELEGRAM_ALLOWED_USER_IDS in $ENV_FILE so only you can feed the bot (your id: forward a message to @userinfobot)."
  fi
  return 0
}

# ------------------------------------------------------------------ schedule
do_schedule() {
  head1 "Schedule (launchd, every 6 hours)"
  if [ "$(uname)" != "Darwin" ]; then warn "launchd exists only on macOS; run System/Telegram/ingest.py from your own scheduler"; return 0; fi
  if [ ! -x "$PY_BIN" ]; then fail "Python.app not found at $PY_APP. Run: xcode-select --install"; return 1; fi
  mkdir -p "$HOME/Library/LaunchAgents" "$(dirname "$LOG")"
  sed -e "s#/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python#$PY_BIN#" \
      -e "s#/Users/YOU/path/to/vault#$VAULT#g" System/Telegram/$LABEL.plist.example > "$PLIST"
  plutil -lint "$PLIST" >/dev/null || { fail "bad plist"; return 1; }
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null
  launchctl bootstrap "gui/$(id -u)" "$PLIST" || { fail "launchctl bootstrap failed"; return 1; }
  ok "installed $PLIST"
  : > "$LOG"
  launchctl kickstart -k "gui/$(id -u)/$LABEL"; sleep 4
  if grep -q "Operation not permitted" "$LOG" 2>/dev/null; then
    fail "macOS blocks background access to this folder (it is under ~/Documents, ~/Desktop or ~/Downloads)."
    todo "macOS: System Settings → Privacy & Security → Full Disk Access → + → press ⌘⇧G, paste  $(dirname "$PY_APP")/  → select Python.app → Open. Then run: System/setup.sh schedule"
  elif [ -s "$LOG" ]; then
    ok "first run: $(tail -1 "$LOG")"
  else
    warn "no output yet; check $LOG later"
  fi
}

do_unschedule() {
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null; rm -f "$PLIST"; ok "schedule removed"
}

# ------------------------------------------------------------------ check
do_check() {
  head1 "Check"
  [ -f "$ZOTLIT_DIR/main.js" ] && [ -f "$ZOTLIT_DIR/styles.css" ] && ok "ZotLit plugin files present" || fail "ZotLit plugin files missing (run: System/setup.sh base)"
  [ -f "$HOME/Zotero/zotero.sqlite" ] && ok "Zotero data folder: ~/Zotero" || warn "~/Zotero/zotero.sqlite not found; set the Zotero data folder in ZotLit settings"
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    [ "$(git ls-files -v Wiki/Index.md | cut -c1)" = "S" ] && ok "Wiki/Index.md is skip-worktree" || warn "Wiki/Index.md not skip-worktree (run: System/setup.sh base)"
  fi
  if [ -f "$ENV_FILE" ] && [[ "$(env_get TELEGRAM_BOT_TOKEN)" != *replace-with* ]] && [ -n "$(env_get TELEGRAM_BOT_TOKEN)" ]; then
    python3 System/Telegram/ingest.py --whoami >/dev/null 2>&1 && ok "Telegram token works" || fail "Telegram token rejected"
    [ -n "$(env_get TELEGRAM_ALLOWED_USER_IDS)" ] && ok "Telegram sender restricted" || warn "TELEGRAM_ALLOWED_USER_IDS empty: anyone who finds the bot can add notes"
  else
    warn "Telegram not configured (run: System/setup.sh telegram)"
  fi
  if [ "$(uname)" = "Darwin" ]; then
    if [ -f "$PLIST" ] && ! grep -q "$VAULT/System/Telegram/ingest.py" "$PLIST"; then
      warn "schedule is installed for another vault ($(sed -n 's#.*<string>\(.*ingest.py\)</string>.*#\1#p' "$PLIST")); run: System/setup.sh schedule"
    elif launchctl print "gui/$(id -u)/$LABEL" >/dev/null 2>&1; then
      local code; code="$(launchctl print "gui/$(id -u)/$LABEL" | sed -n 's/.*last exit code = \([0-9-]*\).*/\1/p')"
      if tail -1 "$LOG" 2>/dev/null | grep -q "Operation not permitted"; then fail "schedule installed but blocked by macOS (see Full Disk Access step)"
      else ok "schedule loaded (last exit code ${code:-none}); last log line: $(tail -1 "$LOG" 2>/dev/null)"; fi
    else
      warn "schedule not installed (run: System/setup.sh schedule). Without it, run System/Telegram/ingest.py at least daily."
    fi
  fi
  python3 -m unittest discover -s System/Telegram/tests >/dev/null 2>&1 && ok "Telegram script tests pass" || fail "Telegram script tests fail"
}

# ------------------------------------------------------------------ main
cmd="${1:-all}"
case "$cmd" in
  base)       do_base ;;
  telegram)   do_telegram ;;
  schedule)   do_schedule ;;
  unschedule) do_unschedule ;;
  check)      do_check ;;
  all)        do_base && do_telegram && do_schedule; do_check ;;
  *) sed -n '2,13p' "$0"; exit 2 ;;
esac

if [ ${#TODO[@]} -gt 0 ]; then
  head1 "Still to do by hand"
  i=1; for t in "${TODO[@]}"; do printf '  %d. %s\n' "$i" "$t"; i=$((i+1)); done
fi
echo
