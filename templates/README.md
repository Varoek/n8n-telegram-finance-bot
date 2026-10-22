# Sheet templates

Import each CSV into the matching tab of your Google Sheet (File, Import, "Replace current sheet"):

- `transactions-headers.csv` into a tab named exactly `transactions`
- `reports-headers.csv` into a tab named exactly `reports`

Afterwards format these columns as **Plain text** (Format, Number, Plain text), otherwise Google Sheets converts
dates to serial numbers and long reference numbers to scientific notation:

- `transactions`: `created_at`, `txn_date`, `ref_no`, `edited_at`, `void_at`
- `reports`: `cycle_id`, `start`, `end`, `sent_at`
