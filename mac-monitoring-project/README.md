# mac-monitoring-project

This project is designed to monitor MAC addresses along with their signal strengths. It consists of a backend built with Python and Flask, and a frontend developed using Angular.

## Project Structure

```
mac-monitoring-project
├── backend
│   ├── app.py                # Main entry point for the backend application
│   ├── requirements.txt      # Lists dependencies for the backend
│   ├── models
│   │   └── mac_entry.py      # Defines the MacEntry class for MAC address entries
│   ├── routes
│   │   └── mac_routes.py     # Contains route definitions for MAC address logging
│   ├── utils
│   │   └── logger.py         # Utility functions for logging activities
│   └── README.md             # Documentation for the backend
├── frontend
│   ├── angular.json          # Configuration file for the Angular project
│   ├── package.json          # Lists dependencies for the frontend
│   ├── tsconfig.json         # TypeScript configuration file
│   ├── src
│   │   ├── app
│   │   │   ├── app.component.ts          # Main application component
│   │   │   ├── app.module.ts             # Main application module
│   │   │   ├── mac-monitor
│   │   │   │   ├── mac-monitor.component.ts  # Component for monitoring MAC addresses
│   │   │   │   └── mac-monitor.component.html # HTML template for the MAC monitor component
│   │   │   └── services
│   │   │       └── mac.service.ts         # Service for communicating with the backend
│   │   └── assets                          # Directory for static assets
│   └── README.md             # Documentation for the frontend
└── README.md                # Overall documentation for the project
```

## Backend Setup

1. Navigate to the `backend` directory.
2. Install the required dependencies using:
   ```
   pip install -r requirements.txt
   ```
3. Run the backend application:
   ```
   python app.py
   ```

## Frontend Setup

1. Navigate to the `frontend` directory.
2. Install the required dependencies using:
   ```
   npm install
   ```
3. Start the Angular application:
   ```
   ng serve
   ```

## Usage

- The backend API will handle requests for logging and retrieving MAC addresses.
- The frontend will display the monitored MAC addresses and their signal strengths in real-time.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.