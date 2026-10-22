# Security

## Never commit

| Item | Where it should live instead |
|---|---|
| Telegram bot token | n8n credential "Telegram API" |
| Anthropic API key | n8n credential "Header Auth" (name `x-api-key`) |
| Google service-account JSON key (`private_key`, `client_email`) | n8n credential "Google Service Account API" |
| Spreadsheet ID, Telegram user IDs, group chat ID | n8n `Config` node (replaced by placeholders on export) |
| healthchecks.io ping URL | the heartbeat workflow (replaced by a placeholder on export) |
| n8n encryption key (`N8N_ENCRYPTION_KEY`), `.env` files | your host, never in git |
| Raw workflow exports | `exports-raw/` (git-ignored); only sanitized copies go to `workflows/` |
| Screenshots showing IDs, names, amounts, URLs | blur before adding to `docs/screenshots/` |

## Publishing checklist

1. Export each workflow from n8n into `exports-raw/` (git-ignored).
2. Run `python scripts/sanitize_workflow.py exports-raw/<file>.json -o workflows/<name>.json`.
3. Run `python scripts/check_secrets.py`. It must print `OK`.
4. Open every screenshot and check: no chat IDs, no spreadsheet ID in the URL bar, no n8n **Config** node output
   (it shows user IDs and the spreadsheet ID), no real names or amounts.
5. Install the pre-commit hook: `cp scripts/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`.
6. Push. The GitHub Action repeats the scan.

## If a secret leaks anyway

1. **Revoke it immediately** (BotFather `/revoke`, Anthropic Console, Google Cloud service-account key).
2. Rotating is not enough if the secret is in git history: rewrite history (`git filter-repo`) or delete and recreate the repository.
3. Remember that forks and caches may keep copies, which is why revoking comes first.

## Runtime hardening used by the project

- Only whitelisted Telegram user IDs are processed; everyone else is ignored silently
- Only `/webhook/*` is exposed through the tunnel; the n8n editor stays private
- Anthropic spend limit set in the Console
- Error alerts never include images or full payloads
