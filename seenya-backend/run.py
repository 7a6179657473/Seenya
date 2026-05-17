"""
Seenya Wireless Scanner - Main Application Entry Point
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()
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
    
    host = os.getenv("SEENYA_HOST", "127.0.0.1")
    port = int(os.getenv("SEENYA_PORT", "5000"))
    debug = os.getenv("SEENYA_DEBUG", "false").lower() == "true"

    print(f"\nServer starting on http://{host}:{port}")
    print("API endpoints:")
    print(f"  GET  /health                    - Health check")
    print(f"  GET  /api/scanning/interfaces   - Get wireless interfaces")
    print(f"  POST /api/scanning/start        - Start scanning")
    print(f"  POST /api/scanning/stop         - Stop scanning")
    print(f"  GET  /api/scanning/status       - Get scanning status")
    print(f"  GET  /api/scanning/devices      - Get detected devices")
    print(f"  POST /api/scanning/devices/clear - Clear detected devices")
    print(f"\nWebSocket endpoint: ws://{host}:{port}")
    print("=" * 50)

    if debug:
        print("WARNING: Debug mode is enabled. Do not use in production.")

    socketio.run(app, host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
