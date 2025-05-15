from app.extensions import db,ma
from datetime import datetime
from enum import Enum

class OrderStatus(Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    order_number = db.Column(db.String(50), unique=True)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    subtotal = db.Column(db.Float)
    tax = db.Column(db.Float)
    shipping_cost = db.Column(db.Float)
    total = db.Column(db.Float)
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(50), default='pending')
    shipping_address = db.Column(db.JSON)
    billing_address = db.Column(db.JSON)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variants.id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    discount_price = db.Column(db.Float)
    
    product = db.relationship('Product')
    variant = db.relationship('ProductVariant')

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        load_instance = True
        include_fk = True

class OrderItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderItem
        load_instance = True

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
order_item_schema = OrderItemSchema()
order_items_schema = OrderItemSchema(many=True)