from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta

from ..models.booking import Booking
from ..models.package import Package
from ..database.db_config import db_session

class BookingService:
    """Servicio para gestionar operaciones relacionadas con reservas de viajes"""

    def get_all_bookings(self):
        """Obtiene todas las reservas"""
        try:
            return Booking.query.order_by(desc(Booking.created_at)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reservas: {str(e)}")

    def get_booking_by_id(self, booking_id):
        """Obtiene una reserva por su ID"""
        try:
            return Booking.query.filter_by(id=booking_id).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reserva: {str(e)}")

    def get_booking_by_number(self, booking_number):
        """Obtiene una reserva por su número de reserva"""
        try:
            return Booking.query.filter_by(booking_number=booking_number).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reserva por número: {str(e)}")

    def get_user_bookings(self, user_id):
        """Obtiene todas las reservas de un usuario específico"""
        try:
            return Booking.query.filter_by(user_id=user_id).order_by(desc(Booking.created_at)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reservas del usuario: {str(e)}")

    def get_package_bookings(self, package_id):
        """Obtiene todas las reservas para un paquete específico"""
        try:
            return Booking.query.filter_by(package_id=package_id).order_by(desc(Booking.created_at)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reservas del paquete: {str(e)}")

    def create_booking(self, booking):
        """Crea una nueva reserva"""
        try:
            # Calculamos el precio total si no está establecido
            if not booking.total_price:
                package = Package.query.filter_by(id=booking.package_id).first()
                if package:
                    booking.calculate_total_price(package.price)
            
            db_session.add(booking)
            db_session.commit()
            return booking.id
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al crear reserva: {str(e)}")

    def update_booking(self, booking):
        """Actualiza una reserva existente"""
        try:
            db_session.commit()
            return True
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al actualizar reserva: {str(e)}")

    def delete_booking(self, booking_id):
        """Elimina una reserva"""
        try:
            booking = self.get_booking_by_id(booking_id)
            if booking:
                db_session.delete(booking)
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al eliminar reserva: {str(e)}")

    def update_booking_status(self, booking_id, new_status):
        """Actualiza el estado de una reserva"""
        try:
            booking = self.get_booking_by_id(booking_id)
            if booking and new_status in ['pending', 'confirmed', 'cancelled']:
                booking.status = new_status
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al actualizar estado de reserva: {str(e)}")

    def check_availability(self, package_id, travel_date):
        """Verifica disponibilidad para un paquete en una fecha específica"""
        try:
            # Obtenemos el paquete para verificar max_travelers
            package = Package.query.filter_by(id=package_id).first()
            if not package or not package.availability:
                return False
            
            # Contamos las reservas confirmadas o pendientes para esa fecha
            bookings_count = Booking.query.filter(
                Booking.package_id == package_id,
                Booking.travel_date == travel_date,
                Booking.status.in_(['confirmed', 'pending'])
            ).with_entities(func.sum(Booking.number_of_travelers)).scalar() or 0
            
            # Verificamos si hay espacio disponible
            return bookings_count < package.max_travelers
        except SQLAlchemyError as e:
            raise Exception(f"Error al verificar disponibilidad: {str(e)}")

    def get_available_dates(self, package_id, start_date, end_date):
        """Obtiene fechas disponibles para un paquete en un rango determinado"""
        try:
            # Obtenemos el paquete
            package = Package.query.filter_by(id=package_id).first()
            if not package or not package.availability:
                return []
            
            # Generamos todas las fechas en el rango
            dates = []
            current_date = start_date
            while current_date <= end_date:
                # Verificamos disponibilidad para cada fecha
                if self.check_availability(package_id, current_date):
                    dates.append(current_date)
                current_date += timedelta(days=1)
            
            return dates
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener fechas disponibles: {str(e)}")

    def get_upcoming_bookings(self, user_id=None):
        """Obtiene reservas próximas (para un usuario específico o todas)"""
        try:
            query = Booking.query.filter(
                Booking.travel_date >= datetime.utcnow().date(),
                Booking.status != 'cancelled'
            ).order_by(Booking.travel_date)
            
            if user_id:
                query = query.filter(Booking.user_id == user_id)
            
            return query.all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reservas próximas: {str(e)}")

    def get_booking_stats(self, start_date=None, end_date=None):
        """Obtiene estadísticas de reservas en un período"""
        try:
            query = db_session.query(
                func.count(Booking.id).label('total_bookings'),
                func.sum(Booking.total_price).label('total_revenue')
            )
            
            if start_date:
                query = query.filter(Booking.created_at >= start_date)
            if end_date:
                query = query.filter(Booking.created_at <= end_date)
            
            result = query.first()
            
            # Contamos reservas por estado
            status_counts = {}
            for status in ['pending', 'confirmed', 'cancelled']:
                count = Booking.query.filter(Booking.status == status).count()
                status_counts[status] = count
            
            return {
                'total_bookings': result.total_bookings or 0,
                'total_revenue': float(result.total_revenue or 0),
                'status_counts': status_counts
            }
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener estadísticas de reservas: {str(e)}")

    def has_user_traveled(self, user_id, package_id):
        """Verifica si un usuario ha viajado con un paquete específico (para permitir reseñas)"""
        try:
            # Verificamos si tiene alguna reserva confirmada con fecha de viaje pasada
            has_traveled = Booking.query.filter(
                Booking.user_id == user_id,
                Booking.package_id == package_id,
                Booking.status == 'confirmed',
                Booking.travel_date < datetime.utcnow().date()
            ).first() is not None
            
            return has_traveled
        except SQLAlchemyError as e:
            raise Exception(f"Error al verificar si el usuario ha viajado: {str(e)}")

    def get_most_active_users(self, limit=5):
        """Obtiene los usuarios con más reservas"""
        try:
            from ..models.user import User
            
            # Contamos reservas por usuario
            booking_counts = db_session.query(
                Booking.user_id,
                func.count(Booking.id).label('booking_count')
            ).group_by(Booking.user_id).subquery()
            
            # Unimos con la tabla de usuarios
            users = db_session.query(
                User, 
                booking_counts.c.booking_count
            ).join(
                booking_counts,
                User.id == booking_counts.c.user_id
            ).order_by(
                desc(booking_counts.c.booking_count)
            ).limit(limit).all()
            
            return users
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener usuarios más activos: {str(e)}")