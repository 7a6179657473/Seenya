#!/usr/bin/env python3
"""
Phase 3 debug gate: end-to-end integration of the capture pipeline and the
JobManager/device-store wiring, without hardware. Replays canned tcpdump lines
through process_lines() (the same loop ScanJob.do_work feeds), then exercises
the action handlers that the front-end will call. Usage:

    python3 dev/test_integration.py
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '_stubs'))
MODULE_PY = os.path.join(HERE, '..', 'projects', 'Seenya', 'src', 'module.py')

spec = importlib.util.spec_from_file_location('seenya_module', MODULE_PY)
sm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sm)

m = sm.module
_failures = []


def check(name, cond):
    print(f'{"PASS" if cond else "FAIL"} - {name}')
    if not cond:
        _failures.append(name)


# A realistic-ish capture: AP beacon (x3), a client probe, a data frame, plus a
# multicast frame and a noise line that should contribute nothing.
AP = '00:11:22:aa:bb:cc'
CLIENT = '0a:1b:2c:3d:4e:5f'
PEER = '12:34:56:78:9a:bc'
SAMPLE = [
    f'-60dBm signal BSSID:{AP} SA:{AP} DA:ff:ff:ff:ff:ff:ff Beacon (Net)',
    f'-58dBm signal BSSID:{AP} SA:{AP} DA:ff:ff:ff:ff:ff:ff Beacon (Net)',
    f'-55dBm signal BSSID:{AP} SA:{AP} DA:ff:ff:ff:ff:ff:ff Beacon (Net)',   # strongest
    f'-70dBm signal SA:{CLIENT} DA:ff:ff:ff:ff:ff:ff Probe Request (Net)',
    f'-40dBm signal BSSID:{AP} SA:{PEER} DA:{CLIENT} Data',
    f'-50dBm signal SA:{CLIENT} DA:01:00:5e:00:00:fb Data',                  # multicast dest dropped
    'tcpdump: listening on wlan1mon, link-type IEEE802_11_RADIO',            # noise
]

# --- reset state and replay through the real pipeline loop ---
sm.DEVICES.clear()
sm.OUIS.clear()
detections = sm.process_lines(SAMPLE)
# detections: beacon AP x3 + probe CLIENT x1 + data (AP+PEER+CLIENT) x1 each + mcast CLIENT x1 = 8
check('process_lines detection count', detections == 8)

# --- get_devices reflects unique, aggregated devices ---
resp = m.dispatch('get_devices')
macs = {d['mac'] for d in resp['devices']}
check('three unique devices (AP, CLIENT, PEER)', macs == {AP, CLIENT, PEER})
check('get_devices count matches', resp['count'] == 3)

by_mac = {d['mac']: d for d in resp['devices']}
check('AP seen 4 times (3 beacons + 1 data BSSID)', by_mac[AP]['count'] == 4)
check('AP keeps strongest signal (-40 from data frame)', by_mac[AP]['signal'] == -40)
check('CLIENT seen 3 times (probe + data + mcast)', by_mac[CLIENT]['count'] == 3)
check('every device has full record', all(
    {'mac', 'signal', 'first_seen', 'last_seen', 'count', 'vendor'} <= set(d)
    for d in resp['devices']))

# --- get_status mirrors the store ---
st = m.dispatch('get_status')
check('status device_count == 3', st['device_count'] == 3)
check('status not scanning (no job started)', st['scanning'] is False)

# --- OUI vendor lookup when the DB is populated ---
sm.DEVICES.clear()
sm.OUIS = {'0011AA': 'Acme Devices'}   # key = first 3 octets, upper, no separators
sm.process_lines([f'-60dBm signal SA:00:11:aa:99:88:77 DA:ff:ff:ff:ff:ff:ff Data'])
vendor = m.dispatch('get_devices')['devices'][0]['vendor']
check('vendor resolved from OUI db', vendor == 'Acme Devices')
sm.process_lines([f'-60dBm signal SA:de:ad:be:ef:00:01 DA:ff:ff:ff:ff:ff:ff Data'])
unknown = next(d for d in m.dispatch('get_devices')['devices'] if d['mac'] == 'de:ad:be:ef:00:01')
check('unknown OUI -> Unknown', unknown['vendor'] == 'Unknown')

# --- start_scan actually registers a ScanJob bound to the interface ---
sm.DEVICES.clear()
r = m.dispatch('start_scan', interface='wlan1mon')
job = sm.job_manager.get_job(r['job_id'], remove_if_complete=False)
check('start_scan created a ScanJob', isinstance(job, sm.ScanJob))
check('ScanJob bound to wlan1mon', job.interface == 'wlan1mon')
check('ScanJob builds correct tcpdump command',
      job._build_command() == ['tcpdump', '-l', '-e', '-n', '-s', '256', '-i', 'wlan1mon'])
check('status scanning during job', m.dispatch('get_status')['scanning'] is True)

# --- stop tears it down ---
m.dispatch('stop_scan')
check('status not scanning after stop', m.dispatch('get_status')['scanning'] is False)

# --- clear empties the store ---
m.dispatch('clear_devices')
check('clear empties store', m.dispatch('get_devices')['count'] == 0)

print()
if _failures:
    print(f'{len(_failures)} CHECK(S) FAILED: {_failures}')
    sys.exit(1)
print('ALL CHECKS PASSED')
