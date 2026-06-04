#!/usr/bin/env python3
"""
Seenya - WiFi Pineapple Mark 7 module backend.

Detects nearby devices by capturing 802.11 MAC addresses, with signal strength
and vendor (OUI) lookup.

Architecture (see SEENYA_TRACKER.md):
  - Capture engine = native `tcpdump` on a monitor-mode interface, run inside a
    background `Job` (installed on-device via opkg).
  - Front-end talks to these `@module.handles_action` handlers over the Pineapple
    module socket; live updates are done by polling `get_devices` (no WebSockets).

Phase 1 = SDK skeleton: action dispatch, dependency management, and the in-memory
device store. The actual tcpdump capture inside `ScanJob.do_work` is stubbed here
and implemented in Phase 2.
"""

import json
import logging
import os
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from pineapple.modules import Module, Request
from pineapple.jobs import Job, JobManager
import pineapple.helpers.notification_helpers as notifier
from pineapple.helpers.opkg_helpers import OpkgJob

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CAPTURE_PACKAGE = 'tcpdump'          # native capture tool, installed via opkg
OUI_FILE = '/etc/pineapple/ouis'     # vendor lookup DB shipped on the Pineapple
SNAPLEN = '256'                      # only need the 802.11 headers, not payloads

# A 6-octet colon-separated hex token. The trailing negative lookahead rejects a
# match that is really part of a longer hex:colon run -- without it, a 2-hex
# label like "DA:" in "DA:ff:ff:ff:ff:ff:ff" gets mis-aligned into the MAC.
_MAC_RE = re.compile(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}(?!:?[0-9a-fA-F])')
# RadioTap signal, printed by tcpdump as e.g. "-67dBm signal" or "-32dB signal".
_SIGNAL_RE = re.compile(r'(-\d+)\s*dBm?\s+signal')

module = Module('Seenya', logging.DEBUG)
job_manager = JobManager(name='Seenya', module=module, log_level=logging.DEBUG)

# ---------------------------------------------------------------------------
# In-memory state
# ---------------------------------------------------------------------------
OUIS: Dict[str, str] = {}            # "AABBCC" -> "Vendor", loaded on_start
DEVICES: Dict[str, dict] = {}        # mac -> device record


class ScanState:
    """Tracks the single active capture job (if any)."""

    def __init__(self):
        self.job_id: Optional[str] = None
        self.interface: Optional[str] = None

    @property
    def scanning(self) -> bool:
        if not self.job_id:
            return False
        job = job_manager.get_job(self.job_id, remove_if_complete=False)
        return job is not None and not job.is_complete


scan_state = ScanState()


# ---------------------------------------------------------------------------
# Device store helpers
# ---------------------------------------------------------------------------
def _lookup_vendor(mac: str) -> str:
    prefix = mac.upper().replace(':', '').replace('-', '')[:6]
    return OUIS.get(prefix, 'Unknown')


def is_valid_mac(mac: str) -> bool:
    """True for a real unicast MAC. Filters broadcast, all-zero and multicast
    (group bit = LSB of the first octet). Ported from the original Seenya scanner."""
    if not mac:
        return False
    mac = mac.lower()
    if mac in ('00:00:00:00:00:00', 'ff:ff:ff:ff:ff:ff'):
        return False
    try:
        first_octet = int(mac.split(':')[0], 16)
    except ValueError:
        return False
    if first_octet & 0x01:        # multicast / group address
        return False
    return True


def parse_line(line: str) -> Tuple[Set[str], Optional[int]]:
    """Pure parser: extract valid unicast MACs and the RSSI (dBm) from one
    tcpdump '-e' 802.11/RadioTap output line. No I/O — unit tested off-device."""
    macs = {m.lower() for m in _MAC_RE.findall(line) if is_valid_mac(m)}
    signal_match = _SIGNAL_RE.search(line)
    signal = int(signal_match.group(1)) if signal_match else None
    return macs, signal


def record_device(mac: str, signal: Optional[int] = None) -> None:
    """Insert or update a detected device. Called by the capture job (Phase 2/3)."""
    mac = mac.lower()
    now = datetime.now().isoformat()
    dev = DEVICES.get(mac)
    if dev is None:
        DEVICES[mac] = {
            'mac': mac,
            'signal': signal,
            'first_seen': now,
            'last_seen': now,
            'count': 1,
            'vendor': _lookup_vendor(mac),
        }
    else:
        dev['last_seen'] = now
        dev['count'] += 1
        if signal is not None and (dev['signal'] is None or signal > dev['signal']):
            dev['signal'] = signal


def process_lines(lines) -> int:
    """Consume an iterable of tcpdump output lines, recording every detected
    device. Returns the number of detections processed. Kept separate from the
    subprocess so the full parse->record->aggregate pipeline is testable off-device."""
    detections = 0
    for line in lines:
        macs, signal = parse_line(line)
        for mac in macs:
            record_device(mac, signal)
            detections += 1
    return detections


# ---------------------------------------------------------------------------
# Capture job  (tcpdump on a monitor-mode interface)
# ---------------------------------------------------------------------------
class ScanJob(Job[bool]):
    """Runs `tcpdump` on a monitor-mode interface, streaming each line through
    parse_line() and feeding detections into the device store. Runs until stop()."""

    def __init__(self, interface: str):
        super().__init__()
        self.interface = interface
        self._process: Optional[subprocess.Popen] = None
        self._stopped = False

    def _build_command(self) -> List[str]:
        # -l line-buffered, -e link-level (802.11 addresses), -n no name lookups,
        # -s small snaplen (headers only). The interface must already be in
        # monitor mode (e.g. wlan1mon).
        return ['tcpdump', '-l', '-e', '-n', '-s', SNAPLEN, '-i', self.interface]

    def do_work(self, logger: logging.Logger) -> bool:
        cmd = self._build_command()
        logger.debug('Starting capture: ' + ' '.join(cmd))
        try:
            self._process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
        except FileNotFoundError:
            self.error = f'{CAPTURE_PACKAGE} not found. Install it first (manage_dependencies).'
            logger.error(self.error)
            return False

        process_lines(self._process.stdout)

        return_code = self._process.wait()
        logger.debug(f'tcpdump exited with code {return_code}')

        if not self._stopped and return_code not in (0, None):
            self.error = f'tcpdump exited with code {return_code} (check the interface is in monitor mode).'
            return False
        return True

    def stop(self):
        self._stopped = True
        if self._process is not None:
            try:
                self._process.terminate()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Lifecycle handlers
# ---------------------------------------------------------------------------
@module.on_start()
def load_ouis() -> None:
    if not os.path.exists(OUI_FILE):
        module.logger.warning(f'OUI file {OUI_FILE} not found; vendor lookups disabled.')
        return
    try:
        with open(OUI_FILE) as f:
            global OUIS
            OUIS = json.load(f)
        module.logger.debug(f'Loaded {len(OUIS)} OUIs.')
    except Exception as e:
        module.logger.warning(f'Failed to load OUIs: {e}')


@module.on_shutdown()
def stop_on_shutdown(signal: int = None) -> None:
    if scan_state.job_id:
        module.logger.debug('Stopping active scan on shutdown.')
        job_manager.stop_job(job_id=scan_state.job_id)


# ---------------------------------------------------------------------------
# Notification callbacks
# ---------------------------------------------------------------------------
def _notify_dependency_done(job: OpkgJob) -> None:
    if not job.was_successful:
        module.send_notification(f'{CAPTURE_PACKAGE} install failed: {job.error}', notifier.ERROR)
    elif getattr(job, 'install', True):
        module.send_notification(f'{CAPTURE_PACKAGE} is ready.', notifier.SUCCESS)


def _notify_scan_done(job: ScanJob) -> None:
    if not job.was_successful and job.error:
        module.send_notification(f'Scan error: {job.error}', notifier.ERROR)


# ---------------------------------------------------------------------------
# Action handlers
# ---------------------------------------------------------------------------
@module.handles_action('check_dependencies')
def check_dependencies(request: Request):
    import pineapple.helpers.opkg_helpers as opkg
    return {'installed': opkg.check_if_installed(CAPTURE_PACKAGE, module.logger)}


@module.handles_action('manage_dependencies')
def manage_dependencies(request: Request):
    install = request.__dict__.get('install', True)
    job_id = job_manager.execute_job(
        OpkgJob(CAPTURE_PACKAGE, install), callbacks=[_notify_dependency_done]
    )
    return {'job_id': job_id}


@module.handles_action('list_interfaces')
def list_interfaces(request: Request):
    return {'interfaces': _available_interfaces()}


def _available_interfaces() -> List[str]:
    # Phase 2 will narrow this to monitor-capable interfaces (via `iw`).
    try:
        return sorted(i for i in os.listdir('/sys/class/net') if i != 'lo')
    except FileNotFoundError:
        return []


@module.handles_action('start_scan')
def start_scan(request: Request):
    if scan_state.scanning:
        return 'A scan is already running.', False

    interface = request.__dict__.get('interface')
    if not interface:
        return 'No interface specified.', False

    job_id = job_manager.execute_job(ScanJob(interface), callbacks=[_notify_scan_done])
    scan_state.job_id = job_id
    scan_state.interface = interface
    module.send_notification(f'Scanning for devices on {interface}.', notifier.INFO)
    return {'job_id': job_id, 'interface': interface}


@module.handles_action('stop_scan')
def stop_scan(request: Request):
    if not scan_state.job_id:
        return {'stopped': False, 'message': 'No scan is running.'}

    job_manager.stop_job(job_id=scan_state.job_id)
    interface = scan_state.interface
    scan_state.job_id = None
    scan_state.interface = None
    module.send_notification('Scan stopped.', notifier.INFO)
    return {'stopped': True, 'interface': interface}


@module.handles_action('get_status')
def get_status(request: Request):
    return {
        'scanning': scan_state.scanning,
        'interface': scan_state.interface,
        'job_id': scan_state.job_id,
        'device_count': len(DEVICES),
    }


@module.handles_action('get_devices')
def get_devices(request: Request):
    devices = sorted(DEVICES.values(), key=lambda d: d['last_seen'], reverse=True)
    return {'devices': devices, 'count': len(devices)}


@module.handles_action('clear_devices')
def clear_devices(request: Request):
    DEVICES.clear()
    return {'cleared': True}


if __name__ == '__main__':
    module.start()
