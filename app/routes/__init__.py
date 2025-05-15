from .auth import api as auth_bp
from .product import api as product_bp
from .order import api as order_bp
from .cart import api as cart_bp
from .review import api as review_bp

from .payment import api as payment_bp
from .admin import api as admin_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(review_bp, url_prefix='/api/reviews')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
