export interface DetectedDevice {
  mac: string;
  signal_strength: number;
  first_seen: string;
  last_seen: string;
  count: number;
  device_type: string;
}

export interface ScanningStatus {
  success: boolean;
  is_scanning: boolean;
  devices_detected: number;
}

export interface WirelessInterface {
  name: string;
  description?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface DevicesResponse {
  success: boolean;
  devices: { [mac: string]: DetectedDevice };
  count: number;
}
