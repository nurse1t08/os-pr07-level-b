#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
tmp=$(mktemp -d)
pid=''
cleanup() {
  if [[ -n "$pid" ]]; then kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; fi
  rm -rf "$tmp"
}
trap cleanup EXIT
python3 fifo_server.py --dir "$tmp" & pid=$!
for i in {1..50}; do [[ -p "$tmp/requests.fifo" ]] && break; sleep 0.1; done
python3 fifo_client.py '2 * (5 + 7)' --dir "$tmp"
python3 fifo_client.py '10 / 2 + 3' --dir "$tmp"
python3 measure_latency.py --mode fifo --path "$tmp"
kill "$pid"; wait "$pid" 2>/dev/null || true; pid=''
python3 unix_server.py --socket "$tmp/service.sock" & pid=$!
for i in {1..50}; do [[ -S "$tmp/service.sock" ]] && break; sleep 0.1; done
python3 unix_client.py '2 + 3' --socket "$tmp/service.sock" & c1=$!
python3 unix_client.py '4 * 5' --socket "$tmp/service.sock" & c2=$!
python3 unix_client.py '10 / 2' --socket "$tmp/service.sock" & c3=$!
wait "$c1" "$c2" "$c3"
python3 measure_latency.py --mode unix --path "$tmp/service.sock"
kill "$pid"; wait "$pid" 2>/dev/null || true; pid=''
python3 compare_memory.py --count 10000000
