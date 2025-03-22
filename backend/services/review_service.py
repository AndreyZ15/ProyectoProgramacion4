from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, func

from ..models.review import Review
from ..database.db_config import db_session

class ReviewService:
    """Servicio para gestionar operaciones relacionadas con reseñas"""

    def get_all_reviews(self):
        """Obtiene todas las reseñas"""
        try:
            return Review.query.order_by(desc(Review.date)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reseñas: {str(e)}")

    def get_review_by_id(self, review_id):
        """Obtiene una reseña por su ID"""
        try:
            return Review.query.filter_by(id=review_id).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reseña: {str(e)}")

    def get_package_reviews(self, package_id):
        """Obtiene todas las reseñas de un paquete específico"""
        try:
            return Review.query.filter_by(
                package_id=package_id,
                is_approved=1  # Solo reseñas aprobadas
            ).order_by(desc(Review.date)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reseñas del paquete: {str(e)}")

    def get_user_reviews(self, user_id):
        """Obtiene todas las reseñas de un usuario específico"""
        try:
            return Review.query.filter_by(user_id=user_id).order_by(desc(Review.date)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reseñas del usuario: {str(e)}")

    def get_user_package_review(self, user_id, package_id):
        """Verifica si un usuario ya ha dejado una reseña para un paquete específico"""
        try:
            return Review.query.filter_by(
                user_id=user_id,
                package_id=package_id
            ).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al verificar reseña existente: {str(e)}")

    def create_review(self, review):
        """Crea una nueva reseña"""
        try:
            db_session.add(review)
            db_session.commit()
            return review.id
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al crear reseña: {str(e)}")

    def update_review(self, review):
        """Actualiza una reseña existente"""
        try:
            db_session.commit()
            return True
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al actualizar reseña: {str(e)}")

    def delete_review(self, review_id):
        """Elimina una reseña"""
        try:
            review = self.get_review_by_id(review_id)
            if review:
                db_session.delete(review)
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al eliminar reseña: {str(e)}")

    def approve_review(self, review_id):
        """Aprueba una reseña pendiente"""
        try:
            review = self.get_review_by_id(review_id)
            if review:
                review.is_approved = 1  # 1 = aprobado
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al aprobar reseña: {str(e)}")

    def reject_review(self, review_id):
        """Rechaza una reseña pendiente"""
        try:
            review = self.get_review_by_id(review_id)
            if review:
                review.is_approved = 2  # 2 = rechazado
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al rechazar reseña: {str(e)}")

    def get_pending_reviews(self):
        """Obtiene todas las reseñas pendientes de aprobación"""
        try:
            return Review.query.filter_by(is_approved=0).order_by(desc(Review.date)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reseñas pendientes: {str(e)}")

    def get_review_stats(self):
        """Obtiene estadísticas sobre las reseñas"""
        try:
            total_reviews = Review.query.count()
            avg_rating = db_session.query(func.avg(Review.rating)).scalar() or 0
            
            # Distribución de calificaciones
            ratings_distribution = {}
            for i in range(1, 6):
                count = Review.query.filter_by(rating=i).count()
                ratings_distribution[i] = count
            
            # Conteo por estado de aprobación
            approval_stats = {
                'pending': Review.query.filter_by(is_approved=0).count(),
                'approved': Review.query.filter_by(is_approved=1).count(),
                'rejected': Review.query.filter_by(is_approved=2).count()
            }
            
            return {
                'total_reviews': total_reviews,
                'average_rating': float(avg_rating),
                'ratings_distribution': ratings_distribution,
                'approval_stats': approval_stats
            }
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener estadísticas de reseñas: {str(e)}")

    def get_recent_reviews(self, limit=5):
        """Obtiene las reseñas más recientes (aprobadas)"""
        try:
            return Review.query.filter_by(is_approved=1).order_by(desc(Review.date)).limit(limit).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reseñas recientes: {str(e)}")

    def get_top_rated_reviews(self, limit=5):
        """Obtiene las reseñas con mejor calificación"""
        try:
            return Review.query.filter_by(
                is_approved=1
            ).order_by(
                desc(Review.rating), 
                desc(Review.date)
            ).limit(limit).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reseñas mejor calificadas: {str(e)}")