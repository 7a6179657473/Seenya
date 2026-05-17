"""
Flask Application Factory
"""

import os
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

socketio = SocketIO()

ALLOWED_ORIGINS = os.getenv("SEENYA_ALLOWED_ORIGINS", "http://localhost:3000").split(",")


def create_app():
    app = Flask(__name__)

    secret = os.getenv("SEENYA_SECRET_KEY")
    if not secret:
        raise RuntimeError(
            "SEENYA_SECRET_KEY environment variable is not set. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    app.config['SECRET_KEY'] = secret

    CORS(app, origins=ALLOWED_ORIGINS)
    socketio.init_app(app, cors_allowed_origins=ALLOWED_ORIGINS)

    from .routes.scanning_routes import scanning_bp
    app.register_blueprint(scanning_bp)

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'Seenya Wireless Scanner'}

    return app
