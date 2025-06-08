import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface MacEntry {
  macAddress: string;
  signalStrength: number;
  lastSeen: string;
}

@Injectable({
  providedIn: 'root'
})
export class MacService {
  private apiUrl = 'http://localhost:5000/api/macs'; // Adjust the URL as needed

  constructor(private http: HttpClient) { }

  logMacEntry(macEntry: MacEntry): Observable<MacEntry> {
    return this.http.post<MacEntry>(this.apiUrl, macEntry);
  }

  getMacEntries(): Observable<MacEntry[]> {
    return this.http.get<MacEntry[]>(this.apiUrl);
  }
}