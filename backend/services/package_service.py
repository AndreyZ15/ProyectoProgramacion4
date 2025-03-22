from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, func

from ..models.package import Package
from ..models.review import Review
from ..database.db_config import db_session

class PackageService:
    """Servicio para gestionar operaciones relacionadas con paquetes turísticos"""

    def get_all_packages(self):
        """Obtiene todos los paquetes turísticos"""
        try:
            return Package.query.all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener paquetes: {str(e)}")

    def get_available_packages(self):
        """Obtiene todos los paquetes disponibles"""
        try:
            return Package.query.filter_by(availability=True).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener paquetes disponibles: {str(e)}")

    def get_package_by_id(self, package_id):
        """Obtiene un paquete por su ID"""
        try:
            return Package.query.filter_by(id=package_id).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener paquete: {str(e)}")

    def create_package(self, package):
        """Crea un nuevo paquete turístico"""
        try:
            db_session.add(package)
            db_session.commit()
            return package.id
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al crear paquete: {str(e)}")

    def update_package(self, package):
        """Actualiza la información de un paquete existente"""
        try:
            db_session.commit()
            return True
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al actualizar paquete: {str(e)}")

    def delete_package(self, package_id):
        """Elimina un paquete turístico"""
        try:
            package = self.get_package_by_id(package_id)
            if package:
                db_session.delete(package)
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al eliminar paquete: {str(e)}")

    def toggle_availability(self, package_id):
        """Cambia el estado de disponibilidad de un paquete"""
        try:
            package = self.get_package_by_id(package_id)
            if package:
                package.availability = not package.availability
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al cambiar disponibilidad: {str(e)}")

    def search_packages(self, query, filters=None):
        """Busca paquetes por destino o descripción con filtros opcionales"""
        try:
            search_query = f"%{query}%"
            result = Package.query.filter(
                (Package.destination.ilike(search_query)) | 
                (Package.description.ilike(search_query))
            )
            
            if filters:
                if 'min_price' in filters:
                    result = result.filter(Package.price >= filters['min_price'])
                if 'max_price' in filters:
                    result = result.filter(Package.price <= filters['max_price'])
                if 'min_duration' in filters:
                    result = result.filter(Package.duration >= filters['min_duration'])
                if 'max_duration' in filters:
                    result = result.filter(Package.duration <= filters['max_duration'])
                if 'difficulty' in filters:
                    result = result.filter(Package.difficulty_level == filters['difficulty'])
                if 'season' in filters:
                    result = result.filter(Package.season.like(f"%{filters['season']}%"))
                
            return result.all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al buscar paquetes: {str(e)}")

    def get_packages_by_price_range(self, min_price, max_price):
        """Obtiene paquetes por rango de precios"""
        try:
            return Package.query.filter(
                Package.price >= min_price,
                Package.price <= max_price,
                Package.availability == True
            ).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener paquetes por rango de precio: {str(e)}")

    def get_packages_by_duration(self, min_days, max_days):
        """Obtiene paquetes por duración"""
        try:
            return Package.query.filter(
                Package.duration >= min_days,
                Package.duration <= max_days,
                Package.availability == True
            ).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener paquetes por duración: {str(e)}")

    def get_top_rated_packages(self, limit=5):
        """Obtiene los paquetes mejor calificados"""
        try:
            # Usando una subconsulta para obtener la calificación promedio
            avg_ratings = db_session.query(
                Review.package_id,
                func.avg(Review.rating).label('avg_rating')
            ).group_by(Review.package_id).subquery()
            
            # Uniendo con la tabla de paquetes
            packages = db_session.query(Package).join(
                avg_ratings,
                Package.id == avg_ratings.c.package_id
            ).filter(
                Package.availability == True
            ).order_by(
                desc(avg_ratings.c.avg_rating)
            ).limit(limit).all()
            
            return packages
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener paquetes mejor calificados: {str(e)}")

    def get_most_booked_packages(self, limit=5):
        """Obtiene los paquetes más reservados"""
        try:
            from ..models.booking import Booking
            
            # Contamos las reservas por paquete
            booking_counts = db_session.query(
                Booking.package_id,
                func.count(Booking.id).label('booking_count')
            ).filter(
                Booking.status != 'cancelled'
            ).group_by(Booking.package_id).subquery()
            
            # Unimos con la tabla de paquetes
            packages = db_session.query(Package).join(
                booking_counts,
                Package.id == booking_counts.c.package_id
            ).order_by(
                desc(booking_counts.c.booking_count)
            ).limit(limit).all()
            
            return packages
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener paquetes más reservados: {str(e)}")

    def get_package_reviews(self, package_id):
        """Obtiene las reseñas de un paquete específico"""
        try:
            return Review.query.filter_by(
                package_id=package_id,
                is_approved=1
            ).order_by(desc(Review.date)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener reseñas del paquete: {str(e)}")

    def get_package_average_rating(self, package_id):
        """Obtiene la calificación promedio de un paquete"""
        try:
            result = db_session.query(func.avg(Review.rating)).filter(
                Review.package_id == package_id,
                Review.is_approved == 1
            ).scalar()
            
            return float(result) if result else 0
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener calificación promedio: {str(e)}")

    def get_similar_packages(self, package_id, limit=3):
        """Obtiene paquetes similares basados en duración y precio"""
        try:
            package = self.get_package_by_id(package_id)
            if not package:
                return []
            
            similar_packages = Package.query.filter(
                Package.id != package_id,
                Package.availability == True,
                Package.duration.between(package.duration - 3, package.duration + 3),
                Package.price.between(package.price * 0.7, package.price * 1.3)
            ).limit(limit).all()
            
            return similar_packages
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener paquetes similares: {str(e)}")