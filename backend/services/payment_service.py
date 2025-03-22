from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, func
import uuid
from datetime import datetime

from ..models.payment import Payment
from ..models.booking import Booking
from ..database.db_config import db_session

class PaymentService:
    """Servicio para gestionar operaciones relacionadas con pagos"""

    def get_all_payments(self):
        """Obtiene todos los pagos"""
        try:
            return Payment.query.order_by(desc(Payment.payment_date)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener pagos: {str(e)}")

    def get_payment_by_id(self, payment_id):
        """Obtiene un pago por su ID"""
        try:
            return Payment.query.filter_by(id=payment_id).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener pago: {str(e)}")

    def get_booking_payments(self, booking_id):
        """Obtiene todos los pagos de una reserva específica"""
        try:
            return Payment.query.filter_by(booking_id=booking_id).order_by(desc(Payment.payment_date)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener pagos de la reserva: {str(e)}")

    def get_user_payments(self, user_id):
        """Obtiene todos los pagos de un usuario específico"""
        try:
            return Payment.query.filter_by(user_id=user_id).order_by(desc(Payment.payment_date)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener pagos del usuario: {str(e)}")

    def create_payment(self, payment):
        """Crea un nuevo pago"""
        try:
            db_session.add(payment)
            db_session.commit()
            return payment.id
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al crear pago: {str(e)}")

    def update_payment(self, payment):
        """Actualiza un pago existente"""
        try:
            db_session.commit()
            return True
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al actualizar pago: {str(e)}")

    def delete_payment(self, payment_id):
        """Elimina un pago"""
        try:
            payment = self.get_payment_by_id(payment_id)
            if payment:
                db_session.delete(payment)
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al eliminar pago: {str(e)}")

    def process_payment(self, booking_id, user_id, amount, payment_method, card_last_digits=None, billing_address=None):
        """Procesa un nuevo pago y actualiza el estado si corresponde"""
        try:
            # Simulación de procesamiento con pasarela de pagos
            # En un caso real, aquí se integraría con la API de la pasarela
            transaction_id = str(uuid.uuid4())
            
            # Crear el registro de pago
            payment = Payment(
                booking_id=booking_id,
                user_id=user_id,
                amount=amount,
                payment_method=payment_method,
                transaction_id=transaction_id,
                status='completed',  # Asumimos que el pago es exitoso
                card_last_digits=card_last_digits,
                billing_address=billing_address
            )
            
            db_session.add(payment)
            
            # Verificar si con este pago se completa el total de la reserva
            booking = Booking.query.filter_by(id=booking_id).first()
            if booking:
                # Calcular el total pagado hasta ahora
                total_paid = db_session.query(func.sum(Payment.amount)).filter(
                    Payment.booking_id == booking_id,
                    Payment.status == 'completed'
                ).scalar() or 0
                
                total_paid += amount
                
                # Si el total pagado cubre el precio total, confirmar la reserva
                if total_paid >= booking.total_price and booking.status == 'pending':
                    booking.status = 'confirmed'
                
            db_session.commit()
            
            return {
                'payment_id': payment.id,
                'transaction_id': transaction_id,
                'status': 'completed',
                'booking_status': booking.status if booking else None
            }
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al procesar pago: {str(e)}")

    def refund_payment(self, payment_id):
        """Procesa un reembolso de pago"""
        try:
            payment = self.get_payment_by_id(payment_id)
            if not payment or payment.status != 'completed':
                return False
            
            # Simular procesamiento de reembolso
            # En un caso real, aquí se integraría con la API de la pasarela
            payment.status = 'refunded'
            
            # Verificar si hay que actualizar el estado de la reserva
            booking = Booking.query.filter_by(id=payment.booking_id).first()
            if booking and booking.status == 'confirmed':
                # Verificar si después del reembolso los pagos no alcanzan para cubrir el total
                total_paid = db_session.query(func.sum(Payment.amount)).filter(
                    Payment.booking_id == booking.id,
                    Payment.status == 'completed'
                ).scalar() or 0
                
                total_paid -= payment.amount
                
                if total_paid < booking.total_price:
                    booking.status = 'pending'
            
            db_session.commit()
            
            return True
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al procesar reembolso: {str(e)}")

    def get_payment_stats(self, start_date=None, end_date=None):
        """Obtiene estadísticas de pagos en un período"""
        try:
            query = db_session.query(
                func.count(Payment.id).label('total_payments'),
                func.sum(Payment.amount).label('total_amount')
            ).filter(Payment.status == 'completed')
            
            if start_date:
                query = query.filter(Payment.payment_date >= start_date)
            if end_date:
                query = query.filter(Payment.payment_date <= end_date)
            
            result = query.first()
            
            # Pagos por método de pago
            payment_methods = {}
            methods = db_session.query(
                Payment.payment_method,
                func.count(Payment.id).label('count'),
                func.sum(Payment.amount).label('amount')
            ).filter(
                Payment.status == 'completed'
            ).group_by(
                Payment.payment_method
            ).all()
            
            for method in methods:
                payment_methods[method.payment_method] = {
                    'count': method.count,
                    'amount': float(method.amount) if method.amount else 0
                }
            
            return {
                'total_payments': result.total_payments or 0,
                'total_amount': float(result.total_amount or 0),
                'payment_methods': payment_methods
            }
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener estadísticas de pagos: {str(e)}")

    def check_booking_payment_status(self, booking_id):
        """Verifica el estado de pago de una reserva"""
        try:
            booking = Booking.query.filter_by(id=booking_id).first()
            if not booking:
                return None
            
            total_paid = db_session.query(func.sum(Payment.amount)).filter(
                Payment.booking_id == booking_id,
                Payment.status == 'completed'
            ).scalar() or 0
            
            pending_amount = booking.total_price - total_paid
            
            return {
                'booking_id': booking_id,
                'total_price': booking.total_price,
                'total_paid': float(total_paid),
                'pending_amount': float(pending_amount),
                'is_fully_paid': total_paid >= booking.total_price,
                'payment_percentage': (total_paid / booking.total_price) * 100 if booking.total_price > 0 else 0
            }
        except SQLAlchemyError as e:
            raise Exception(f"Error al verificar estado de pago: {str(e)}")

    def generate_payment_receipt(self, payment_id):
        """Genera datos para un recibo de pago"""
        try:
            payment = self.get_payment_by_id(payment_id)
            if not payment:
                return None
            
            booking = Booking.query.filter_by(id=payment.booking_id).first()
            
            receipt_data = {
                'receipt_number': f"RCP-{payment.id}",
                'transaction_id': payment.transaction_id,
                'payment_date': payment.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
                'payment_method': payment.payment_method,
                'amount': payment.amount,
                'status': payment.status,
                'user_name': payment.user.name if payment.user else 'N/A',
                'booking_number': booking.booking_number if booking else 'N/A',
                'destination': booking.package.destination if booking and booking.package else 'N/A',
                'travel_date': booking.travel_date.strftime('%Y-%m-%d') if booking else 'N/A',
                'generated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return receipt_data
        except SQLAlchemyError as e:
            raise Exception(f"Error al generar recibo de pago: {str(e)}")