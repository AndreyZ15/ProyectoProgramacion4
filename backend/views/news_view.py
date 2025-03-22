from flask import Blueprint, request, jsonify
from ..controllers.news_controller import (
    create_news, get_all_news, get_featured_news, get_news_by_category,
    get_news, update_news, delete_news, get_exclusive_news
)
from ..controllers import token_required, role_required

# Crear el Blueprint para las rutas de noticias
news_bp = Blueprint('news', __name__, url_prefix='/api/news')

# Ruta para obtener todas las noticias
@news_bp.route('', methods=['GET'])
def get_news_list():
    return get_all_news()

# Ruta para obtener noticias destacadas
@news_bp.route('/featured', methods=['GET'])
def get_featured():
    return get_featured_news()

# Ruta para obtener noticias por categoría
@news_bp.route('/category/<string:category>', methods=['GET'])
def get_by_category(category):
    return get_news_by_category(category)

# Ruta para obtener una noticia específica
@news_bp.route('/<int:news_id>', methods=['GET'])
def get_news_by_id(news_id):
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.news_service import NewsService
    
    try:
        news_service = NewsService()
        
        # Incrementar contador de vistas
        news_service.increment_views(news_id)
        
        return get_news(news_id)
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para crear una nueva noticia (solo admin)
@news_bp.route('', methods=['POST'])
@token_required
@role_required(['admin'])
def add_news(current_user):
    return create_news(current_user)

# Ruta para actualizar una noticia (solo admin)
@news_bp.route('/<int:news_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_news_by_id(current_user, news_id):
    return update_news(current_user, news_id)

# Ruta para eliminar una noticia (solo admin)
@news_bp.route('/<int:news_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_news_by_id(current_user, news_id):
    return delete_news(current_user, news_id)

# Ruta para obtener noticias exclusivas (solo VIP y admin)
@news_bp.route('/exclusive', methods=['GET'])
@token_required
@role_required(['admin', 'vip'])
def get_vip_news(current_user):
    return get_exclusive_news(current_user)

# Ruta para buscar noticias
@news_bp.route('/search', methods=['GET'])
def search_news():
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'message': 'Query parameter is required!'}), 400
    
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.news_service import NewsService
    
    try:
        news_service = NewsService()
        news_list = news_service.search_news(query)
        
        result = []
        for news in news_list:
            result.append({
                'id': news.id,
                'title': news.title,
                'content_preview': news.get_preview(150),
                'publish_date': news.publish_date.strftime('%Y-%m-%d'),
                'image_url': news.image_url,
                'category': news.category,
                'is_exclusive': news.is_exclusive
            })
        
        return jsonify({'news': result})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para obtener las noticias populares
@news_bp.route('/popular', methods=['GET'])
def get_popular_news():
    limit = request.args.get('limit', 5, type=int)
    
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.news_service import NewsService
    
    try:
        news_service = NewsService()
        news_list = news_service.get_popular_news(limit)
        
        result = []
        for news in news_list:
            result.append({
                'id': news.id,
                'title': news.title,
                'content_preview': news.get_preview(150),
                'publish_date': news.publish_date.strftime('%Y-%m-%d'),
                'image_url': news.image_url,
                'views_count': news.views_count
            })
        
        return jsonify({'popular_news': result})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para cambiar el estado destacado de una noticia (toggle)
@news_bp.route('/<int:news_id>/toggle-featured', methods=['PUT'])
@token_required
@role_required(['admin'])
def toggle_featured_status(current_user, news_id):
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.news_service import NewsService
    
    try:
        news_service = NewsService()
        result = news_service.toggle_featured(news_id)
        
        if result:
            return jsonify({'message': 'Featured status updated successfully!'})
        else:
            return jsonify({'message': 'News not found!'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500