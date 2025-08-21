# app/app.py
from flask import Flask
from app.blueprints.main.routes import main_bp
from flask_session import Session  # Optional, for server-side sessions

def create_app():
    app = Flask(__name__)
    
    # Secret key for sessions and flash messages
    app.secret_key = "supersecretkey"  # Change in production
    
    # Optional: server-side sessions
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    # Register blueprint
    app.register_blueprint(main_bp)

    return app
