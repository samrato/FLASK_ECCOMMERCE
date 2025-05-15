from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from .config import Config
from .extensions import db, ma, mail

def create_app(config_class=Config):
    # Create Flask application instance
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    mail.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    # Import models within app context
    with app.app_context():
        import backend.models
    
    # Register routes
    from .routes import register_routes
    register_routes(app)  # Pass the app instance here
    
    return app