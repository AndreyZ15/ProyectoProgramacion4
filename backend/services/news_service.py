from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, and_, or_

from ..models.news import News
from ..database.db_config import db_session

class NewsService:
    """Servicio para gestionar operaciones relacionadas con noticias"""

    def get_all_news(self):
        """Obtiene todas las noticias"""
        try:
            return News.query.order_by(desc(News.publish_date)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener noticias: {str(e)}")

    def get_news_by_id(self, news_id):
        """Obtiene una noticia por su ID"""
        try:
            return News.query.filter_by(id=news_id).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener noticia: {str(e)}")

    def get_news_by_category(self, category):
        """Obtiene noticias por categoría"""
        try:
            return News.query.filter_by(category=category).order_by(desc(News.publish_date)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener noticias por categoría: {str(e)}")

    def get_featured_news(self):
        """Obtiene noticias destacadas"""
        try:
            return News.query.filter_by(is_featured=True).order_by(desc(News.publish_date)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener noticias destacadas: {str(e)}")

    def get_exclusive_news(self):
        """Obtiene noticias exclusivas para clientes VIP"""
        try:
            return News.query.filter_by(is_exclusive=True).order_by(desc(News.publish_date)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener noticias exclusivas: {str(e)}")

    def create_news(self, news):
        """Crea una nueva noticia"""
        try:
            db_session.add(news)
            db_session.commit()
            return news.id
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al crear noticia: {str(e)}")

    def update_news(self, news):
        """Actualiza una noticia existente"""
        try:
            db_session.commit()
            return True
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al actualizar noticia: {str(e)}")

    def delete_news(self, news_id):
        """Elimina una noticia"""
        try:
            news = self.get_news_by_id(news_id)
            if news:
                db_session.delete(news)
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al eliminar noticia: {str(e)}")

    def search_news(self, query):
        """Busca noticias por título o contenido"""
        try:
            search_query = f"%{query}%"
            return News.query.filter(
                or_(
                    News.title.ilike(search_query),
                    News.content.ilike(search_query),
                    News.tags.ilike(search_query)
                )
            ).order_by(desc(News.publish_date)).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al buscar noticias: {str(e)}")

    def increment_views(self, news_id):
        """Incrementa el contador de vistas de una noticia"""
        try:
            news = self.get_news_by_id(news_id)
            if news:
                news.views_count += 1
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al incrementar vistas: {str(e)}")

    def get_popular_news(self, limit=5):
        """Obtiene las noticias más populares basadas en vistas"""
        try:
            return News.query.order_by(desc(News.views_count)).limit(limit).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener noticias populares: {str(e)}")

    def get_recent_news(self, limit=5, exclude_exclusive=True):
        """Obtiene las noticias más recientes"""
        try:
            query = News.query
            if exclude_exclusive:
                query = query.filter_by(is_exclusive=False)
            
            return query.order_by(desc(News.publish_date)).limit(limit).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener noticias recientes: {str(e)}")

    def get_related_news(self, news_id, category, limit=3):
        """Obtiene noticias relacionadas basadas en la categoría"""
        try:
            return News.query.filter(
                and_(
                    News.category == category,
                    News.id != news_id
                )
            ).order_by(desc(News.publish_date)).limit(limit).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener noticias relacionadas: {str(e)}")

    def get_news_by_tag(self, tag, limit=10):
        """Obtiene noticias por etiqueta"""
        try:
            search_tag = f"%{tag}%"
            return News.query.filter(News.tags.ilike(search_tag)).order_by(desc(News.publish_date)).limit(limit).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener noticias por etiqueta: {str(e)}")

    def toggle_featured(self, news_id):
        """Cambia el estado de destacada de una noticia"""
        try:
            news = self.get_news_by_id(news_id)
            if news:
                news.is_featured = not news.is_featured
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al cambiar estado de destacada: {str(e)}")

    def toggle_exclusive(self, news_id):
        """Cambia el estado de exclusiva de una noticia"""
        try:
            news = self.get_news_by_id(news_id)
            if news:
                news.is_exclusive = not news.is_exclusive
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al cambiar estado de exclusiva: {str(e)}")