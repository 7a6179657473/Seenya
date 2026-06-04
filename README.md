# Seenya

A **WiFi Pineapple Mark 7** module for passive device detection. Seenya captures
nearby 802.11 MAC addresses with signal strength and vendor, and presents them as a
live table inside the Pineapple's management UI.

> Built as a proper Mk7 module: an Angular Material front-end loaded into the Pineapple
> UI, with a Python back-end on the Hak5 module SDK. It does **not** run a standalone
> web server.

## Features
- Live capture of nearby device MACs on a monitor-mode interface
- Per-device signal strength (RSSI) and vendor (OUI) lookup
- Aggregation: first/last seen, frame count, strongest signal
- One-click install of the capture dependency (`tcpdump`) via `opkg`
- Angular Material UI: interface picker, start/stop, auto-refreshing device table

## How it works
| Layer | Location | Notes |
|-------|----------|-------|
| Back-end | `projects/Seenya/src/module.py` | Hak5 SDK (`Module`, `JobManager`, `opkg`, notifications). Runs `tcpdump` in a background `Job`, parses each 802.11 line for MAC + RSSI, aggregates into a device store. Talks to the UI over the module socket. |
| Front-end | `projects/Seenya/src/lib/` | Angular 9 library. `Seenya.service.ts` wraps the module API; the component polls `get_devices`/`get_status` every 2s (no WebSockets). |
| Manifest | `projects/Seenya/src/module.json` | Module metadata (name, version, target devices). |

**Backend actions** (each a `@module.handles_action` in `module.py`, called 1:1 by the
front-end service): `check_dependencies`, `manage_dependencies`, `list_interfaces`,
`start_scan`, `stop_scan`, `get_status`, `get_devices`, `clear_devices`.

## Install
See **[docs/ON_DEVICE.md](docs/ON_DEVICE.md)** for the full build + install + smoke-test
runbook. Short version, on a build host:

```bash
nvm use            # Node 14 (see .nvmrc) — required by the Angular 9 toolchain
./dev/preflight.sh # verify packaging artifacts
./build.sh package # npm install -> ng build --prod -> Seenya-<ver>.tar.gz
./build.sh copy    # scp to root@172.16.42.1:/pineapple/modules  (or upload the tar in the UI)
```

> **Angular version is pinned to 9 on purpose.** The module is a library loaded into the
> Mk7 firmware's Angular 9 host app — upgrading the framework would break loading. Build
> with Node 12–14; newer Node will fail the Angular 9 build.

## Development
The Python back-end is testable on a laptop without the Pineapple, via a mock of the
Hak5 SDK in `dev/_stubs/`:

```bash
./dev/run_tests.sh   # byte-compile + backend unit/integration + frontend↔backend contract
```

- `dev/test_module.py` — action dispatch + scan lifecycle (mock SDK)
- `dev/test_parser.py` — the pure tcpdump MAC/RSSI parser
- `dev/test_integration.py` — full capture pipeline → device store → actions
- `dev/test_frontend_contract.py` — front-end action/column wiring matches the backend

`dev/` is a development harness and is not shipped to the device.

## Legal
For **authorized** security testing and education only. Capturing wireless traffic may
be regulated where you live — only monitor networks and devices you own or have explicit
permission to test.

## License
[MIT](LICENSE).
