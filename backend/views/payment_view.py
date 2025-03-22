from flask import Blueprint, request, jsonify
from ..controllers import token_required, role_required

# Crear el Blueprint para las rutas de pagos
payment_bp = Blueprint('payments', __name__, url_prefix='/api/payments')

# Ruta para procesar un nuevo pago
@payment_bp.route('', methods=['POST'])
@token_required
def process_payment(current_user):
    data = request.get_json()
    
    # Validar datos de entrada
    if not data or not data.get('booking_id') or not data.get('amount') or not data.get('payment_method'):
        return jsonify({'message': 'Missing required fields!'}), 400
    
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.payment_service import PaymentService
    from ..services.booking_service import BookingService
    
    try:
        booking_service = BookingService()
        payment_service = PaymentService()
        
        # Verificar si la reserva existe y pertenece al usuario
        booking = booking_service.get_booking_by_id(data.get('booking_id'))
        if not booking:
            return jsonify({'message': 'Booking not found!'}), 404
        
        # Solo el propietario o un admin puede pagar
        if booking.user_id != current_user.id and current_user.role != 'admin':
            return jsonify({'message': 'Unauthorized to pay for this booking!'}), 403
        
        # Verificar estado de la reserva
        if booking.status == 'cancelled':
            return jsonify({'message': 'Cannot pay for a cancelled booking!'}), 400
        
        # Procesar el pago
        result = payment_service.process_payment(
            booking_id=data.get('booking_id'),
            user_id=current_user.id,
            amount=data.get('amount'),
            payment_method=data.get('payment_method'),
            card_last_digits=data.get('card_last_digits'),
            billing_address=data.get('billing_address')
        )
        
        return jsonify({
            'message': 'Payment processed successfully!',
            'payment_id': result['payment_id'],
            'transaction_id': result['transaction_id'],
            'status': result['status'],
            'booking_status': result['booking_status']
        }), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para obtener todos los pagos (solo admin)
@payment_bp.route('', methods=['GET'])
@token_required
@role_required(['admin'])
def get_all_payments(current_user):
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.payment_service import PaymentService
    
    try:
        payment_service = PaymentService()
        payments = payment_service.get_all_payments()
        
        result = []
        for payment in payments:
            result.append({
                'id': payment.id,
                'booking_id': payment.booking_id,
                'user_id': payment.user_id,
                'user_name': payment.user.name,
                'amount': payment.amount,
                'payment_method': payment.payment_method,
                'transaction_id': payment.transaction_id,
                'status': payment.status,
                'payment_date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'payments': result})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para obtener pagos de una reserva específica
@payment_bp.route('/booking/<int:booking_id>', methods=['GET'])
@token_required
def get_booking_payments(current_user, booking_id):
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.payment_service import PaymentService
    from ..services.booking_service import BookingService
    
    try:
        booking_service = BookingService()
        payment_service = PaymentService()
        
        # Verificar si la reserva existe
        booking = booking_service.get_booking_by_id(booking_id)
        if not booking:
            return jsonify({'message': 'Booking not found!'}), 404
        
        # Solo el propietario o un admin puede ver los pagos
        if booking.user_id != current_user.id and current_user.role != 'admin':
            return jsonify({'message': 'Unauthorized to view these payments!'}), 403
        
        # Obtener los pagos
        payments = payment_service.get_booking_payments(booking_id)
        
        result = []
        for payment in payments:
            result.append({
                'id': payment.id,
                'amount': payment.amount,
                'payment_method': payment.payment_method,
                'transaction_id': payment.transaction_id,
                'status': payment.status,
                'payment_date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Obtener el estado de pago de la reserva
        payment_status = payment_service.check_booking_payment_status(booking_id)
        
        return jsonify({
            'booking_id': booking_id,
            'payments': result,
            'payment_status': payment_status
        })
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para obtener pagos del usuario actual
@payment_bp.route('/my-payments', methods=['GET'])
@token_required
def get_my_payments(current_user):
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.payment_service import PaymentService
    
    try:
        payment_service = PaymentService()
        payments = payment_service.get_user_payments(current_user.id)
        
        result = []
        for payment in payments:
            result.append({
                'id': payment.id,
                'booking_id': payment.booking_id,
                'amount': payment.amount,
                'payment_method': payment.payment_method,
                'transaction_id': payment.transaction_id,
                'status': payment.status,
                'payment_date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'payments': result})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para procesar un reembolso (solo admin)
@payment_bp.route('/<int:payment_id>/refund', methods=['POST'])
@token_required
@role_required(['admin'])
def refund_payment(current_user, payment_id):
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.payment_service import PaymentService
    
    try:
        payment_service = PaymentService()
        result = payment_service.refund_payment(payment_id)
        
        if result:
            return jsonify({'message': 'Payment refunded successfully!'})
        else:
            return jsonify({'message': 'Cannot refund this payment!'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para generar un recibo de pago
@payment_bp.route('/<int:payment_id>/receipt', methods=['GET'])
@token_required
def generate_payment_receipt(current_user, payment_id):
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.payment_service import PaymentService
    
    try:
        payment_service = PaymentService()
        payment = payment_service.get_payment_by_id(payment_id)
        
        if not payment:
            return jsonify({'message': 'Payment not found!'}), 404
        
        # Solo el usuario que realizó el pago o un admin puede ver el recibo
        if payment.user_id != current_user.id and current_user.role != 'admin':
            return jsonify({'message': 'Unauthorized to view this receipt!'}), 403
        
        # Generar datos del recibo
        receipt_data = payment_service.generate_payment_receipt(payment_id)
        
        if not receipt_data:
            return jsonify({'message': 'Error generating receipt!'}), 500
        
        # En un caso real, aquí se generaría un PDF y se enviaría como archivo
        # Por ahora, devolvemos los datos en JSON
        return jsonify({'receipt': receipt_data})
    except Exception as e:
        return jsonify({'message': str(e)}), 500