# MAC Address Monitoring Project - Backend

This project is designed to monitor MAC addresses along with their signal strengths. It provides a backend service built with Flask that logs the latest time each MAC address was seen.

## Project Structure

- **app.py**: Main entry point for the backend application. Initializes the Flask app and sets up routes.
- **requirements.txt**: Lists the dependencies required for the backend application.
- **models/mac_entry.py**: Defines the `MacEntry` class representing a MAC address entry with properties for MAC address, signal strength, and last seen timestamp.
- **routes/mac_routes.py**: Contains route definitions for logging MAC addresses and retrieving logs.
- **utils/logger.py**: Provides utility functions for logging activities related to MAC address monitoring.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd mac-monitoring-project/backend
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

## Usage

- The backend API allows you to log MAC addresses and retrieve the logs. Refer to the route definitions in `mac_routes.py` for available endpoints and their usage.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.