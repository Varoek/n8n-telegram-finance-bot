#!/usr/bin/env python3
"""Scan the repository for secrets before you commit or push. Exit code 1 if anything suspicious is found.

    python scripts/check_secrets.py

Also flags every key of a local, git-ignored .sanitize-map.json (your real values) if it appears anywhere.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "node_modules", "__pycache__", "exports-raw", "workflows-private"}
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".rar", ".pdf", ".ico"}
SKIP_FILES = {".sanitize-map.json"}

PATTERNS = {
    "Anthropic API key": r"sk-ant-[A-Za-z0-9_\-]{20,}",
    "Telegram bot token": r"\b\d{8,10}:[A-Za-z0-9_\-]{35}\b",
    "Private key block": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "Service account email": r"[A-Za-z0-9._-]+@[A-Za-z0-9-]+\.iam\.gserviceaccount\.com",
    "healthchecks ping URL": r"hc-ping\.com/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
    "Google Sheet ID in URL": r"/spreadsheets/d/[A-Za-z0-9_\-]{30,}",
}
ID_RX = re.compile(r'"(group_chat_id|admin_chat_id)"\s*:\s*(-?\d{9,})')
ALLOWED_IDS = {"111111111", "-1001234567890", "444444444"}


def iter_files():
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts) or p.suffix.lower() in SKIP_SUFFIX or p.name in SKIP_FILES:
            continue
        yield p


def main():
    problems = []
    real_values = []
    map_file = ROOT / ".sanitize-map.json"
    if map_file.exists():
        real_values = [k for k in json.loads(map_file.read_text(encoding="utf-8")) if len(k) >= 6]

    for p in iter_files():
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = p.relative_to(ROOT)
        for label, rx in PATTERNS.items():
            for m in re.finditer(rx, text):
                val = m.group(0)
                if "your-" in val.lower() or "example" in val.lower() or "YOUR_" in val:
                    continue
                problems.append("%s: %s (%s...)" % (rel, label, val[:12]))
        for m in ID_RX.finditer(text):
            if m.group(2) not in ALLOWED_IDS:
                problems.append("%s: %s looks like a real ID (%s)" % (rel, m.group(1), m.group(2)[:4] + "..."))
        for v in real_values:
            if v in text:
                problems.append("%s: contains a value from .sanitize-map.json (%s...)" % (rel, v[:4]))
        if p.suffix == ".json":
            try:
                json.loads(text)
            except ValueError as exc:
                problems.append("%s: invalid JSON (%s)" % (rel, exc))

    if problems:
        print("PROBLEMS FOUND:")
        for line in problems:
            print(" -", line)
        sys.exit(1)
    print("OK: no secrets found, all JSON files valid.")


if __name__ == "__main__":
    main()
