# Telegram bot and group

## 1. Create the bot

1. In Telegram open **@BotFather** (blue tick) and press Start.
2. Send `/newbot`, choose a display name, then a username ending in `bot`.
3. BotFather returns a token like `123456789:AAH...`. Store it in a password manager. Anyone with the token controls the bot; never commit it.

## 2. Disable privacy mode (required for photos in groups)

`/setprivacy` then choose the bot, then **Disable**. Remove and re-add the bot to any group it joined earlier.

## 3. Command menu

`/setcommands`, choose the bot, send:

```
undo - Batalkan transaksi terakhir (atau /undo ID)
edit - Ubah transaksi: /edit ID kategori=... nominal=... catatan=...
last - 10 transaksi terakhir
summary - Ringkasan siklus: /summary, /summary lalu, /summary 2026-10
help - Bantuan
```

## 4. Group

Create a group with your partner, add the bot, press **Start** in a private chat with the bot (so it can DM you alerts).
Do not change group features before collecting the chat ID; an upgrade to a supergroup changes the ID.

## 5. Collect IDs

Run this **before** any n8n Telegram workflow is published (getUpdates does not work while a webhook is set), after
sending a message from each account in the group and privately to the bot:

```bash
export BOT_TOKEN='...'
curl -s "https://api.telegram.org/bot$BOT_TOKEN/deleteWebhook"
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getUpdates" \
  | jq '.result[] | select(.message) | .message | {chat_id: .chat.id, type: .chat.type, user_id: .from.id, name: .from.first_name}'
```

- group `chat_id` (negative number) becomes `group_chat_id`
- each `user_id` goes into `allowed_user_ids`
- the private chat id is `admin_chat_id`

Only the n8n Telegram credential and the `Config` node ever hold these values.
