#!/usr/bin/env python3
"""
Off-device test harness for Seenya's module.py (Phase 1 debug gate).

Injects the mock `pineapple` package (dev/_stubs) onto sys.path, imports the
real backend module.py, and exercises every action handler, asserting response
shapes and the scan/device lifecycle. Run on the laptop:

    python3 dev/test_module.py
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '_stubs'))           # mock 'pineapple'
MODULE_PY = os.path.join(HERE, '..', 'projects', 'Seenya', 'src', 'module.py')

spec = importlib.util.spec_from_file_location('seenya_module', MODULE_PY)
sm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sm)

m = sm.module  # the (mock) Module instance created inside module.py

_failures = []


def check(name, cond):
    print(f'{"PASS" if cond else "FAIL"} - {name}')
    if not cond:
        _failures.append(name)


# --- all expected actions are registered (incl. JobManager's poll_job) ---
for action in ['check_dependencies', 'manage_dependencies', 'list_interfaces',
               'start_scan', 'stop_scan', 'get_status', 'get_devices',
               'clear_devices', 'poll_job']:
    check(f'action registered: {action}', action in m._action_handlers)

# --- on_start lifecycle runs without a real OUI file ---
m.run_startup()
check('startup handler tolerates missing OUI file', True)

# --- initial status ---
r = m.dispatch('get_status')
check('get_status shape', set(r) == {'scanning', 'interface', 'job_id', 'device_count'})
check('not scanning initially', r['scanning'] is False)

# --- device store: insert + dedupe + aggregate ---
check('get_devices empty', m.dispatch('get_devices') == {'devices': [], 'count': 0})
sm.record_device('AA:BB:CC:11:22:33', -42)
sm.record_device('aa:bb:cc:11:22:33', -40)   # same MAC, stronger signal
r = m.dispatch('get_devices')
check('device deduped to one', r['count'] == 1)
d = r['devices'][0]
check('device fields present', {'mac', 'signal', 'first_seen', 'last_seen', 'count', 'vendor'} <= set(d))
check('count incremented', d['count'] == 2)
check('keeps strongest signal', d['signal'] == -40)
check('mac normalized lowercase', d['mac'] == 'aa:bb:cc:11:22:33')

# --- start_scan validation + lifecycle ---
r = m.dispatch('start_scan')
check('start_scan without interface -> error tuple', isinstance(r, tuple) and r[1] is False)

r = m.dispatch('start_scan', interface='wlan1mon')
check('start_scan returns job_id + interface', isinstance(r, dict) and 'job_id' in r and r['interface'] == 'wlan1mon')

r = m.dispatch('get_status')
check('scanning True after start', r['scanning'] is True and r['interface'] == 'wlan1mon')

r = m.dispatch('start_scan', interface='wlan1mon')
check('no double scan -> error tuple', isinstance(r, tuple) and r[1] is False)

r = m.dispatch('stop_scan')
check('stop_scan ok', r.get('stopped') is True and r.get('interface') == 'wlan1mon')

r = m.dispatch('get_status')
check('not scanning after stop', r['scanning'] is False and r['interface'] is None)

# --- clear ---
check('clear_devices ok', m.dispatch('clear_devices') == {'cleared': True})
check('devices empty after clear', m.dispatch('get_devices')['count'] == 0)

# --- dependency actions ---
r = m.dispatch('check_dependencies')
check('check_dependencies shape', isinstance(r, dict) and isinstance(r.get('installed'), bool))
r = m.dispatch('manage_dependencies', install=True)
check('manage_dependencies returns job_id', isinstance(r, dict) and 'job_id' in r)

# --- at least one notification was emitted during the lifecycle ---
check('notifications captured', len(m.notifications) >= 2)

print()
if _failures:
    print(f'{len(_failures)} CHECK(S) FAILED: {_failures}')
    sys.exit(1)
print('ALL CHECKS PASSED')
