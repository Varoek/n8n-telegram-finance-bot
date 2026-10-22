# Workflow notes

Node names matter: expressions refer to nodes by name (for example `$('Format Reply')`). The sanitized exports in
[`workflows/`](../workflows/README.md) are the source of truth; this page explains how they fit together.

## FIN-01 Ingest

`Telegram Trigger` (message + callback_query) -> `Config` -> `Normalize` (Code) -> `Is Whitelisted?` -> `Route Kind` (Switch: callback / command / image / text)

- **image / text**: `Check Queue` -> `Is New?` -> `Insert Queue Row` (write-ahead) -> `Prep Call` -> `Run Process Txn` (FIN-02)
- **command**: `Route Command` (Switch on the first word) -> `/undo`, `/edit`, `/last`, `/summary` (calls FIN-04), `/help`
- **callback**: `Parse Callback` -> `Answer Callback` + `Route Callback` (`u` undo, `m` category menu, `c` set category, `y`/`n` confirm or cancel)

Callback data format (max 64 bytes): `u|<id>`, `m|<id>`, `c|<id>|<index>`, `y|<id>`, `n|<id>`.

## FIN-02 Process Txn (about 34 nodes)

1. `Start` -> `Config` -> `Confirmed?` (true: skip Claude) -> `Set Model` -> `Is Image?` -> `Get Image` (+ `Save Image`) -> `Build Request`
2. `Call Claude` (HTTP, retries, error output) -> `Parse and Validate` -> `OK?`
3. Not OK: `Can Escalate?` -> `Switch to Sonnet` (loops back to `Set Model`) or `Prepare Confirm` -> `Is Readable?` -> `Save Confirm` + `Ask Confirm` / `Say Unreadable` -> `Mark Done (confirm)`
4. OK: `Entry` -> `Find Duplicate` -> `Merge Dup Result` -> `Is Duplicate?` -> `Append row` -> `Restore Context` -> `Format Reply` -> `Mark Done` -> `Send Reply`
5. Errors (Get Image, Call Claude, Append row error outputs): `Bump Attempts` -> `Notify Queued?` -> `Queued Notice` -> `Alert Admin`

## FIN-03 Retry Queue

`Schedule (15 min)` -> `Config` -> two branches:

- retry: `Get Pending` (**All conditions**: status = pending AND attempts < 5) -> `Filter Old` (older than 3 minutes) -> `Loop Over Items` -> `Parse Payload` -> `Run Process Txn`; error output -> `Bump Attempts`
- alert: `Find Stuck` (**All conditions**: pending AND attempts > 4) -> `Mark Failed` -> admin alert

## FIN-04 Report

Triggers: `Schedule Daily` (07:00) and `Start` (from `/summary`). `Cycle` computes the 26th-to-25th window; for the scheduled run it only
continues when the `reports` tab has no row for that cycle (so a missed day is caught up). `Aggregate` does all arithmetic in code;
`Call Commentary` asks Haiku for a short comment on the aggregated JSON (on error the report is sent without it).

## FIN-98 Heartbeat and FIN-99 Error Handler

FIN-98 pings healthchecks.io every 5 minutes. FIN-99 is set as the **Error workflow** of all other workflows; it formats the error,
suppresses repeats of the same node within 30 minutes (`fin_errors`), and sends a Telegram message to the admin.
Handled errors (error outputs) do not trigger the error workflow, which is why FIN-02 sends its own admin alert.

## Settings that are easy to get wrong

- Data table / Google Sheets "Always Output Data" where a no-match result must not stop the chain
- Filter **Must Match = All conditions** whenever there is more than one filter
- Inline keyboard buttons: label in **Text**, value in **Additional Fields, Callback Data**
- Telegram nodes: **Append n8n Attribution = OFF**
- Switch / IF: the compared value goes in the right-hand `value2` box; the operator is only `is equal to`
- Publish sub-workflows (FIN-02, FIN-04) again after every edit
