#!/usr/bin/env bash
# Phase 5 packaging pre-flight: verifies everything build.sh needs is present and
# valid BEFORE you run the Angular build on a build host. Runs anywhere (no Node,
# no hardware). Usage:  ./dev/preflight.sh   (from the Seenya/ module root)
set -euo pipefail
cd "$(dirname "$0")/.."

NAME="$(basename "$PWD")"
SRC="projects/$NAME/src"
fail=0
ok()   { echo "  ok   - $1"; }
bad()  { echo "  FAIL - $1"; fail=1; }

echo "== module: $NAME =="

for f in "$SRC/module.json" "$SRC/module.py" "$SRC/module.svg"; do
    [ -f "$f" ] && ok "present: $f" || bad "missing: $f"
done
[ -d "$SRC/assets" ] && ok "present: assets/" || bad "missing: assets/"

python3 -c "import json;json.load(open('$SRC/module.json'))" 2>/dev/null \
    && ok "module.json is valid JSON" || bad "module.json is not valid JSON"

# manifest name must equal the workspace dir (build.sh derives both from basename)
mn="$(python3 -c "import json;print(json.load(open('$SRC/module.json'))['name'])" 2>/dev/null || true)"
[ "$mn" = "$NAME" ] && ok "manifest name matches dir ($NAME)" || bad "manifest name '$mn' != dir '$NAME'"

python3 -m py_compile "$SRC/module.py" 2>/dev/null \
    && ok "module.py byte-compiles" || bad "module.py has syntax errors"

# Build host needs a Node compatible with Angular 9 (12-14). Warn loudly otherwise.
if command -v node >/dev/null 2>&1; then
    major="$(node -p 'process.versions.node.split(".")[0]')"
    if [ "$major" -ge 12 ] && [ "$major" -le 14 ]; then
        ok "node $(node -v) is compatible with the Angular 9 toolchain"
    else
        echo "  warn - node $(node -v): Angular 9 needs Node 12-14. Use nvm before 'ng build'."
    fi
else
    echo "  warn - node not found: install Node 12-14 on the build host."
fi

echo
[ "$fail" -eq 0 ] && echo "PRE-FLIGHT OK — ready for ./build.sh package on a build host" \
                  || { echo "PRE-FLIGHT FAILED"; exit 1; }
