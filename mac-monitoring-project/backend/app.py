from flask import Flask
from routes.mac_routes import mac_routes

app = Flask(__name__)

# Register the MAC routes
app.register_blueprint(mac_routes)

@app.route('/')
def home():
    return "Welcome to the MAC Address Monitoring API!"

if __name__ == '__main__':
    app.run(debug=True)