#!/usr/bin/env python3
"""
Phase 4 toolchain-free gate: validates the Angular frontend wires correctly to
the Python backend WITHOUT needing the Angular 9 build toolchain (which is
incompatible with this machine's Node). Checks:
  - every action the service calls exists as a @module.handles_action in module.py
  - every service method the component calls is defined on the service
  - every table column in the component has a matColumnDef in the template
    and corresponds to a field on the Device interface
Usage:  python3 dev/test_frontend_contract.py
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC = os.path.join(ROOT, 'projects', 'Seenya', 'src')


def read(*parts):
    with open(os.path.join(SRC, *parts)) as f:
        return f.read()


module_py = read('module.py')
service_ts = read('lib', 'services', 'Seenya.service.ts')
component_ts = read('lib', 'components', 'Seenya.component.ts')
component_html = read('lib', 'components', 'Seenya.component.html')

_failures = []


def check(name, cond, detail=''):
    print(f'{"PASS" if cond else "FAIL"} - {name}' + (f'  ({detail})' if detail and not cond else ''))
    if not cond:
        _failures.append(name)


# --- backend actions vs frontend action strings ---
backend_actions = set(re.findall(r"@module\.handles_action\(['\"]([^'\"]+)['\"]\)", module_py))
frontend_actions = set(re.findall(r"this\.call\(['\"]([^'\"]+)['\"]", service_ts))
check('backend exposes actions', len(backend_actions) >= 8, str(backend_actions))
check('frontend calls some actions', len(frontend_actions) >= 8, str(frontend_actions))
missing = frontend_actions - backend_actions
check('every frontend action exists in backend', not missing, f'missing in backend: {missing}')

# --- service methods used by component are defined ---
service_methods = set(re.findall(r'^\s{4}(\w+)\s*\(', service_ts, re.M))
used_methods = set(re.findall(r'this\.seenya\.(\w+)\(', component_ts))
undefined = used_methods - service_methods
check('component only calls defined service methods', not undefined, f'undefined: {undefined}')
check('component actually uses the service', len(used_methods) >= 6, str(used_methods))

# --- table columns: displayedColumns vs matColumnDef vs Device fields ---
device_fields = set(re.findall(r'^\s{4}(\w+)\s*:', service_ts, re.M))
cols_match = re.search(r'displayedColumns\s*=\s*\[([^\]]+)\]', component_ts)
displayed = set(re.findall(r"'([^']+)'", cols_match.group(1))) if cols_match else set()
col_defs = set(re.findall(r'matColumnDef="([^"]+)"', component_html))
check('displayedColumns parsed', len(displayed) == 5, str(displayed))
check('every displayed column has a matColumnDef', displayed <= col_defs, f'no def for: {displayed - col_defs}')
check('every matColumnDef is displayed (no orphans)', col_defs <= displayed, f'orphans: {col_defs - displayed}')
check('every column maps to a Device field', displayed <= device_fields, f'not on Device: {displayed - device_fields}')

# --- sanity: header/row defs reference displayedColumns ---
check('table header row binds displayedColumns', 'matHeaderRowDef="displayedColumns"' in component_html)
check('table data row binds displayedColumns', 'columns: displayedColumns' in component_html)

# --- module name used by service matches manifest/module.py ---
check("service targets module 'Seenya'", "MODULE = 'Seenya'" in service_ts)

print()
if _failures:
    print(f'{len(_failures)} CHECK(S) FAILED: {_failures}')
    sys.exit(1)
print('ALL CHECKS PASSED')
print(f'  backend actions : {sorted(backend_actions)}')
print(f'  frontend actions: {sorted(frontend_actions)}')
