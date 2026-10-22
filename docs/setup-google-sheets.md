# Google Sheets with a service account

A service account is a robot Google user. Its key does not expire, unlike an OAuth app left in "Testing" mode (7 days).

1. Google Cloud Console: new project `finance-bot`, enable **Google Sheets API**.
2. IAM and Admin, Service Accounts: create `n8n-finance`, skip the roles. Keys, Add key, JSON. Store the file privately.
3. Create the spreadsheet; name the tabs exactly `transactions` and `reports`.
4. Import the header rows from [`templates/`](../templates/README.md) and format the listed columns as **Plain text**.
5. Share the sheet with the service-account email as **Editor**.
6. Copy the spreadsheet ID from the URL (between `/d/` and `/edit`) into the Config node. Do not retype it: `l`, `I` and `1` look alike.
7. In n8n create a **Google Service Account API** credential with the `client_email` and the `private_key`.

If the private key is rejected (`DECODER routines::unsupported`), replace the literal `\n` sequences by real line breaks, or create a new key.
Organizations that block service-account keys require a personal Google account for this project.
