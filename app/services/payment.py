import stripe
from flask import current_app

class PaymentService:
    @staticmethod
    def create_payment_intent(order):
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),  # Amount in cents
                currency='usd',
                metadata={
                    'order_id': order.id,
                    'order_number': order.order_number
                }
            )
            return {
                'client_secret': intent.client_secret,
                'publishable_key': current_app.config['STRIPE_PUBLISHABLE_KEY']
            }
        except Exception as e:
            current_app.logger.error(f'Stripe error: {str(e)}')
            return None
    
    @staticmethod
    def handle_webhook(payload, sig_header):
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        endpoint_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            current_app.logger.error(f'Invalid payload: {str(e)}')
            return None
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            current_app.logger.error(f'Invalid signature: {str(e)}')
            return None
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            order_id = payment_intent['metadata']['order_id']
            return order_id, 'succeeded'
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            order_id = payment_intent['metadata']['order_id']
            return order_id, 'failed'
        
        return None