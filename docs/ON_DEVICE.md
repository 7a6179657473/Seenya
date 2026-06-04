# Seenya — Build, Install & On-Device Debugging

This is the Phase 5 runbook: turn the source in this repo into an installed WiFi
Pineapple Mark 7 module and verify it live. The earlier phases are all verifiable
off-device (`./dev/run_tests.sh`); **everything in this file needs the hardware**
(a monitor-mode radio) and a build host, because the capture path uses real
`tcpdump` on a real 802.11 interface.

---

## 0. Pre-flight (no hardware needed)

From the module root:

```bash
./dev/preflight.sh     # checks module.json / module.py / svg / assets, manifest name, node version
./dev/run_tests.sh     # backend + frontend-contract suites (72+ checks)
```

Both should pass before you build.

---

## 1. Build the module (on a build host)

A Pineapple module is an **Angular 9 library**. The Angular 9 CLI/ng-packagr needs
**Node 12–14** — newer Node (e.g. 24) will fail the build. This is a toolchain
constraint, not a code issue; do **not** upgrade the module to a newer Angular, or
it won't load into the Mk7's Angular 9 host UI.

```bash
# one-time, on the build host
nvm install 14 && nvm use 14        # or any Node 12-14

cd Seenya
./build.sh package                  # npm install -> ng build --prod -> Seenya-<ver>.tar.gz
```

`build.sh` will offer to run `npm install` if `node_modules/` is missing. On success
you get `dist/Seenya/` (the built bundle + `module.json` + `module.py` + `module.svg`)
and a `Seenya-<version>.tar.gz` in the module root.

If `ng build --prod` fails, run it directly to see why:
```bash
npx ng build --prod
```

---

## 2. Install on the Mk7

The Pineapple must reach the internet for `opkg` (to install tcpdump). Internet
sharing from the laptop is already set up — after an antenna reboot run
`~/claude-workspace/pineapple-share-up.sh` first.

**Option A — scp (build.sh helper):**
```bash
./build.sh copy          # scp dist/Seenya -> root@172.16.42.1:/pineapple/modules
```

**Option B — UI upload:** WiFi Pineapple UI → *Modules* → *Get Modules* /
*Upload* → select `Seenya-<ver>.tar.gz`.

Installed location on the device: `/pineapple/modules/Seenya/` (backend at
`/pineapple/modules/Seenya/module.py`).

---

## 3. On-device smoke test (the real gate)

Open the **Seenya** module in the Pineapple UI, then verify each layer:

### 3a. Dependency (tcpdump)
- The UI shows a banner if tcpdump is missing → click **Install tcpdump**.
- Cross-check on the device:
  ```bash
  ssh root@172.16.42.1
  opkg list-installed | grep -i tcpdump      # is it installed?
  opkg update && opkg install tcpdump        # manual install if needed
  ```

### 3b. Monitor interface
- Put the scanning radio into monitor mode (Recon, or):
  ```bash
  iw dev                                      # list interfaces + their type
  airmon-ng start wlan1                       # -> wlan1mon (typical Mk7 scanning radio)
  ```
- It should then appear in the module's **interface picker** (backend
  `list_interfaces` reads `/sys/class/net`). Pick the `…mon` interface.

### 3c. Live capture
- Click **Start Scan**. Within a few seconds the device table should populate
  (MAC · Vendor · Signal · Frames · Last seen), updating every 2s.
- **Cross-check the raw capture** matches what Seenya shows:
  ```bash
  tcpdump -e -n -s 256 -i wlan1mon            # same flags the module uses
  # you should see 802.11 frames with "-NNdBm signal" and SA:/DA:/BSSID: addresses
  ```
  The MACs and signal levels in the UI should correspond to this stream.
- **Stop Scan** and **Clear** should both work; status returns to *Idle*.

### 3d. Vendor lookup
- `vendor` column should resolve known OUIs. The DB is on-device:
  ```bash
  ls -l /etc/pineapple/ouis                   # present on Mk7 firmware
  ```
  If absent, vendors show `Unknown` (handled gracefully).

---

## 4. Debugging by layer

**Backend won't start / actions error** — run the backend by hand to see logs live:
```bash
ssh root@172.16.42.1
python3 /pineapple/modules/Seenya/module.py   # prints startup + handler logs (DEBUG)
# in another shell, confirm the module socket exists while it runs:
ls -l /tmp/modules/Seenya.sock
```
Also check the system log:
```bash
logread | grep -i seenya
logread -f                                     # follow live while you click in the UI
```

**Scan starts but no devices**
1. Wrong/!monitor interface → `iw dev` (type should be `monitor`); re-`airmon-ng`.
2. No nearby traffic → confirm with the manual `tcpdump` in 3c.
3. tcpdump exits immediately → the module surfaces
   *"tcpdump exited with code N (check the interface is in monitor mode)"* as a
   notification; reproduce with the manual `tcpdump` command to see the real error.

**Module doesn't appear / blank panel in UI**
- Almost always an Angular version mismatch — rebuild with the Angular 9 toolchain
  (Section 1). Check the browser devtools console for load errors.

**check_dependencies says missing but tcpdump is installed**
- Confirm the opkg package name is exactly `tcpdump` (`opkg list-installed | grep tcpdump`).

---

## 5. Uninstall / cleanup
```bash
ssh root@172.16.42.1 'rm -rf /pineapple/modules/Seenya'   # or remove via the UI
```

---

## Notes / record results here
When you run the live test, capture anything that differed (interface names,
opkg package name, OUI path, tcpdump output format) back into this file — those are
the device-specific facts the off-device tests can't know.
