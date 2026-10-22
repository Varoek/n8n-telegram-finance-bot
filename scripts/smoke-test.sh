#!/usr/bin/env bash
# Quick API checks for your own keys. Reads values from a local .env (git-ignored).
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || { echo "Copy .env.example to .env and fill it in first."; exit 1; }
set -a; . ./.env; set +a

echo "== Telegram: getMe"
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | jq '{ok, username: .result.username}'

echo "== Telegram: webhook status"
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo" \
  | jq '{pending: .result.pending_update_count, last_error: .result.last_error_message}'

echo "== Claude API (Haiku)"
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: ${ANTHROPIC_API_KEY}" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-haiku-5-5","max_tokens":20,"messages":[{"role":"user","content":"Reply with OK"}]}' \
  | jq -r '(.content[]? | select(.type=="text") | .text) // .error.message'
