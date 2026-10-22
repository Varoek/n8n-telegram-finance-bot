# n8n

## Container

Pin the version, set the timezone and map a host folder for images and backups. Do not change an existing `N8N_ENCRYPTION_KEY`.

```yaml
services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:2.42.4
    restart: unless-stopped
    environment:
      - TZ=Asia/Makassar
      - GENERIC_TIMEZONE=Asia/Makassar
      - WEBHOOK_URL=https://n8n.example.com/
      - N8N_PROXY_HOPS=1
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - N8N_RESTRICT_FILE_ACCESS_TO=/files
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=336
    volumes:
      - n8n_data:/home/node/.n8n
      - /srv/finance-bot:/files
```

```bash
sudo mkdir -p /srv/finance-bot/images /srv/finance-bot/backups
sudo chown -R 1000:1000 /srv/finance-bot
docker compose up -d
```

## Tunnel

Expose **only** `webhook/*` publicly (Cloudflare Zero Trust, Tunnels, Public Hostnames: Path `webhook/*`). Keep the editor behind
Tailscale or Cloudflare Access. Check the webhook after publishing FIN-01:

```bash
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo" | jq
# expect: pending_update_count 0 and no last_error_message
```

## Credentials (Overview, Create credential)

| Type | Name | Fields |
|---|---|---|
| Telegram API | Telegram Finance Bot | Access Token |
| Header Auth | Anthropic API | Name `x-api-key`, Value = API key |
| Google Service Account API | Google Sheets Finance | `client_email`, `private_key` |

## Data tables

| Table | Columns |
|---|---|
| `fin_queue` | `update_id` number, `kind` string, `payload` string, `status` string (`pending`/`done`/`failed`), `attempts` number, `last_error` string |
| `fin_confirm` | `conf_id` string, `payload` string |
| `fin_errors` | `key` string, `last_sent` string |

## Config node

Copy [`config/config.example.json`](../config/config.example.json) into an **Edit Fields (Set)** node named `Config` (mode JSON, keep other input fields)
and fill in your values. Copy the node into every workflow.

## Heartbeat

Create a check on healthchecks.io (period 5 min, grace 5 min) and put its ping URL in the FIN-98 HTTP Request node.
