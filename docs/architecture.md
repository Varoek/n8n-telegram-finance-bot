# Architecture

## System context

```mermaid
flowchart LR
  U["Telegram group<br/>(two people + bot)"] -->|photo / text| TG[Telegram Bot API]
  TG -->|webhook HTTPS| CF["Cloudflare Tunnel<br/>(only /webhook/* is public)"]
  CF --> N8N["n8n 2.x (Docker)"]
  N8N -->|image + prompt| CL["Claude API<br/>Haiku 5.5 / Sonnet 5.5"]
  N8N -->|append / update rows| GS[(Google Sheets<br/>service account)]
  N8N --> DT[(n8n Data Tables)]
  N8N --> SSD[("Local volume<br/>images + backups")]
  N8N -->|reply + buttons| TG
  N8N -. heartbeat .-> HC[healthchecks.io]
```

The home server is behind CGNAT and accepts **no inbound connections**: the Cloudflare tunnel is an outbound
connection, and Telegram delivers updates to a public hostname that the tunnel forwards to n8n.

## Workflow map

```mermaid
flowchart TD
  T[Telegram Trigger] --> F1["FIN-01 Ingest<br/>whitelist, route, queue, commands, callbacks"]
  F1 -->|photo / text| F2["FIN-02 Process Txn<br/>Claude, validate, Sheet, reply"]
  F1 -->|/summary| F4["FIN-04 Report"]
  S3["Schedule 15 min"] --> F3["FIN-03 Retry Queue"] --> F2
  S4["Schedule daily 07:00"] --> F4
  S98["Schedule 5 min"] --> F98["FIN-98 Heartbeat"]
  ERR["Any workflow error"] --> F99["FIN-99 Error Handler"]
```

## Processing a transaction (FIN-02)

```mermaid
flowchart TD
  A[Input: image or text + caption] --> B["Claude Haiku 5.5<br/>JSON only"]
  B --> C{"Valid and<br/>confidence >= 0.75?"}
  C -- yes --> D{Duplicate?}
  C -- no --> E["Retry once with Sonnet 5.5"]
  E --> C2{Valid?}
  C2 -- yes --> D
  C2 -- no --> H["Ask the humans:<br/>Yes / No buttons"]
  D -- yes --> I["Notice, mark queue row done"]
  D -- no --> F[Append row to Google Sheets]
  F --> G["Mark queue row done, reply with Undo / Category buttons"]
  B -. API error .-> Q["Queue row stays pending<br/>retried by FIN-03"]
  F -. Sheets error .-> Q
```

## Design decisions

| Decision | Reason |
|---|---|
| **Write-ahead queue** (Data Table) before any API call | A crash or outage cannot lose a message; FIN-03 re-runs pending rows |
| **Idempotency key** (`src_id` = Telegram update ID) checked before every append | Retries and Telegram redeliveries never create duplicate rows |
| **Soft delete** (`status = void`) | Audit trail; reports ignore void rows |
| **LLM never does arithmetic** | All sums and comparisons are done in Code nodes; the model only writes optional commentary |
| **Fixed category list + validation in code** | Consistent data even when the model improvises |
| **Haiku first, Sonnet on low confidence** | Cheapest model that is accurate enough, with a safety net |
| **Service account for Google** | No OAuth token that expires after 7 days |
| **Plain-text date and reference columns** | Google Sheets would otherwise convert them and break filters |
| **Only `/webhook/*` exposed** | The n8n editor stays private |
| **Whitelist by Telegram user ID** | Strangers who add the bot to a group are ignored |
| **Heartbeat to an external service** | An Error Trigger cannot fire when n8n itself is down |
| **Cycle report, not calendar month** | Matches the household's salary cycle (26th to 25th); a daily check catches a missed day |

## Failure behaviour

| What fails | What happens | How you find out | Recovery |
|---|---|---|---|
| Home internet / tunnel / VM / n8n down | Telegram holds updates and redelivers later | healthchecks.io alert | Automatic; dedupe prevents doubles |
| n8n crashes mid-processing | Queue row was written first, so it is still `pending` | No reply to that message | FIN-03 within 15 min |
| Claude API error / 429 / overload | HTTP node retries, then error output | Bot says "saved to queue" + admin alert | FIN-03 retries; after 5 attempts a permanent-failure alert |
| Model returns bad JSON or low confidence | Retry with Sonnet, then ask for confirmation | Yes/No buttons | Tap Yes or type the entry |
| Google Sheets or credential problem | Append fails, row stays `pending` | Queue notice + admin alert | Fix credential; FIN-03 re-runs |
| Same screenshot sent twice | Blocked by `src_id` and `ref_no` | "Already recorded" notice | Undo if it was not a duplicate |
| Wrong amount or category | Row exists | You notice in the reply | `/undo`, `/edit`, or buttons |
