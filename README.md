# Seenya - Wireless MAC Address Scanner

**Phase 1: MAC Address Detection Module** ✅ **COMPLETED**

Seenya is a powerful wireless device detection tool that captures and monitors MAC addresses of devices within wireless range. Built with Python (Flask) backend and Angular Material frontend, it provides real-time detection and logging capabilities.

## 🚀 Current Status: Phase 1 Complete

### ✅ What's Working:
- Real-time wireless MAC address detection using scapy
- Modern Angular Material UI for device monitoring
- WebSocket-based real-time updates
- Device type identification (OUI lookup)
- Signal strength monitoring
- Packet count tracking
- First/last seen timestamps

### 📋 Features:
- **Backend**: Python Flask API with SocketIO for real-time communication
- **Frontend**: Angular 16 with Material Design components
- **Scanning**: Wireless packet capture using scapy library
- **Real-time**: Live updates via WebSocket connections
- **Cross-platform**: Windows support with PowerShell setup scripts

## 🛠️ Quick Start

### Prerequisites
- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **Administrator privileges** (required for packet capture on Windows)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Seenya
   ```

2. **Setup Backend** (Run as Administrator)
   ```bash
   setup-backend.bat
   ```

3. **Setup Frontend**
   ```bash
   setup-frontend.bat
   ```

### Running the Application

1. **Start Backend** (Run as Administrator)
   ```bash
   start-backend.bat
   ```
   Backend will be available at: http://localhost:5000

2. **Start Frontend** (In another terminal)
   ```bash
   start-frontend.bat
   ```
   Frontend will be available at: http://localhost:4200

3. **Open your browser** and navigate to http://localhost:4200

## 📁 Project Structure

```
Seenya/
├── seenya-backend/           # Python Flask API
│   ├── app/
│   │   ├── services/         # Wireless scanning service
│   │   ├── routes/          # API endpoints
│   │   ├── models/          # Data models
│   │   └── utils/           # Utilities
│   ├── requirements.txt     # Python dependencies
│   └── run.py              # Main application entry
├── seenya-frontend/         # Angular Material UI
│   ├── src/app/
│   │   ├── components/      # UI components
│   │   ├── services/        # API services
│   │   └── models/         # TypeScript interfaces
│   └── package.json        # Node.js dependencies
├── setup-backend.bat       # Backend setup script
├── setup-frontend.bat      # Frontend setup script
├── start-backend.bat       # Backend start script
├── start-frontend.bat      # Frontend start script
└── WARP.md                # Development guidance
```

## 🔧 API Endpoints

- `GET /health` - Health check
- `GET /api/scanning/interfaces` - Get wireless interfaces
- `POST /api/scanning/start` - Start scanning
- `POST /api/scanning/stop` - Stop scanning
- `GET /api/scanning/status` - Get scanning status
- `GET /api/scanning/devices` - Get detected devices
- `POST /api/scanning/devices/clear` - Clear detected devices
- `WebSocket: ws://localhost:5000` - Real-time device updates

## 🎯 Roadmap

### Phase 2: Logging & Database (Next)
- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Historical device logs
- [ ] Device tracking over time
- [ ] Alert system for known/new devices
- [ ] Export functionality (CSV, JSON)

### Phase 3: Advanced Features
- [ ] Access Point creation mode
- [ ] Device fingerprinting
- [ ] Network mapping
- [ ] Mobile app companion

### Phase 4: Hardware Integration
- [ ] Hak5 Pineapple module
- [ ] Raspberry Pi deployment
- [ ] Portable hardware solution

## 🔒 Security & Legal Notice

**Important**: This tool is designed for educational and authorized security testing purposes only. Ensure you have explicit permission before scanning networks you don't own. Wireless monitoring may be subject to local laws and regulations.

## 🤝 Contributing

Contributions are welcome! This project is open source and will remain that way.

## 📄 License

Open source - feel free to contribute and suggest improvements!

---

**Note**: Administrator privileges are required on Windows for packet capture functionality. The tool currently works best in monitor mode on wireless interfaces that support it.
