# Testing

Test each workflow separately with pinned data, then test FIN-01 last with real Telegram messages.

## Functional tests (in the real group)

| # | Action | Expected |
|---|---|---|
| 1 | Send `kopi 25rb` | Reply with amount, category, ID and two buttons; one new `ok` row |
| 2 | Send a transfer screenshot | Correct amount, date, merchant; image saved on the volume |
| 3 | Send a QRIS screenshot with a caption | Caption in `notes`; sensible category |
| 4 | Tap Undo | Row becomes `void` |
| 5 | Tap Change category and pick one | Category updated, `edited_at` filled |
| 6 | `/edit ID nominal=30000 catatan=tes` | Fields updated |
| 7 | `/last`, `/undo` | List of 10; own last entry voided |
| 8 | Blurry or non-payment photo | Sonnet retry, Yes/No buttons, or "cannot read" |
| 9 | Same screenshot twice | "Already recorded" |
| 10 | Message from the second person | `who` shows that person |
| 11 | `/summary`, `/summary lalu` | Totals match a manual SUMIFS in the sheet |
| 12 | Message from a stranger | No reply, no row |

## Failure drills

| Drill | How | Expected |
|---|---|---|
| Server down | stop the n8n container, send a photo and a text, start it again | both recorded exactly once |
| Claude unreachable | block `api.anthropic.com` temporarily, send a photo | "saved to queue" + admin alert; recovers within 15 min |
| Sheets unreachable | remove the service account from the sheet, send a text | same; recovers after access is restored |
| Permanent failure | keep Claude blocked for about 90 minutes | alert after 5 attempts; status `failed` |
| Heartbeat | stop n8n for 12 minutes | healthchecks.io alert |

Accuracy test: send 20 to 30 real screenshots from your own banks and e-wallets; the amount should be correct on at least 98%.
If not, compare Haiku and Sonnet on the failures and change `model_default` in the Config node.

Use a **new `update_id` for every pinned test**; a repeated one is (correctly) reported as a duplicate.
