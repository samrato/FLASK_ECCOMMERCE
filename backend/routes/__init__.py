from flask import Blueprint

# Create all blueprints here to avoid circular imports
auth_bp = Blueprint('auth', __name__)
# user_bp = Blueprint('user', __name__)
product_bp = Blueprint('product', __name__)
order_bp = Blueprint('order', __name__)
cart_bp = Blueprint('cart', __name__)
review_bp = Blueprint('review', __name__)
# category_bp = Blueprint('category', __name__)
payment_bp = Blueprint('payment', __name__)
admin_bp = Blueprint('admin', __name__)

def register_routes(app):
    """Register all routes with the Flask app"""
    from . import auth,  product, order, cart, review, payment, admin
    
    # Register blueprints with the app
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    # app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    # app.register_blueprint(category_bp, url_prefix='/api/categories')
    app.register_blueprint(payment_bp, url_prefix='/api/payment')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')