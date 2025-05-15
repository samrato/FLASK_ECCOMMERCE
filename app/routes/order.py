from flask import request, jsonify,Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.order import order_schema, orders_schema, order_item_schema
from app.models.cart import Cart, CartItem
from app.models.product import Product, ProductVariant
from app.services.payment import PaymentService
api = Blueprint('order', __name__)

@api.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    current_user = get_jwt_identity()
    orders = Order.query.filter_by(user_id=current_user).order_by(Order.created_at.desc()).all()
    return orders_schema.jsonify(orders), 200

@api.route('/orders/<int:id>', methods=['GET'])
@jwt_required()
def get_order(id):
    current_user = get_jwt_identity()
    order = Order.query.filter_by(id=id, user_id=current_user).first_or_404()
    return order_schema.jsonify(order), 200

@api.route('/orders', methods=['POST'])
@jwt_required()
def create_order():
    current_user = get_jwt_identity()
    
    # Get user's cart
    cart = Cart.query.filter_by(user_id=current_user).first()
    if not cart or not cart.items:
        return jsonify({'message': 'Cart is empty'}), 400
    
    # Validate cart items
    order_items = []
    subtotal = 0
    
    for item in cart.items:
        product = Product.query.get(item.product_id)
        
        # Check product availability
        if not product or not product.is_active:
            return jsonify({'message': f'Product {product.name if product else ""} is no longer available'}), 400
        
        # Check stock
        if product.stock < item.quantity:
            return jsonify({'message': f'Not enough stock for {product.name}'}), 400
        
        # Check variant if exists
        variant = None
        if item.variant_id:
            variant = ProductVariant.query.filter_by(
                id=item.variant_id,
                product_id=item.product_id
            ).first()
            if not variant:
                return jsonify({'message': 'Invalid product variant'}), 400
            if variant.stock < item.quantity:
                return jsonify({'message': f'Not enough stock for variant {variant.value}'}), 400
        
        # Calculate price
        price = product.discount_price if product.discount_price else product.price
        if variant:
            price += variant.additional_price
        
        order_items.append({
            'product_id': product.id,
            'variant_id': variant.id if variant else None,
            'quantity': item.quantity,
            'price': price,
            'product': product,
            'variant': variant
        })
        
        subtotal += price * item.quantity
    
    # Create order
    order = Order(
        user_id=current_user,
        order_number=generate_order_number(),
        subtotal=subtotal,
        tax=0,  # Calculate tax based on location
        shipping_cost=0,  # Calculate shipping
        total=subtotal,  # Will be updated with tax and shipping
        shipping_address=request.json.get('shipping_address'),
        billing_address=request.json.get('billing_address', request.json.get('shipping_address')),
        notes=request.json.get('notes')
    )
    
    db.session.add(order)
    
    # Create order items and update stock
    for item in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product_id'],
            variant_id=item['variant_id'],
            quantity=item['quantity'],
            price=item['price'],
            discount_price=item['product'].discount_price
        )
        db.session.add(order_item)
        
        # Update product stock
        item['product'].stock -= item['quantity']
        if item['variant']:
            item['variant'].stock -= item['quantity']
    
    # Clear cart
    CartItem.query.filter_by(cart_id=cart.id).delete()
    db.session.commit()
    
    return order_schema.jsonify(order), 201

@api.route('/orders/<int:id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(id):
    current_user = get_jwt_identity()
    order = Order.query.filter_by(id=id, user_id=current_user).first_or_404()
    
    if order.status != OrderStatus.PENDING.value:
        return jsonify({'message': 'Order cannot be cancelled at this stage'}), 400
    
    order.status = OrderStatus.CANCELLED.value
    
    # Restore stock
    for item in order.items:
        product = Product.query.get(item.product_id)
        product.stock += item.quantity
        
        if item.variant_id:
            variant = ProductVariant.query.get(item.variant_id)
            variant.stock += item.quantity
    
    db.session.commit()
    return order_schema.jsonify(order), 200

def generate_order_number():
    from datetime import datetime
    now = datetime.now()
    return f"ORD-{now.strftime('%Y%m%d')}-{now.timestamp()}"