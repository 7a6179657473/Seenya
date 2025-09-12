"""
Wireless Scanner Service for MAC Address Detection
Phase 1: Basic wireless scanning and MAC address detection
"""

import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable
from scapy.all import *
import psutil


class WirelessScanner:
    """
    Service for detecting MAC addresses within wireless range
    """
    
    def __init__(self):
        self.is_scanning = False
        self.detected_devices = {}  # {mac: {signal_strength, first_seen, last_seen, count}}
        self.scan_thread = None
        self.callback_functions = []  # Callbacks for new device detection
        
    def get_wireless_interfaces(self) -> List[str]:
        """
        Get available wireless network interfaces
        """
        interfaces = []
        try:
            # Get network interfaces
            for interface_name, interface_info in psutil.net_if_addrs().items():
                # On Windows, wireless interfaces often contain 'Wi-Fi' or 'Wireless'
                if any(keyword in interface_name.lower() for keyword in ['wi-fi', 'wireless', 'wlan']):
                    interfaces.append(interface_name)
            
            # Also get scapy interfaces
            scapy_interfaces = get_if_list()
            for iface in scapy_interfaces:
                if any(keyword in iface.lower() for keyword in ['wi-fi', 'wireless', 'wlan']):
                    if iface not in interfaces:
                        interfaces.append(iface)
                        
        except Exception as e:
            print(f"Error getting wireless interfaces: {e}")
            
        return interfaces
    
    def packet_handler(self, packet):
        """
        Handle captured wireless packets and extract MAC addresses
        """
        try:
            # Check if packet has a wireless layer
            if packet.haslayer(Dot11):
                # Extract MAC addresses from 802.11 frames
                mac_addresses = set()
                
                # Source MAC
                if hasattr(packet[Dot11], 'addr2') and packet[Dot11].addr2:
                    mac_addresses.add(packet[Dot11].addr2)
                
                # Destination MAC  
                if hasattr(packet[Dot11], 'addr1') and packet[Dot11].addr1:
                    mac_addresses.add(packet[Dot11].addr1)
                
                # BSSID (Access Point MAC)
                if hasattr(packet[Dot11], 'addr3') and packet[Dot11].addr3:
                    mac_addresses.add(packet[Dot11].addr3)
                
                # Process each MAC address
                for mac in mac_addresses:
                    if self._is_valid_mac(mac):
                        self._process_detected_mac(mac, packet)
                        
        except Exception as e:
            # Silently handle packet processing errors to avoid spam
            pass
    
    def _is_valid_mac(self, mac: str) -> bool:
        """
        Check if MAC address is valid and not a broadcast/multicast address
        """
        if not mac or mac == "00:00:00:00:00:00" or mac == "ff:ff:ff:ff:ff:ff":
            return False
            
        # Skip multicast addresses (first bit of first byte is 1)
        try:
            first_byte = int(mac.split(':')[0], 16)
            if first_byte & 0x01:  # Multicast bit set
                return False
        except:
            return False
            
        return True
    
    def _process_detected_mac(self, mac: str, packet):
        """
        Process a detected MAC address
        """
        current_time = datetime.now()
        
        # Try to estimate signal strength (limited on Windows without monitor mode)
        signal_strength = self._estimate_signal_strength(packet)
        
        if mac not in self.detected_devices:
            # New device detected
            self.detected_devices[mac] = {
                'signal_strength': signal_strength,
                'first_seen': current_time,
                'last_seen': current_time,
                'count': 1,
                'device_type': self._identify_device_type(mac)
            }
            
            # Notify callbacks of new device
            for callback in self.callback_functions:
                try:
                    callback(mac, self.detected_devices[mac])
                except:
                    pass
                    
        else:
            # Update existing device
            self.detected_devices[mac]['last_seen'] = current_time
            self.detected_devices[mac]['count'] += 1
            if signal_strength > self.detected_devices[mac]['signal_strength']:
                self.detected_devices[mac]['signal_strength'] = signal_strength
    
    def _estimate_signal_strength(self, packet) -> int:
        """
        Estimate signal strength from packet (limited accuracy without monitor mode)
        """
        # On Windows without monitor mode, we can't get accurate RSSI
        # Return a placeholder value
        return -50  # Default moderate signal strength
    
    def _identify_device_type(self, mac: str) -> str:
        """
        Try to identify device type based on MAC address OUI
        """
        # Basic OUI identification (can be expanded with OUI database)
        oui = mac[:8].upper()
        
        common_ouis = {
            '00:50:56': 'VMware',
            '08:00:27': 'VirtualBox',
            '00:15:5D': 'Microsoft Hyper-V',
            'DC:A6:32': 'Apple',
            '00:1B:63': 'Apple',
            'AC:DE:48': 'Apple',
            '28:F0:76': 'Apple iPhone',
            'F4:F5:D8': 'Google',
            '00:1A:11': 'Google',
        }
        
        return common_ouis.get(oui, 'Unknown')
    
    def start_scanning(self, interface: Optional[str] = None) -> bool:
        """
        Start wireless scanning on specified interface
        """
        if self.is_scanning:
            return False
            
        # Get available interfaces if none specified
        if not interface:
            interfaces = self.get_wireless_interfaces()
            if not interfaces:
                print("No wireless interfaces found")
                return False
            interface = interfaces[0]  # Use first available
        
        self.is_scanning = True
        self.scan_thread = threading.Thread(
            target=self._scan_worker, 
            args=(interface,),
            daemon=True
        )
        self.scan_thread.start()
        
        print(f"Started wireless scanning on interface: {interface}")
        return True
    
    def _scan_worker(self, interface: str):
        """
        Worker thread for wireless scanning
        """
        try:
            print(f"Scanning for wireless devices on {interface}...")
            
            # Start packet capture
            sniff(
                iface=interface,
                prn=self.packet_handler,
                stop_filter=lambda x: not self.is_scanning,
                store=0  # Don't store packets in memory
            )
            
        except Exception as e:
            print(f"Error in wireless scanning: {e}")
            self.is_scanning = False
    
    def stop_scanning(self):
        """
        Stop wireless scanning
        """
        self.is_scanning = False
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=2)
        print("Stopped wireless scanning")
    
    def get_detected_devices(self) -> Dict:
        """
        Get all detected devices
        """
        # Convert datetime objects to strings for JSON serialization
        devices = {}
        for mac, info in self.detected_devices.items():
            devices[mac] = {
                'signal_strength': info['signal_strength'],
                'first_seen': info['first_seen'].isoformat(),
                'last_seen': info['last_seen'].isoformat(),
                'count': info['count'],
                'device_type': info['device_type']
            }
        return devices
    
    def clear_detected_devices(self):
        """
        Clear all detected devices
        """
        self.detected_devices.clear()
    
    def add_detection_callback(self, callback: Callable):
        """
        Add a callback function to be called when new devices are detected
        """
        self.callback_functions.append(callback)
    
    def remove_detection_callback(self, callback: Callable):
        """
        Remove a callback function
        """
        if callback in self.callback_functions:
            self.callback_functions.remove(callback)


# Global scanner instance
scanner = WirelessScanner()
