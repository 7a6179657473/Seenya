import { Component, OnInit } from '@angular/core';
import { MacService } from '../services/mac.service';

@Component({
  selector: 'app-mac-monitor',
  templateUrl: './mac-monitor.component.html',
  styleUrls: ['./mac-monitor.component.css']
})
export class MacMonitorComponent implements OnInit {
  macEntries: any[] = [];

  constructor(private macService: MacService) {}

  ngOnInit(): void {
    this.loadMacEntries();
  }

  loadMacEntries(): void {
    this.macService.getMacEntries().subscribe(entries => {
      this.macEntries = entries;
    });
  }
}