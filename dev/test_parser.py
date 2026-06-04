#!/usr/bin/env python3
"""
Phase 2 debug gate: unit tests for the pure tcpdump parser (parse_line /
is_valid_mac) over canned tcpdump '-e' 802.11/RadioTap lines. Runs on the
laptop, no hardware. Usage:  python3 dev/test_parser.py
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

parse_line = sm.parse_line
is_valid_mac = sm.is_valid_mac

_failures = []


def check(name, cond):
    print(f'{"PASS" if cond else "FAIL"} - {name}')
    if not cond:
        _failures.append(name)


# --- is_valid_mac ---
check('valid unicast', is_valid_mac('00:11:22:33:44:55') is True)
check('locally-administered unicast valid', is_valid_mac('02:11:22:33:44:55') is True)
check('broadcast rejected', is_valid_mac('ff:ff:ff:ff:ff:ff') is False)
check('all-zero rejected', is_valid_mac('00:00:00:00:00:00') is False)
check('multicast rejected (group bit)', is_valid_mac('01:00:5e:00:00:fb') is False)
check('ipv6 multicast rejected', is_valid_mac('33:33:00:00:00:01') is False)
check('empty rejected', is_valid_mac('') is False)

# --- parse_line: beacon, BSSID+SA real, DA broadcast ---
beacon = ('13:23:45.100000 -67dBm signal antenna 0 2412 MHz 11g '
          'BSSID:00:11:22:33:44:55 SA:00:11:22:33:44:55 DA:ff:ff:ff:ff:ff:ff '
          'Beacon (HomeNet) [1.0* 2.0*]')
macs, sig = parse_line(beacon)
check('beacon: one unicast mac', macs == {'00:11:22:33:44:55'})
check('beacon: signal -67', sig == -67)

# --- probe request, "dB" (no m) signal form ---
probe = ('22:39:23.054563 1.0 Mb/s 2412 MHz 11b -32dB signal antenna 1 '
         'BSSID:Broadcast DA:Broadcast SA:de:ad:be:ef:00:01 Probe Request (test)')
macs, sig = parse_line(probe)
check('probe: SA extracted, Broadcast keyword ignored', macs == {'de:ad:be:ef:00:01'})
check('probe: signal -32 (dB form)', sig == -32)

# --- data frame: three distinct unicast MACs (note DA: label is hex-safe now) ---
data = ('14:01:02.000000 -40dBm signal 5180 MHz 11a '
        'BSSID:aa:bb:cc:dd:ee:ff SA:12:34:56:78:9a:bc DA:0a:1b:2c:3d:4e:5f Data')
macs, sig = parse_line(data)
check('data: three unicast macs', macs == {'aa:bb:cc:dd:ee:ff', '12:34:56:78:9a:bc', '0a:1b:2c:3d:4e:5f'})
check('data: signal -40', sig == -40)
check('data: DA label not mis-parsed as a mac', 'da:0a:1b:2c:3d:4e' not in macs)

# --- multicast destination filtered, unicast source kept ---
mcast = '15:00:00.0 -55dBm signal SA:00:11:22:33:44:55 DA:01:00:5e:00:00:fb Data'
macs, sig = parse_line(mcast)
check('multicast dest filtered out', macs == {'00:11:22:33:44:55'})

# --- uppercase input normalized to lowercase ---
upper = '16:00:00.0 -48dBm signal SA:AA:BB:CC:DD:EE:01 DA:ff:ff:ff:ff:ff:ff Data'
macs, _ = parse_line(upper)
check('uppercase mac normalized', macs == {'aa:bb:cc:dd:ee:01'})

# --- non-frame noise line: nothing extracted ---
noise = 'tcpdump: listening on wlan1mon, link-type IEEE802_11_RADIO (802.11 plus radiotap header)'
macs, sig = parse_line(noise)
check('noise line: no macs', macs == set())
check('noise line: no signal', sig is None)

# --- timestamp tokens never mistaken for a MAC ---
check('timestamp not parsed as mac', parse_line('13:23:45.100000 some text')[0] == set())

# --- end-to-end: parse_line feeding record_device aggregates correctly ---
sm.DEVICES.clear()
for ln in (beacon, beacon, data):
    macs, sig = parse_line(ln)
    for mac in macs:
        sm.record_device(mac, sig)
# beacon mac (1) + data macs (3) = 4 unique; beacon seen twice
check('aggregation: 4 unique devices stored', len(sm.DEVICES) == 4)
check('aggregation: repeated beacon mac count == 2', sm.DEVICES['00:11:22:33:44:55']['count'] == 2)
check('aggregation: vendor field set', sm.DEVICES['00:11:22:33:44:55']['vendor'] == 'Unknown')

print()
if _failures:
    print(f'{len(_failures)} CHECK(S) FAILED: {_failures}')
    sys.exit(1)
print('ALL CHECKS PASSED')
