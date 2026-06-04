import { Injectable } from '@angular/core';
import { ApiService } from './api.service';

/** A device row as returned by the backend `get_devices` action. */
export interface Device {
    mac: string;
    signal: number | null;
    first_seen: string;
    last_seen: string;
    count: number;
    vendor: string;
}

const MODULE = 'Seenya';

/**
 * Typed wrapper around ApiService.request for Seenya's backend actions.
 * Every action string here must match a `@module.handles_action(...)` in module.py.
 */
@Injectable({
    providedIn: 'root'
})
export class SeenyaService {
    constructor(private api: ApiService) {}

    private call(action: string, payload: any, cb: (response: any) => void): void {
        this.api.request({ module: MODULE, action, ...payload }, cb);
    }

    checkDependencies(cb: (r: any) => void): void {
        this.call('check_dependencies', {}, cb);
    }

    manageDependencies(install: boolean, cb: (r: any) => void): void {
        this.call('manage_dependencies', { install }, cb);
    }

    listInterfaces(cb: (r: any) => void): void {
        this.call('list_interfaces', {}, cb);
    }

    startScan(iface: string, cb: (r: any) => void): void {
        this.call('start_scan', { interface: iface }, cb);
    }

    stopScan(cb: (r: any) => void): void {
        this.call('stop_scan', {}, cb);
    }

    getStatus(cb: (r: any) => void): void {
        this.call('get_status', {}, cb);
    }

    getDevices(cb: (r: any) => void): void {
        this.call('get_devices', {}, cb);
    }

    clearDevices(cb: (r: any) => void): void {
        this.call('clear_devices', {}, cb);
    }
}
