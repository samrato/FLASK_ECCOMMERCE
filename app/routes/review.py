from flask import request, jsonify,Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.review import Review, review_schema, reviews_schema
from app.models.product import Product
from app.models.order import Order, OrderItem
api = Blueprint('reviews', __name__)

@api.route('/products/<int:product_id>/reviews', methods=['GET'])
def get_product_reviews(product_id):
    reviews = Review.query.filter_by(
        product_id=product_id,
        is_approved=True
    ).order_by(Review.created_at.desc()).all()
    return reviews_schema.jsonify(reviews), 200

@api.route('/products/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(product_id):
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # Check if user has purchased the product
    has_purchased = db.session.query(Order).join(OrderItem).filter(
        Order.user_id == current_user,
        OrderItem.product_id == product_id,
        Order.status == 'delivered'
    ).first()
    
    if not has_purchased:
        return jsonify({'message': 'You must purchase the product before reviewing'}), 403
    
    # Check if user already reviewed this product
    existing_review = Review.query.filter_by(
        user_id=current_user,
        product_id=product_id
    ).first()
    
    if existing_review:
        return jsonify({'message': 'You have already reviewed this product'}), 400
    
    review = Review(
        user_id=current_user,
        product_id=product_id,
        rating=data['rating'],
        title=data.get('title'),
        comment=data.get('comment')
    )
    
    db.session.add(review)
    db.session.commit()
    
    return review_schema.jsonify(review), 201

@api.route('/reviews/<int:id>', methods=['PUT'])
@jwt_required()
def update_review(id):
    current_user = get_jwt_identity()
    review = Review.query.get_or_404(id)
    
    if review.user_id != current_user:
        return jsonify({'message': 'You can only update your own reviews'}), 403
    
    data = request.get_json()
    review.rating = data.get('rating', review.rating)
    review.title = data.get('title', review.title)
    review.comment = data.get('comment', review.comment)
    
    db.session.commit()
    return review_schema.jsonify(review), 200

@api.route('/reviews/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_review(id):
    current_user = get_jwt_identity()
    review = Review.query.get_or_404(id)
    
    if review.user_id != current_user:
        return jsonify({'message': 'You can only delete your own reviews'}), 403
    
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted'}), 200