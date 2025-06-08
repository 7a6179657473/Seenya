# MAC Address Monitoring Project

This project is designed to monitor MAC addresses along with their signal strengths. It consists of a backend built with Python (Flask) and a frontend developed using Angular.

## Project Structure

- **backend/**: Contains the backend application files.
  - **app.py**: Main entry point for the backend application.
  - **requirements.txt**: Lists the dependencies required for the backend.
  - **models/**: Contains the data models.
    - **mac_entry.py**: Defines the MacEntry class for MAC address entries.
  - **routes/**: Contains route definitions for the backend.
    - **mac_routes.py**: Handles requests for logging and retrieving MAC addresses.
  - **utils/**: Contains utility functions.
    - **logger.py**: Provides logging functionalities.
  - **README.md**: Documentation for the backend.

- **frontend/**: Contains the frontend application files.
  - **angular.json**: Configuration file for the Angular project.
  - **package.json**: Lists the dependencies for the frontend.
  - **tsconfig.json**: TypeScript configuration file.
  - **src/**: Contains the source code for the Angular application.
    - **app/**: Contains the main application components and services.
      - **app.component.ts**: Main application component.
      - **app.module.ts**: Main application module.
      - **mac-monitor/**: Contains the MAC monitor component.
        - **mac-monitor.component.ts**: Displays monitored MAC addresses.
        - **mac-monitor.component.html**: HTML template for the MAC monitor component.
      - **services/**: Contains services for API communication.
        - **mac.service.ts**: Handles communication with the backend API.
    - **assets/**: Directory for static assets.
  - **README.md**: Documentation for the frontend.

## Setup Instructions

### Backend

1. Navigate to the `backend` directory.
2. Install the required dependencies using:
   ```
   pip install -r requirements.txt
   ```
3. Run the backend application:
   ```
   python app.py
   ```

### Frontend

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
- The frontend application will provide a user interface to display the monitored MAC addresses and their signal strengths.

## Contributing

Feel free to submit issues or pull requests to improve the project!