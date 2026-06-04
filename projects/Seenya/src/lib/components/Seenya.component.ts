import { Component, OnDestroy, OnInit } from '@angular/core';
import { Device, SeenyaService } from '../services/Seenya.service';

@Component({
    selector: 'lib-Seenya',
    templateUrl: './Seenya.component.html',
    styleUrls: ['./Seenya.component.css']
})
export class SeenyaComponent implements OnInit, OnDestroy {

    interfaces: string[] = [];
    selectedInterface = '';
    scanning = false;
    devices: Device[] = [];
    deviceCount = 0;
    depsInstalled = true;
    busy = false;
    error = '';

    readonly displayedColumns = ['mac', 'vendor', 'signal', 'count', 'last_seen'];
    private pollHandle: any = null;
    private readonly POLL_MS = 2000;

    constructor(private seenya: SeenyaService) {}

    ngOnInit(): void {
        this.refreshInterfaces();
        this.checkDeps();
        this.refreshStatus();
    }

    ngOnDestroy(): void {
        this.stopPolling();
    }

    // --- dependency management ---
    checkDeps(): void {
        this.seenya.checkDependencies((r) => {
            if (r && !r.error) {
                this.depsInstalled = !!r.installed;
            }
        });
    }

    installDeps(): void {
        this.busy = true;
        this.seenya.manageDependencies(true, () => {
            // opkg install runs as a background job; re-check shortly after.
            setTimeout(() => {
                this.busy = false;
                this.checkDeps();
            }, 4000);
        });
    }

    // --- interfaces / status ---
    refreshInterfaces(): void {
        this.seenya.listInterfaces((r) => {
            if (r && r.interfaces) {
                this.interfaces = r.interfaces;
                if (!this.selectedInterface && r.interfaces.length) {
                    // Prefer a monitor-mode-looking interface (e.g. wlan1mon).
                    this.selectedInterface =
                        r.interfaces.find((i: string) => i.indexOf('mon') !== -1) || r.interfaces[0];
                }
            }
        });
    }

    refreshStatus(): void {
        this.seenya.getStatus((r) => {
            if (r && !r.error) {
                this.scanning = !!r.scanning;
                this.deviceCount = r.device_count || 0;
                if (r.interface) {
                    this.selectedInterface = r.interface;
                }
                if (this.scanning) {
                    this.startPolling();
                }
            }
        });
    }

    // --- scan controls ---
    start(): void {
        if (!this.selectedInterface) {
            this.error = 'Select an interface first.';
            return;
        }
        this.error = '';
        this.busy = true;
        this.seenya.startScan(this.selectedInterface, (r) => {
            this.busy = false;
            if (r && r.error) {
                this.error = r.error;
                return;
            }
            this.scanning = true;
            this.startPolling();
        });
    }

    stop(): void {
        this.busy = true;
        this.seenya.stopScan(() => {
            this.busy = false;
            this.scanning = false;
            this.stopPolling();
            this.refreshDevices();
        });
    }

    clear(): void {
        this.seenya.clearDevices(() => {
            this.devices = [];
            this.deviceCount = 0;
        });
    }

    // --- device polling ---
    refreshDevices(): void {
        this.seenya.getDevices((r) => {
            if (r && r.devices) {
                this.devices = r.devices;
                this.deviceCount = r.count;
            }
        });
    }

    private startPolling(): void {
        if (this.pollHandle) {
            return;
        }
        this.refreshDevices();
        this.pollHandle = setInterval(() => {
            this.refreshDevices();
            this.seenya.getStatus((r) => {
                if (r && !r.error) {
                    this.scanning = !!r.scanning;
                    if (!this.scanning) {
                        this.stopPolling();
                    }
                }
            });
        }, this.POLL_MS);
    }

    private stopPolling(): void {
        if (this.pollHandle) {
            clearInterval(this.pollHandle);
            this.pollHandle = null;
        }
    }

    signalLabel(signal: number | null): string {
        return signal === null || signal === undefined ? '—' : signal + ' dBm';
    }
}
