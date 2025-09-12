# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Seenya is a MAC address monitoring tool designed to detect and log wireless device MAC addresses, tracking when devices have been seen before. The project consists of two main components:

1. **Root-level Python CLI tool** (`default.py`) - Future implementation for wireless capture using aircrack-ng suite
2. **mac-monitoring-project** - Full-stack web application for MAC address monitoring with signal strength tracking

## Architecture

### Backend (Python Flask)
- **Entry point**: `mac-monitoring-project/backend/app.py`
- **Models**: Simple in-memory storage with `MacEntry` class
- **Routes**: RESTful API endpoints for MAC logging and retrieval
- **Logging**: File-based logging to `mac_log.txt`
- **No database**: Currently uses in-memory dictionary and file logging

### Frontend (Angular 12)
- **Framework**: Angular 12 with TypeScript
- **Components**: `MacMonitorComponent` for displaying MAC entries
- **Services**: `MacService` for HTTP API communication
- **Build target**: Standard Angular CLI setup

## Phase 1: MAC Address Detection - ✅ COMPLETED

Phase 1 implementation includes:
- Real-time wireless MAC address detection using scapy
- Modern Angular Material UI with responsive design
- WebSocket-based real-time communication
- Device type identification via OUI lookup
- Signal strength monitoring and packet counting
- Complete REST API with scanning controls

## Common Development Commands

### Quick Setup (Windows)
```batch
# Setup backend (run as Administrator)
setup-backend.bat

# Setup frontend (in new terminal)
setup-frontend.bat

# Start backend (run as Administrator)
start-backend.bat

# Start frontend (in new terminal)
start-frontend.bat
```

### Backend Development
```bash
# Navigate to backend directory
cd seenya-backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install Python dependencies
pip install -r requirements.txt

# Run Flask development server (runs on http://localhost:5000)
python run.py
```

### Frontend Development
```bash
# Navigate to frontend directory
cd seenya-frontend

# Install Node.js dependencies
npm install

# Start Angular development server (runs on http://localhost:4200)
npm start
# or: ng serve

# Build for production
npm run build:prod

# Run tests
npm test

# Run linting
npm run lint
```

### Testing API Endpoints
```bash
# Log a MAC address (POST)
curl -X POST http://localhost:5000/log_mac -H "Content-Type: application/json" -d '{"mac_address":"AA:BB:CC:DD:EE:FF","signal_strength":-45}'

# Retrieve MAC entries (GET)
curl http://localhost:5000/mac_entries
```

## Code Structure Notes

### Backend Issues to Address
1. **Import errors**: `mac_routes.py` uses relative imports (`from ..models.mac_entry`) but the directory structure doesn't support this
2. **Missing methods**: `MacEntry` class lacks `to_dict()` method used in routes
3. **Inconsistent logging**: Logger function signature doesn't match usage
4. **No timestamp handling**: `MacEntry` constructor expects `last_seen` but routes don't provide it

### Frontend Configuration
- Angular CLI version 12 with standard configuration
- HttpClient for API communication
- Component-based architecture with service layer
- API base URL hardcoded to `http://localhost:5000/api/macs` (differs from actual backend routes)

### Development Workflow
1. **Backend first**: Start Flask server to provide API endpoints
2. **Frontend second**: Start Angular dev server for UI development
3. **API contract**: Ensure frontend service URLs match backend routes
4. **CORS**: Flask-Cors is included in requirements for cross-origin requests

## Key Dependencies

### Backend
- Flask 2.1.2 (web framework)
- Flask-Cors 3.0.10 (cross-origin support)
- SQLAlchemy 1.4.27 (currently unused)
- pandas 1.3.3 (data processing)
- requests 2.26.0 (HTTP client)

### Frontend
- Angular 12.x (framework)
- TypeScript 4.2.0 (language)
- RxJS 6.6.0 (reactive programming)

## Future Implementation Notes

The root `default.py` is placeholder for the main CLI tool that will:
- Use aircrack-ng suite for wireless monitoring
- Create wireless access points
- Capture MAC addresses from nearby devices
- Integrate with the web-based monitoring system
- Target submission as Hak5 MK7 module

## File Structure
```
Seenya/
├── default.py                    # Future CLI implementation
├── WARP.md                      # This file
├── README.md                    # Project overview
└── mac-monitoring-project/      # Web application
    ├── backend/                 # Flask API server
    │   ├── app.py              # Main Flask application
    │   ├── models/mac_entry.py  # Data model
    │   ├── routes/mac_routes.py # API endpoints
    │   ├── utils/logger.py      # Logging utilities
    │   └── requirements.txt     # Python dependencies
    └── frontend/               # Angular web interface
        ├── src/app/           # Angular application
        ├── angular.json       # Angular CLI configuration
        ├── package.json       # Node.js dependencies
        └── tsconfig.json      # TypeScript configuration
```
