from flask import request, jsonify,Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import db
from backend.models.user import User, UserSchema
from backend.models.product import Product, ProductSchema
from backend.models.order import Order, OrderSchema, OrderStatus
from backend.models.review import Review, ReviewSchema
from backend.utils.decorators import admin_required
from.import admin_bp

users_schema = UserSchema(many=True)
products_schema = ProductSchema(many=True)
orders_schema = OrderSchema(many=True)
reviews_schema = ReviewSchema(many=True)

@admin_bp.route('/admin/users', methods=['GET'])
@jwt_required()
@admin_required
def admin_get_users():
    users = User.query.all()
    return users_schema.jsonify(users), 200

@admin_bp.route('/admin/users/<int:id>', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    
    if 'is_admin' in data:
        user.is_admin = data['is_admin']
    if 'is_seller' in data:
        user.is_seller = data['is_seller']
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    db.session.commit()
    return UserSchema().jsonify(user), 200

@admin_bp.route('/admin/products', methods=['GET'])
@jwt_required()
@admin_required
def admin_get_products():
    products = Product.query.all()
    return products_schema.jsonify(products), 200

@admin_bp.route('/admin/orders', methods=['GET'])
@jwt_required()
@admin_required
def admin_get_orders():
    status = request.args.get('status')
    query = Order.query
    
    if status:
        query = query.filter_by(status=status)
    
    orders = query.order_by(Order.created_at.desc()).all()
    return orders_schema.jsonify(orders), 200

@admin_bp.route('/admin/orders/<int:id>/status', methods=['PUT'])
@jwt_required()
@admin_required
def admin_update_order_status(id):
    order = Order.query.get_or_404(id)
    status = request.json.get('status')
    
    if status not in [s.value for s in OrderStatus]:
        return jsonify({'message': 'Invalid status'}), 400
    
    order.status = status
    db.session.commit()
    return OrderSchema().jsonify(order), 200

@admin_bp.route('/admin/reviews', methods=['GET'])
@jwt_required()
@admin_required
def admin_get_reviews():
    is_approved = request.args.get('is_approved')
    query = Review.query
    
    if is_approved is not None:
        query = query.filter_by(is_approved=is_approved.lower() == 'true')
    
    reviews = query.order_by(Review.created_at.desc()).all()
    return reviews_schema.jsonify(reviews), 200

@admin_bp.route('/admin/reviews/<int:id>/approve', methods=['PUT'])
@jwt_required()
@admin_required
def admin_approve_review(id):
    review = Review.query.get_or_404(id)
    review.is_approved = True
    db.session.commit()
    return ReviewSchema().jsonify(review), 200

@admin_bp.route('/admin/stats', methods=['GET'])
@jwt_required()
@admin_required
def admin_get_stats():
    from sqlalchemy import func, extract
    
    # Basic stats
    total_users = User.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(func.sum(Order.total)).scalar() or 0
    
    # Monthly revenue
    monthly_revenue = db.session.query(
        extract('year', Order.created_at).label('year'),
        extract('month', Order.created_at).label('month'),
        func.sum(Order.total).label('revenue')
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    return jsonify({
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'monthly_revenue': [
            {'year': r.year, 'month': r.month, 'revenue': float(r.revenue or 0)}
            for r in monthly_revenue
        ]
    }), 200