#!/usr/bin/env bash
# Off-device test gate for the Seenya backend. Runs the byte-compile + all three
# harnesses against the mock `pineapple` package. No hardware required.
#   Usage:  ./dev/run_tests.sh   (from the Seenya/ module root)
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== py_compile =="
python3 -m py_compile projects/Seenya/src/module.py && echo "  compile ok"

fail=0
for t in test_module test_parser test_integration test_frontend_contract; do
    echo "== dev/$t.py =="
    if python3 "dev/$t.py" | tail -1; then :; else fail=1; fi
done

[ "$fail" -eq 0 ] && echo "ALL SUITES PASSED" || { echo "SUITE FAILURES"; exit 1; }
