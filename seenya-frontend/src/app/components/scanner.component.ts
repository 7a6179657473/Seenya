import { Component, OnInit, OnDestroy } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Subscription } from 'rxjs';
import { ScanningService } from '../services/scanning.service';
import { DetectedDevice } from '../models/device.model';

@Component({
  selector: 'app-scanner',
  templateUrl: './scanner.component.html',
  styleUrls: ['./scanner.component.css']
})
export class ScannerComponent implements OnInit, OnDestroy {
  isScanning = false;
  isLoading = false;
  detectedDevices: DetectedDevice[] = [];
  selectedInterface = '';
  availableInterfaces: string[] = [];
  
  private subscriptions: Subscription[] = [];
  
  // Material table columns
  displayedColumns: string[] = ['mac', 'device_type', 'signal_strength', 'count', 'first_seen', 'last_seen'];

  constructor(
    private scanningService: ScanningService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadWirelessInterfaces();
    this.loadDetectedDevices();
    this.setupRealtimeUpdates();
    this.checkScanningStatus();
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  private loadWirelessInterfaces(): void {
    this.scanningService.getWirelessInterfaces().subscribe({
      next: (response) => {
        if (response.success) {
          this.availableInterfaces = response.interfaces;
          if (this.availableInterfaces.length > 0) {
            this.selectedInterface = this.availableInterfaces[0];
          }
        }
      },
      error: (error) => {
        console.error('Error loading wireless interfaces:', error);
        this.showSnackBar('Failed to load wireless interfaces', 'error');
      }
    });
  }

  private loadDetectedDevices(): void {
    this.scanningService.getDetectedDevices().subscribe({
      next: (response) => {
        if (response.success) {
          this.detectedDevices = Object.entries(response.devices).map(([mac, device]) => ({
            ...device,
            mac
          }));
        }
      },
      error: (error) => {
        console.error('Error loading detected devices:', error);
      }
    });
  }

  private setupRealtimeUpdates(): void {
    const deviceStream = this.scanningService.getDeviceDetectedStream().subscribe({
      next: (device) => {
        // Check if device already exists in list
        const existingIndex = this.detectedDevices.findIndex(d => d.mac === device.mac);
        
        if (existingIndex >= 0) {
          // Update existing device
          this.detectedDevices[existingIndex] = device;
        } else {
          // Add new device
          this.detectedDevices.push(device);
        }
        
        // Sort by last seen (most recent first)
        this.detectedDevices.sort((a, b) => 
          new Date(b.last_seen).getTime() - new Date(a.last_seen).getTime()
        );
      }
    });
    
    this.subscriptions.push(deviceStream);
  }

  private checkScanningStatus(): void {
    this.scanningService.getScanningStatus().subscribe({
      next: (status) => {
        if (status.success) {
          this.isScanning = status.is_scanning;
        }
      },
      error: (error) => {
        console.error('Error checking scanning status:', error);
      }
    });
  }

  startScanning(): void {
    if (this.isScanning) return;
    
    this.isLoading = true;
    
    this.scanningService.startScanning(this.selectedInterface || undefined).subscribe({
      next: (response) => {
        this.isLoading = false;
        if (response.success) {
          this.isScanning = true;
          this.showSnackBar('Wireless scanning started successfully', 'success');
        } else {
          this.showSnackBar(response.error || 'Failed to start scanning', 'error');
        }
      },
      error: (error) => {
        this.isLoading = false;
        console.error('Error starting scanning:', error);
        this.showSnackBar('Failed to start scanning', 'error');
      }
    });
  }

  stopScanning(): void {
    if (!this.isScanning) return;
    
    this.isLoading = true;
    
    this.scanningService.stopScanning().subscribe({
      next: (response) => {
        this.isLoading = false;
        if (response.success) {
          this.isScanning = false;
          this.showSnackBar('Wireless scanning stopped', 'info');
        } else {
          this.showSnackBar(response.error || 'Failed to stop scanning', 'error');
        }
      },
      error: (error) => {
        this.isLoading = false;
        console.error('Error stopping scanning:', error);
        this.showSnackBar('Failed to stop scanning', 'error');
      }
    });
  }

  clearDevices(): void {
    this.scanningService.clearDetectedDevices().subscribe({
      next: (response) => {
        if (response.success) {
          this.detectedDevices = [];
          this.showSnackBar('Detected devices cleared', 'info');
        } else {
          this.showSnackBar(response.error || 'Failed to clear devices', 'error');
        }
      },
      error: (error) => {
        console.error('Error clearing devices:', error);
        this.showSnackBar('Failed to clear devices', 'error');
      }
    });
  }

  refreshDevices(): void {
    this.loadDetectedDevices();
    this.showSnackBar('Device list refreshed', 'info');
  }

  getSignalStrengthColor(strength: number): string {
    if (strength > -40) return 'green';
    if (strength > -60) return 'orange';
    return 'red';
  }

  formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleString();
  }

  private showSnackBar(message: string, type: 'success' | 'error' | 'info'): void {
    const config = {
      duration: 3000,
      panelClass: [`snackbar-${type}`]
    };
    
    this.snackBar.open(message, 'Close', config);
  }
}
