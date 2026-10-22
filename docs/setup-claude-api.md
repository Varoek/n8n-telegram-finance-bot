# Claude API

1. Create an account in the Anthropic Console (API billing is separate from a claude.ai subscription).
2. Add a small prepaid credit and set a **monthly spend limit** (for example $5).
3. Create an API key named `n8n-finance`. It is shown once; store it in a password manager.
4. Test it:

```bash
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-haiku-5-5","max_tokens":100,"messages":[{"role":"user","content":"Reply with the word OK"}]}'
```

Notes

- Models: `claude-haiku-5-5` (default), `claude-sonnet-5-5` (fallback).
- Do not send `temperature`, `top_p`, `top_k` or an assistant prefill to Haiku 5.5.
- Image limit: 5 MB per image. Telegram photos are JPEG; files sent as "document" can be larger.
- In n8n the key lives in a **Header Auth** credential: Name `x-api-key`, Value the key (no quotes, no `Bearer`).
- If a key is ever pasted into a chat, ticket or commit: delete it in the Console and create a new one.
