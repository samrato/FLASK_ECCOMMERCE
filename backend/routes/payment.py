from flask import request, jsonify,Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import db
from backend.models.order import Order
from backend.services.payment import PaymentService
from backend .routes import payment_bp

@payment_bp.route('/orders/<int:id>/payment', methods=['POST'])
@jwt_required()
def create_payment(id):
    current_user = get_jwt_identity()
    order = Order.query.filter_by(id=id, user_id=current_user).first_or_404()
    
    if order.payment_status != 'pending':
        return jsonify({'message': 'Payment already processed'}), 400
    
    payment_data = PaymentService.create_payment_intent(order)
    if not payment_data:
        return jsonify({'message': 'Payment processing error'}), 500
    
    return jsonify({"Message":"Payment is succesfully Done"},payment_data), 200

@payment_bp.route('/payment/webhook', methods=['POST'])
def payment_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    result = PaymentService.handle_webhook(payload, sig_header)
    if not result:
        return jsonify({'message': 'Invalid webhook'}), 400
    
    order_id, status = result
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'message': 'Order not found'}), 404
    
    if status == 'succeeded':
        order.payment_status = 'paid'
        order.status = 'processing'
    elif status == 'failed':
        order.payment_status = 'failed'
    
    db.session.commit()
    return jsonify({'message': 'Webhook received'}), 200