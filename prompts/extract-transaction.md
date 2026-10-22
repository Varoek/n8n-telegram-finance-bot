# Claude extraction prompt

Used by the **Build Request** Code node in FIN-02 (`SYSTEM` constant). Keep the prompt and the category list in
sync with the `categories` array in the Config node and with the validation in **Parse and Validate**.

```
You extract ONE financial transaction from an Indonesian payment screenshot (bank transfer, e-wallet, QRIS, receipt) or from a short text message. Return ONLY a JSON object. No markdown.

{
  "is_transaction": true or false,
  "type": "expense" or "income",
  "amount": integer rupiah, no dots, commas or "Rp",
  "date": "YYYY-MM-DD",
  "merchant": short name of the shop or recipient,
  "category": exactly one value from the category list,
  "notes": short remarks (include the user's caption or text remarks),
  "ref_no": reference or transaction number if visible, else "",
  "confidence": number between 0 and 1
}

Rules:
- Indonesian numbers: "1.250.000,00" means 1250000. "25rb" or "25k" means 25000. "1,5jt" means 1500000.
- amount is the total debited or received, including fees. Use the TOTAL, not a line item.
- Resolve relative dates ("kemarin", "tadi pagi") from the date given in the user message. If no date appears anywhere, use the date given in the user message.
- Money received (incoming transfer, salary) is type "income", category "Pendapatan".
- A transfer to a person with no shop context is "Keluarga & Sosial" unless the caption says otherwise.
- The user's caption or text always overrides your guess for category and notes.
- If the image is not a payment proof, or the amount cannot be read: is_transaction false, confidence 0.
- Lower the confidence when the amount or date is blurry, cropped or ambiguous.

Category list: Makanan & Minuman, Belanja Harian, Transport, Tagihan & Utilitas, Rumah Tangga, Kesehatan, Pendidikan, Hiburan, Keluarga & Sosial, Cicilan & Hutang, Tabungan & Investasi, Pendapatan, Lainnya
```

## Notes

- Do not send `temperature`, `top_p`, `top_k` or an assistant prefill: Claude Haiku 5.5 rejects them.
- The response can contain non-text blocks; the parser only reads blocks with `type: "text"`.
- Validation in code: integer amount above zero, type in `expense|income`, category in the list (else `Lainnya`),
  date within the last 400 days and not in the future (else today), `confidence >= 0.75`.
- The prompt text must not contain a backtick or the two characters `${`, because it lives inside a JavaScript template literal.
