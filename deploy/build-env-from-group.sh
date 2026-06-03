#!/usr/bin/env bash
# Build /opt/pd-game/.env from group chat .env + game-specific keys.
# Usage (on server): sudo bash deploy/build-env-from-group.sh /opt/group_ai_chat_bot/.env /opt/pd-game/.env

set -euo pipefail

GROUP_ENV="${1:-/opt/group_ai_chat_bot/.env}"
OUT_ENV="${2:-/opt/pd-game/.env}"

if [[ ! -f "$GROUP_ENV" ]]; then
  echo "Missing group env: $GROUP_ENV" >&2
  exit 1
fi

get_var() {
  local key="$1"
  grep -E "^${key}=" "$GROUP_ENV" 2>/dev/null | tail -1 | cut -d= -f2- || true
}

OPENAI_API_KEY="$(get_var OPENAI_API_KEY)"
DEEPSEEK_API_KEY="$(get_var DEEPSEEK_API_KEY)"
SMTP_HOST="$(get_var SMTP_HOST)"
SMTP_PORT="$(get_var SMTP_PORT)"
SMTP_USER="$(get_var SMTP_USER)"
SMTP_PASSWORD="$(get_var SMTP_PASSWORD)"
SMTP_FROM="$(get_var SMTP_FROM)"

if [[ -z "$OPENAI_API_KEY" && -z "$DEEPSEEK_API_KEY" ]]; then
  echo "Need OPENAI_API_KEY or DEEPSEEK_API_KEY in $GROUP_ENV" >&2
  exit 1
fi

if [[ -f "$OUT_ENV" ]] && grep -q '^SECRET_KEY=' "$OUT_ENV"; then
  SECRET_KEY="$(grep -E '^SECRET_KEY=' "$OUT_ENV" | tail -1 | cut -d= -f2-)"
else
  SECRET_KEY="$(openssl rand -hex 32)"
fi

umask 077
cat > "$OUT_ENV" <<EOF
# Generated from $GROUP_ENV — $(date -u +%Y-%m-%dT%H:%M:%SZ)
OPENAI_API_KEY=${OPENAI_API_KEY}
DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}

SECRET_KEY=${SECRET_KEY}
APP_BASE_URL=https://game.xjhuang.com
APP_NAME=ACTR Lab — AI Games
PORT=5001
FLASK_DEBUG=false

LEGACY_ADMIN_USER=ACTR2026
LEGACY_ADMIN_PASSWORD=ACTR2026

SMTP_HOST=${SMTP_HOST:-smtp.gmail.com}
SMTP_PORT=${SMTP_PORT:-587}
SMTP_USER=${SMTP_USER}
SMTP_PASSWORD=${SMTP_PASSWORD}
SMTP_FROM=${SMTP_FROM:-${SMTP_USER}}
EOF

chown www-data:www-data "$OUT_ENV" 2>/dev/null || true
chmod 600 "$OUT_ENV"
echo "Wrote $OUT_ENV"
