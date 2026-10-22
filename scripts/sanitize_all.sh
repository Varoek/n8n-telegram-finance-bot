#!/usr/bin/env bash
# Sanitize every exported workflow in exports-raw/ in one go.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p workflows

# 1) build the private map automatically (healthchecks ping URLs)
python3 - <<'PY'
import json, glob, os, re
path = '.sanitize-map.json'
m = json.load(open(path)) if os.path.exists(path) else {}
for f in glob.glob('exports-raw/FIN-*.json'):
    text = open(f, encoding='utf-8').read()
    for url in set(re.findall(r'https://hc-ping\.com/[0-9a-fA-F-]{36}', text)):
        m[url] = 'https://hc-ping.com/YOUR-HEALTHCHECK-UUID'
json.dump(m, open(path, 'w'), indent=2)
print('map entries:', len(m))
PY

# 2) sanitize each FIN-* export
for f in exports-raw/FIN-*.json; do
  base=$(basename "$f")
  case "$base" in
    FIN-01*) out=FIN-01-ingest ;;
    FIN-02*) out=FIN-02-process-txn ;;
    FIN-03*) out=FIN-03-retry-queue ;;
    FIN-04*) out=FIN-04-report ;;
    FIN-98*) out=FIN-98-heartbeat ;;
    FIN-99*) out=FIN-99-error-handler ;;
    *) echo "skip $base"; continue ;;
  esac
  python3 scripts/sanitize_workflow.py "$f" -o "workflows/$out.json" --map .sanitize-map.json
done

# 3) final scan
python3 scripts/check_secrets.py
