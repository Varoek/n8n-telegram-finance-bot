#!/usr/bin/env python3
"""Make an exported n8n workflow safe to publish.

Usage:
    python scripts/sanitize_workflow.py exports-raw/FIN-02.json -o workflows/FIN-02-process-txn.json
    python scripts/sanitize_workflow.py exports-raw/FIN-02.json -o out.json --map .sanitize-map.json

What it does
  * removes credential IDs/names, webhook IDs, instance ID, pinned data, workflow/project IDs and cached URLs
  * reads the Config node and replaces the real Telegram user IDs, group chat ID and spreadsheet ID everywhere
    (also when they were hard-coded in another node)
  * optional --map file: {"real value": "placeholder"} for anything else you want replaced
  * finally scans the result for API keys, bot tokens, private keys, service-account emails and ping URLs
    and refuses to write the file if it finds one (use --force only if you reviewed the finding)

Re-import notes: credentials, data tables and sub-workflow references show REPLACE_ME and must be re-selected
in n8n after import.
"""
import argparse
import copy
import json
import re
import sys
from pathlib import Path

DUMMY_USER_IDS = ["111111111", "222222222", "333333333"]
DUMMY_ADMIN = "444444444"
DUMMY_GROUP = "-1001234567890"
DUMMY_GROUP_ABS = "1001234567890"
DUMMY_SHEET = "YOUR_SPREADSHEET_ID"

PATTERNS = {
    "Anthropic API key": r"sk-ant-[A-Za-z0-9_\-]{20,}",
    "Telegram bot token": r"\b\d{8,10}:[A-Za-z0-9_\-]{35}\b",
    "Private key block": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "Service account email": r"[A-Za-z0-9._-]+@[A-Za-z0-9-]+\.iam\.gserviceaccount\.com",
    "healthchecks ping URL": r"hc-ping\.com/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
}


def collect_secrets(wf, extra):
    """Map real value -> placeholder, using the Config node plus the optional map file."""
    m = {}
    for node in wf.get("nodes", []):
        if node.get("name") != "Config":
            continue
        raw = node.get("parameters", {}).get("jsonOutput")
        if not raw:
            continue
        try:
            cfg = json.loads(raw)
        except ValueError:
            continue
        for i, uid in enumerate(cfg.get("allowed_user_ids", [])):
            m[str(uid)] = DUMMY_USER_IDS[min(i, len(DUMMY_USER_IDS) - 1)]
        admin = cfg.get("admin_chat_id")
        if admin is not None and str(admin) not in m:
            m[str(admin)] = DUMMY_ADMIN
        gid = cfg.get("group_chat_id")
        if gid is not None:
            m[str(gid)] = DUMMY_GROUP
            m[str(abs(int(gid)))] = DUMMY_GROUP_ABS
        if cfg.get("spreadsheet_id"):
            m[cfg["spreadsheet_id"]] = DUMMY_SHEET
    m.update(extra)
    return m


def scrub_structure(wf):
    wf = copy.deepcopy(wf)
    wf["pinData"] = {}
    wf["meta"] = {}
    for key in ("id", "versionId", "activeVersionId", "shared", "tags", "staticData", "triggerCount",
                "homeProject", "createdAt", "updatedAt"):
        wf.pop(key, None)
    for node in wf.get("nodes", []):
        node.pop("webhookId", None)
        if "credentials" in node:
            node["credentials"] = {ctype: {"id": "REPLACE_ME", "name": ctype} for ctype in node["credentials"]}
        _walk(node.get("parameters", {}))
    return wf


def _walk(obj):
    if isinstance(obj, dict):
        obj.pop("cachedResultUrl", None)
        for key in ("dataTableId", "workflowId"):
            ref = obj.get(key)
            if isinstance(ref, dict) and "value" in ref:
                ref["value"] = "REPLACE_ME"
        for v in obj.values():
            _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v)


def find_leaks(text):
    leaks = []
    for label, rx in PATTERNS.items():
        for match in re.finditer(rx, text):
            value = match.group(0)
            if "your-" in value.lower() or "example" in value.lower():
                continue
            leaks.append((label, value[:12] + "..."))
    return leaks


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--map", help="JSON file {real value: placeholder} (keep it git-ignored)")
    ap.add_argument("--force", action="store_true", help="write even if the final scan found something")
    args = ap.parse_args()

    wf = json.loads(Path(args.input).read_text(encoding="utf-8"))
    extra = json.loads(Path(args.map).read_text(encoding="utf-8")) if args.map else {}

    secrets = collect_secrets(wf, extra)
    wf = scrub_structure(wf)
    text = json.dumps(wf, indent=2, ensure_ascii=False)

    replaced = 0
    for real in sorted(secrets, key=len, reverse=True):
        if real and real in text:
            text = text.replace(real, secrets[real])
            replaced += 1

    try:
        json.loads(text)
    except ValueError as exc:
        sys.exit("Result is not valid JSON after replacement: %s" % exc)

    leaks = find_leaks(text)
    if leaks and not args.force:
        for label, preview in leaks:
            print("LEAK FOUND: %s (%s)" % (label, preview), file=sys.stderr)
        sys.exit("Refusing to write %s. Add the value to --map or review the workflow." % args.output)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text + "\n", encoding="utf-8")
    print("Wrote %s (%d secret values replaced, %d nodes)." % (out, replaced, len(wf.get("nodes", []))))


if __name__ == "__main__":
    main()
