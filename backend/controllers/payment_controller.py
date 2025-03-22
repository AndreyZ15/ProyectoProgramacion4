from flask import request, jsonify, send_file
from datetime import datetime
import uuid
import os
from io import BytesIO

from ..models.payment import Payment
from ..services.payment_service import PaymentService
from ..services.booking_service import BookingService
from ..services.package_service import PackageService
from ..services.user_service import UserService
from ..utils.pdf_generator import generate_receipt_pdf
from . import token_required, role_required

payment_service = PaymentService()
booking_service = BookingService()
package_service = PackageService()
user_service = UserService()

# Procesar pago de una reserva
@token_required
def process_payment(current_user):
    data = request.get_json()
    
    # Validar datos de entrada
    if not data or not data.get('booking_id') or not data.get('payment_method'):
        return jsonify({'message': 'Missing required fields!'}), 400
    
    # Verificar si la reserva existe y pertenece al usuario
    booking = booking_service.get_booking_by_id(data.get('booking_id'))
    
    if not booking:
        return jsonify({'message': 'Booking not found!'}), 404
    
    if booking.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized access!'}), 403
    
    # Verificar si la reserva ya fue pagada
    if payment_service.is_booking_paid(data.get('booking_id')):
        return jsonify({'message': 'This booking is already paid!'}), 400
    
    # Obtener el paquete y calcular el precio
    package = package_service.get_package_by_id(booking.package_id)
    if not package:
        return jsonify({'message': 'Package not found!'}), 404
    
    # Calcular precio base
    base_price = package.price * booking.number_of_travelers
    
    # Aplicar descuento para clientes VIP
    discount = 0
    if current_user.role == 'vip':
        discount = base_price * 0.1  # 10% de descuento para VIP
    
    total_amount = base_price - discount
    
    # Procesar el pago (simulado)
    transaction_id = str(uuid.uuid4())
    payment_status = "completed"  # En un sistema real, esto vendría de la pasarela de pagos
    
    # Crear el registro de pago
    new_payment = Payment(
        booking_id=data.get('booking_id'),
        user_id=current_user.id,
        amount=total_amount,
        payment_date=datetime.now(),
        payment_method=data.get('payment_method'),
        transaction_id=transaction_id,
        status=payment_status,
        discount_applied=discount
    )
    
    payment_id = payment_service.create_payment(new_payment)
    
    # Actualizar estado de la reserva
    if payment_status == "completed":
        booking.status = "confirmed"
        booking_service.update_booking(booking)
    
    return jsonify({
        'message': 'Payment processed successfully!',
        'payment_id': payment_id,
        'transaction_id': transaction_id,
        'amount': total_amount,
        'discount_applied': discount,
        'status': payment_status
    }), 201

# Obtener recibo de pago en PDF
@token_required
def get_payment_receipt(current_user, payment_id):
    payment = payment_service.get_payment_by_id(payment_id)
    
    if not payment:
        return jsonify({'message': 'Payment not found!'}), 404
    
    # Solo el propietario o admin puede ver/descargar el recibo
    if payment.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized access!'}), 403
    
    # Obtener datos necesarios para el recibo
    booking = booking_service.get_booking_by_id(payment.booking_id)
    package = package_service.get_package_by_id(booking.package_id)
    user = user_service.get_user_by_id(payment.user_id)
    
    # Datos para el PDF
    receipt_data = {
        'receipt_number': f"REC-{payment.id}",
        'transaction_id': payment.transaction_id,
        'date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
        'customer_name': user.name,
        'customer_email': user.email,
        'package_name': package.destination,
        'travel_date': booking.travel_date.strftime('%Y-%m-%d'),
        'number_of_travelers': booking.number_of_travelers,
        'base_amount': payment.amount + payment.discount_applied,
        'discount': payment.discount_applied,
        'total_amount': payment.amount,
        'payment_method': payment.payment_method,
        'status': payment.status
    }
    
    # Generar PDF
    pdf_buffer = generate_receipt_pdf(receipt_data)
    pdf_buffer.seek(0)
    
    return send_file(
        BytesIO(pdf_buffer.read()),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"receipt_{payment.id}.pdf"
    )

# Obtener todos los pagos (admin)
@token_required
@role_required(['admin'])
def get_all_payments(current_user):
    payments = payment_service.get_all_payments()
    output = []
    
    for payment in payments:
        payment_data = {
            'id': payment.id,
            'booking_id': payment.booking_id,
            'user_id': payment.user_id,
            'user_name': payment.user.name,
            'amount': payment.amount,
            'payment_date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
            'payment_method': payment.payment_method,
            'transaction_id': payment.transaction_id,
            'status': payment.status,
            'discount_applied': payment.discount_applied
        }
        output.append(payment_data)
    
    return jsonify({'payments': output})

# Obtener pagos de un usuario
@token_required
def get_user_payments(current_user):
    payments = payment_service.get_user_payments(current_user.id)
    output = []
    
    for payment in payments:
        # Obtener información adicional
        booking = booking_service.get_booking_by_id(payment.booking_id)
        package = package_service.get_package_by_id(booking.package_id)
        
        payment_data = {
            'id': payment.id,
            'booking_id': payment.booking_id,
            'package_destination': package.destination,
            'travel_date': booking.travel_date.strftime('%Y-%m-%d'),
            'amount': payment.amount,
            'payment_date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
            'payment_method': payment.payment_method,
            'status': payment.status,
            'discount_applied': payment.discount_applied
        }
        output.append(payment_data)
    
    return jsonify({'payments': output})

# Obtener un pago específico
@token_required
def get_payment(current_user, payment_id):
    payment = payment_service.get_payment_by_id(payment_id)
    
    if not payment:
        return jsonify({'message': 'Payment not found!'}), 404
    
    # Solo el propietario o admin puede ver el pago
    if payment.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized access!'}), 403
    
    # Obtener información adicional
    booking = booking_service.get_booking_by_id(payment.booking_id)
    package = package_service.get_package_by_id(booking.package_id)
    
    payment_data = {
        'id': payment.id,
        'booking_id': payment.booking_id,
        'user_id': payment.user_id,
        'package_id': booking.package_id,
        'package_destination': package.destination,
        'travel_date': booking.travel_date.strftime('%Y-%m-%d'),
        'number_of_travelers': booking.number_of_travelers,
        'amount': payment.amount,
        'payment_date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
        'payment_method': payment.payment_method,
        'transaction_id': payment.transaction_id,
        'status': payment.status,
        'discount_applied': payment.discount_applied
    }
    
    return jsonify({'payment': payment_data})

# Reembolsar un pago (solo admin)
@token_required
@role_required(['admin'])
def refund_payment(current_user, payment_id):
    payment = payment_service.get_payment_by_id(payment_id)
    
    if not payment:
        return jsonify({'message': 'Payment not found!'}), 404
    
    # Verificar si el pago ya fue reembolsado
    if payment.status == 'refunded':
        return jsonify({'message': 'Payment already refunded!'}), 400
    
    # Actualizar estado del pago (simulado, en un sistema real habría integración con la pasarela)
    payment.status = 'refunded'
    payment_service.update_payment(payment)
    
    # Actualizar estado de la reserva
    booking = booking_service.get_booking_by_id(payment.booking_id)
    booking.status = 'cancelled'
    booking_service.update_booking(booking)
    
    return jsonify({'message': 'Payment refunded successfully!'})

# Verificar estado de un pago
@token_required
def check_payment_status(current_user, payment_id):
    payment = payment_service.get_payment_by_id(payment_id)
    
    if not payment:
        return jsonify({'message': 'Payment not found!'}), 404
    
    # Solo el propietario o admin puede verificar el estado
    if payment.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized access!'}), 403
    
    return jsonify({
        'payment_id': payment.id,
        'transaction_id': payment.transaction_id,
        'status': payment.status,
        'payment_date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S')
    })

# Procesar pago con tarjeta de crédito (simulado)
@token_required
def process_card_payment(current_user):
    data = request.get_json()
    
    # Validar datos de entrada
    if not data or not data.get('booking_id') or not data.get('card_number') or not data.get('expiry_date') or not data.get('cvv'):
        return jsonify({'message': 'Missing required fields!'}), 400
    
    # Validación básica de tarjeta (simulada)
    card_number = data.get('card_number').replace(' ', '')
    if not card_number.isdigit() or len(card_number) not in [15, 16]:
        return jsonify({'message': 'Invalid card number!'}), 400
    
    # Aquí iría la lógica de procesamiento con la pasarela de pagos
    # Por ahora, simplemente llamamos al método genérico
    data['payment_method'] = 'credit_card'
    
    # Utilizar el método de proceso general
    return process_payment(current_user)