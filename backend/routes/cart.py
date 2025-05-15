from flask import request, jsonify,Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import db
from backend.models.cart import Cart, CartItem, cart_schema, cart_item_schema, cart_items_schema
from backend.models.product import Product, ProductVariant
from backend.utils.decorators import validate_schema
from.import cart_bp

@cart_bp.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    current_user = get_jwt_identity()
    cart = Cart.query.filter_by(user_id=current_user).first()
    
    if not cart:
        cart = Cart(user_id=current_user)
        db.session.add(cart)
        db.session.commit()
    
    return cart_schema.jsonify(cart), 200

@cart_bp.route('/cart/items', methods=['POST'])
@jwt_required()
@validate_schema(cart_item_schema)
def add_to_cart():
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # Get or create cart
    cart = Cart.query.filter_by(user_id=current_user).first()
    if not cart:
        cart = Cart(user_id=current_user)
        db.session.add(cart)
    
    # Check if product exists
    product = Product.query.get(data['product_id'])
    if not product or not product.is_active:
        return jsonify({'message': 'Product not available'}), 404
    
    # Check variant if provided
    variant = None
    if data.get('variant_id'):
        variant = ProductVariant.query.filter_by(
            id=data['variant_id'],
            product_id=data['product_id']
        ).first()
        if not variant:
            return jsonify({'message': 'Invalid product variant'}), 400
    
    # Check if item already in cart
    existing_item = None
    if variant:
        existing_item = CartItem.query.filter_by(
            cart_id=cart.id,
            product_id=data['product_id'],
            variant_id=data['variant_id']
        ).first()
    else:
        existing_item = CartItem.query.filter_by(
            cart_id=cart.id,
            product_id=data['product_id']
        ).first()
    
    if existing_item:
        existing_item.quantity += data.get('quantity', 1)
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=data['product_id'],
            variant_id=data.get('variant_id'),
            quantity=data.get('quantity', 1)
        )
        db.session.add(new_item)
    
    db.session.commit()
    return jsonify({'message': 'Item added to cart'}), 200

@cart_bp.route('/cart/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(item_id):
    current_user = get_jwt_identity()
    cart = Cart.query.filter_by(user_id=current_user).first()
    
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404
    
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        return jsonify({'message': 'Item not found in cart'}), 404
    
    quantity = request.json.get('quantity')
    if quantity and quantity > 0:
        item.quantity = quantity
        db.session.commit()
        return cart_item_schema.jsonify(item), 200
    else:
        return jsonify({'message': 'Invalid quantity'}), 400

@cart_bp.route('/cart/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(item_id):
    current_user = get_jwt_identity()
    cart = Cart.query.filter_by(user_id=current_user).first()
    
    if not cart:
        return jsonify({'message': 'Cart not found'}), 404
    
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        return jsonify({'message': 'Item not found in cart'}), 404
    
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'}), 200