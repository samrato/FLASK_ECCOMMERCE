from backend.extensions import db, ma
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime
from backend.models.product import Product
from backend.models.review import Review
from backend.models.order import Order
from backend.models.cart import CartItem
from marshmallow import fields

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_seller = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    products = db.relationship(Product, backref='seller', lazy=True)
    orders = db.relationship(Order, backref='customer', lazy=True)
    reviews = db.relationship(Review, backref='user', lazy=True)
    cart_items = db.relationship(CartItem, backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_tokens(self):
        # Embed role claims in JWT
        additional_claims = {
            "is_admin": self.is_admin,
            "is_seller": self.is_seller
        }
        access_token = create_access_token(identity=str(self.id), additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=str(self.id))
        return access_token, refresh_token

    def __repr__(self):
        return f'<User {self.username}>'

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)

    # Add password field explicitly for input (load only)
    password = fields.String(required=True, load_only=True)
