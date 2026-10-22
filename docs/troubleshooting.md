# Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Bot does not react | Webhook not registered, tunnel path wrong, FIN-01 not published | `getWebhookInfo`; check `webhook/*` path; publish FIN-01 |
| Bot ignores photos in the group | Privacy mode on | BotFather `/setprivacy` Disable; remove and re-add the bot |
| Telegram 400 "can't parse entities" | Unescaped `<` or `&` in HTML mode | Use the `esc()` helper or drop Parse Mode for that node |
| Telegram 400 on inline keyboard | Button has no `callback_data` | Put the value in Additional Fields, Callback Data |
| Reply ends with "sent automatically with n8n" | Attribution on | Additional Fields, Append n8n Attribution = OFF |
| Claude 401 "x-api-key header is required" | No credential attached to the HTTP node | Authentication: Header Auth with the Anthropic credential |
| Claude 401 invalid key | Wrong key | Create a new key; test with curl first |
| Claude 400 "model: Field required" | `model` missing in the body (Set node assignment without a name) | Name the field `model` |
| Credential "does not exist for type httpHeaderAuth" | Node still points to a deleted credential | Create/select the credential again, save, reload the page |
| Claude 400 about temperature/top_p/prefill | Unsupported parameter for Haiku 5.5 | Remove it from the body |
| Sheets 404 "Requested entity was not found" | Wrong spreadsheet ID (look-alike characters) | Copy the ID from the URL; do not retype |
| Sheets "Sheet with name transactions not found" | Tab name differs | Name the tab exactly `transactions` |
| Sheets "No columns found" | Row 1 empty or wrong tab | Add header row, Retry |
| Dates become serial numbers | Column not plain text | Format as Plain text |
| Switch/IF never matches | Extra words pasted into the value box; value left empty | The right-hand box must contain only the value |
| Flow stops after a Data table update | Update matched no row, so no output | Always Output Data = ON |
| Same transaction notice every 15 minutes | Queue rows never become `done` (filter column unset) or Get Pending uses "Any condition" | Filter column `id` equals value; Must Match = All conditions |
| Edits to FIN-02 have no effect | Caller runs the published version | Publish FIN-02 again |
| No alerts although things fail | Handled errors do not trigger the error workflow | FIN-02 sends its own admin alerts; set the error workflow on every other workflow |
