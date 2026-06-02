#!/usr/bin/env bash
# agent-session-briefing — Stop-hook validator (WARN mode).
#
# No-op unless a hub SESSION_BRIEFING.md has uncommitted changes; then runs
# `briefing.py check` and warns on failure WITHOUT blocking the turn.
#
# Register in settings.json under hooks.Stop:
#   { "hooks": [ { "type": "command",
#     "command": "$HOME/.claude/skills/agent-session-briefing/scripts/stop-validate.sh" } ] }
#
# To turn warnings into a hard gate (block the turn until the briefing validates),
# change the final `exit 1` to `exit 2`.

HUB="${SESSION_BRIEFING_HUB:-$HOME/.session-briefings}"
CHECK="${SESSION_BRIEFING_CHECK:-$(dirname "$0")/briefing.py}"   # briefing.py sits beside this hook

command -v python3 >/dev/null 2>&1 || exit 0    # no python      -> fail safe, silent
[ -d "$HUB/.git" ] || exit 0                     # hub not set up -> nothing to do

dirty=$(git -C "$HUB" status --porcelain 2>/dev/null | grep 'SESSION_BRIEFING\.md$' | cut -c4- || true)
[ -n "$dirty" ] || exit 0                         # no changed briefings -> silent no-op

fail=0
while IFS= read -r rel; do
  [ -n "$rel" ] || continue
  if ! out=$(python3 "$CHECK" check "$HUB/$rel" 2>&1); then
    printf 'session-briefing: %s failed validation\n%s\n' "$rel" "$out" >&2
    fail=1
  fi
done <<< "$dirty"

[ "$fail" -eq 0 ] && exit 0
exit 1   # WARN: shown to you, turn proceeds.
         # change to `exit 2` to BLOCK the turn until the briefing validates.
