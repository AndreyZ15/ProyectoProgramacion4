from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from ..controllers.booking_controller import (
    create_booking, get_all_bookings, get_user_bookings, get_booking,
    update_booking_status, delete_booking, check_availability
)
from ..controllers import token_required, role_required

# Crear el Blueprint para las rutas de reservas
booking_bp = Blueprint('bookings', __name__, url_prefix='/api/bookings')

# Ruta para crear una nueva reserva
@booking_bp.route('', methods=['POST'])
@token_required
def add_booking(current_user):
    return create_booking(current_user)

# Ruta para obtener todas las reservas (solo admin)
@booking_bp.route('', methods=['GET'])
@token_required
@role_required(['admin'])
def get_bookings(current_user):
    return get_all_bookings(current_user)

# Ruta para obtener las reservas del usuario actual
@booking_bp.route('/my-bookings', methods=['GET'])
@token_required
def get_my_bookings(current_user):
    return get_user_bookings(current_user)

# Ruta para obtener una reserva específica
@booking_bp.route('/<int:booking_id>', methods=['GET'])
@token_required
def get_booking_by_id(current_user, booking_id):
    return get_booking(current_user, booking_id)

# Ruta para actualizar el estado de una reserva
@booking_bp.route('/<int:booking_id>/status', methods=['PUT'])
@token_required
def update_status(current_user, booking_id):
    return update_booking_status(current_user, booking_id)

# Ruta para eliminar una reserva (solo admin)
@booking_bp.route('/<int:booking_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_booking_by_id(current_user, booking_id):
    return delete_booking(current_user, booking_id)

# Ruta para verificar disponibilidad
@booking_bp.route('/check-availability', methods=['POST'])
def availability():
    return check_availability()

# Ruta para obtener fechas disponibles para un paquete
@booking_bp.route('/available-dates', methods=['GET'])
def get_available_dates():
    package_id = request.args.get('package_id', type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if not package_id or not start_date_str or not end_date_str:
        return jsonify({'message': 'Missing required parameters!'}), 400
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
        from ..services.booking_service import BookingService
        
        booking_service = BookingService()
        available_dates = booking_service.get_available_dates(package_id, start_date, end_date)
        
        return jsonify({
            'package_id': package_id,
            'available_dates': [date.strftime('%Y-%m-%d') for date in available_dates]
        })
    except ValueError:
        return jsonify({'message': 'Invalid date format! Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para generar un PDF de confirmación de reserva
@booking_bp.route('/<int:booking_id>/confirmation-pdf', methods=['GET'])
@token_required
def generate_confirmation_pdf(current_user, booking_id):
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.booking_service import BookingService
    from ..utils.pdf_generator import generate_booking_pdf
    from flask import send_file
    import os
    
    try:
        booking_service = BookingService()
        booking = booking_service.get_booking_by_id(booking_id)
        
        # Verificar permisos
        if not booking or (booking.user_id != current_user.id and current_user.role != 'admin'):
            return jsonify({'message': 'Unauthorized access!'}), 403
        
        # Generar PDF
        pdf_path = generate_booking_pdf(booking)
        
        # Enviar el archivo al cliente
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"booking_confirmation_{booking.booking_number}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para obtener estadísticas de reservas (solo admin)
@booking_bp.route('/stats', methods=['GET'])
@token_required
@role_required(['admin'])
def get_booking_statistics(current_user):
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    try:
        start_date = None
        end_date = None
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
        from ..services.booking_service import BookingService
        
        booking_service = BookingService()
        stats = booking_service.get_booking_stats(start_date, end_date)
        
        return jsonify(stats)
    except ValueError:
        return jsonify({'message': 'Invalid date format! Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500