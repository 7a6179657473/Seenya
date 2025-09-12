"""
Flask Application Factory
"""

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

# Global SocketIO instance
socketio = SocketIO()


def create_app():
    """
    Create and configure Flask application
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'seenya-wireless-scanner-2025'
    
    # Enable CORS for all routes
    CORS(app, origins="*")
    
    # Initialize SocketIO
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register blueprints
    from .routes.scanning_routes import scanning_bp
    app.register_blueprint(scanning_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'Seenya Wireless Scanner'}
    
    return app
