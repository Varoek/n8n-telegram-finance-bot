# Workflows

Put your **sanitized** n8n exports here, one file per workflow:

```
FIN-01-ingest.json
FIN-02-process-txn.json
FIN-03-retry-queue.json
FIN-04-report.json
FIN-98-heartbeat.json
FIN-99-error-handler.json
```

## Export and sanitize

1. In n8n open the workflow, press **Ctrl+A**, **Ctrl+C**, paste into `exports-raw/<name>.json` (this folder is git-ignored).
2. Sanitize:

   ```
   python scripts/sanitize_workflow.py exports-raw/FIN-02.json -o workflows/FIN-02-process-txn.json
   ```

   The script reads your Config node and replaces user IDs, group chat ID and spreadsheet ID everywhere. If you
   have other private values (for example a healthchecks URL), create a git-ignored `.sanitize-map.json`:

   ```
   { "https://hc-ping.com/your-real-uuid": "https://hc-ping.com/YOUR-HEALTHCHECK-UUID" }
   ```

   and pass `--map .sanitize-map.json`.
3. Run `python scripts/check_secrets.py` (must print `OK`).

## Import into n8n

1. Create the 3 data tables first (`fin_queue`, `fin_confirm`, `fin_errors`, see [docs/setup-n8n.md](../docs/setup-n8n.md)).
2. Import FIN-99 and FIN-02 first (sub-workflows), then the rest, FIN-01 last.
3. After import, nodes show `REPLACE_ME` where an ID was removed. Re-select: the credentials on every Telegram,
   Google Sheets and HTTP Request node, the data table on every Data table node, and the target workflow on every
   Execute Workflow node.
4. Fill the **Config** node (copy from `config/config.example.json`) with your own values.
5. Set the **Error workflow** to FIN-99 on every workflow except FIN-99 itself, and the timezone to your own.
6. Publish FIN-99, FIN-98, FIN-02, FIN-04, FIN-03, and FIN-01 last. Publish sub-workflows again after every edit.
