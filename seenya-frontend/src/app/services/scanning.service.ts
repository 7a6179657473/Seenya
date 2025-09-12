import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { io, Socket } from 'socket.io-client';
import { DetectedDevice, ScanningStatus, DevicesResponse } from '../models/device.model';

@Injectable({
  providedIn: 'root'
})
export class ScanningService {
  private readonly API_BASE_URL = 'http://localhost:5000/api/scanning';
  private socket: Socket;
  private deviceDetectedSubject = new Subject<DetectedDevice>();
  
  constructor(private http: HttpClient) {
    this.socket = io('http://localhost:5000');
    this.setupSocketListeners();
  }

  private setupSocketListeners(): void {
    this.socket.on('connect', () => {
      console.log('Connected to server via WebSocket');
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from server');
    });

    this.socket.on('device_detected', (device: DetectedDevice) => {
      this.deviceDetectedSubject.next(device);
    });
  }

  /**
   * Observable for real-time device detection events
   */
  getDeviceDetectedStream(): Observable<DetectedDevice> {
    return this.deviceDetectedSubject.asObservable();
  }

  /**
   * Get available wireless interfaces
   */
  getWirelessInterfaces(): Observable<any> {
    return this.http.get(`${this.API_BASE_URL}/interfaces`);
  }

  /**
   * Start wireless scanning
   */
  startScanning(interface?: string): Observable<any> {
    const payload = interface ? { interface } : {};
    return this.http.post(`${this.API_BASE_URL}/start`, payload);
  }

  /**
   * Stop wireless scanning
   */
  stopScanning(): Observable<any> {
    return this.http.post(`${this.API_BASE_URL}/stop`, {});
  }

  /**
   * Get current scanning status
   */
  getScanningStatus(): Observable<ScanningStatus> {
    return this.http.get<ScanningStatus>(`${this.API_BASE_URL}/status`);
  }

  /**
   * Get all detected devices
   */
  getDetectedDevices(): Observable<DevicesResponse> {
    return this.http.get<DevicesResponse>(`${this.API_BASE_URL}/devices`);
  }

  /**
   * Clear all detected devices
   */
  clearDetectedDevices(): Observable<any> {
    return this.http.post(`${this.API_BASE_URL}/devices/clear`, {});
  }

  /**
   * Check server health
   */
  checkHealth(): Observable<any> {
    return this.http.get('http://localhost:5000/health');
  }

  /**
   * Disconnect socket
   */
  ngOnDestroy(): void {
    if (this.socket) {
      this.socket.disconnect();
    }
  }
}
