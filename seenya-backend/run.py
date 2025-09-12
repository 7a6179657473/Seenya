"""
Seenya Wireless Scanner - Main Application Entry Point
"""

import os
import sys
from app import create_app, socketio
from app.services.wireless_scanner import scanner


def setup_socketio_callbacks():
    """
    Set up SocketIO event handlers and scanner callbacks
    """
    
    @socketio.on('connect')
    def handle_connect():
        print('Client connected to SocketIO')
        
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected from SocketIO')
        
    def device_detection_callback(mac, device_info):
        """
        Callback function for new device detections
        Emit real-time updates to connected clients
        """
        # Convert datetime objects to strings for JSON serialization
        device_data = {
            'mac': mac,
            'signal_strength': device_info['signal_strength'],
            'first_seen': device_info['first_seen'].isoformat(),
            'last_seen': device_info['last_seen'].isoformat(),
            'count': device_info['count'],
            'device_type': device_info['device_type']
        }
        
        # Emit to all connected clients
        socketio.emit('device_detected', device_data)
        print(f"New device detected: {mac} ({device_info['device_type']})")
    
    # Register the callback with the scanner
    scanner.add_detection_callback(device_detection_callback)


def main():
    """
    Main application entry point
    """
    print("Starting Seenya Wireless Scanner...")
    print("Phase 1: MAC Address Detection Module")
    print("=" * 50)
    
    # Create Flask app
    app = create_app()
    
    # Set up SocketIO callbacks
    setup_socketio_callbacks()
    
    # Check if running with administrator privileges (required for packet capture on Windows)
    if os.name == 'nt':  # Windows
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("WARNING: Administrator privileges may be required for packet capture on Windows.")
            print("Consider running as administrator if you encounter permission errors.")
    
    print(f"\nServer starting on http://localhost:5000")
    print("API endpoints:")
    print("  GET  /health                    - Health check")
    print("  GET  /api/scanning/interfaces   - Get wireless interfaces")
    print("  POST /api/scanning/start        - Start scanning")
    print("  POST /api/scanning/stop         - Stop scanning")
    print("  GET  /api/scanning/status       - Get scanning status")
    print("  GET  /api/scanning/devices      - Get detected devices")
    print("  POST /api/scanning/devices/clear - Clear detected devices")
    print("\nWebSocket endpoint: ws://localhost:5000")
    print("=" * 50)
    
    # Run the application with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
