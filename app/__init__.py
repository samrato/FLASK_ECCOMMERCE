from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from .config import Config
from .extensions import db, ma
from .routes import register_routes

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    Mail(app)
    
    # Register routes
    register_routes(app)
    
    return app