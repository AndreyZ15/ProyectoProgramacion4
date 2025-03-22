from flask import request, jsonify
from datetime import datetime

from ..models.news import News
from ..services.news_service import NewsService
from . import token_required, role_required

news_service = NewsService()

# Crear una nueva noticia (solo admin)
@token_required
@role_required(['admin'])
def create_news(current_user):
    data = request.get_json()
    
    # Validar datos de entrada
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'message': 'Missing required fields!'}), 400
    
    # Crear la noticia
    new_news = News(
        title=data.get('title'),
        content=data.get('content'),
        publish_date=datetime.now(),
        image_url=data.get('image_url', ''),
        author_id=current_user.id,
        is_featured=data.get('is_featured', False),
        category=data.get('category', 'general')
    )
    
    news_id = news_service.create_news(new_news)
    
    return jsonify({'message': 'News created successfully!', 'news_id': news_id}), 201

# Obtener todas las noticias
def get_all_news():
    news_list = news_service.get_all_news()
    output = []
    
    for news in news_list:
        news_data = {
            'id': news.id,
            'title': news.title,
            'content_preview': news.content[:150] + '...' if len(news.content) > 150 else news.content,
            'publish_date': news.publish_date.strftime('%Y-%m-%d'),
            'image_url': news.image_url,
            'author_name': news.author.name,
            'is_featured': news.is_featured,
            'category': news.category
        }
        output.append(news_data)
    
    return jsonify({'news': output})

# Obtener noticias destacadas
def get_featured_news():
    news_list = news_service.get_featured_news()
    output = []
    
    for news in news_list:
        news_data = {
            'id': news.id,
            'title': news.title,
            'content_preview': news.content[:150] + '...' if len(news.content) > 150 else news.content,
            'publish_date': news.publish_date.strftime('%Y-%m-%d'),
            'image_url': news.image_url,
            'author_name': news.author.name,
            'category': news.category
        }
        output.append(news_data)
    
    return jsonify({'featured_news': output})

# Obtener noticias por categoría
def get_news_by_category(category):
    news_list = news_service.get_news_by_category(category)
    output = []
    
    for news in news_list:
        news_data = {
            'id': news.id,
            'title': news.title,
            'content_preview': news.content[:150] + '...' if len(news.content) > 150 else news.content,
            'publish_date': news.publish_date.strftime('%Y-%m-%d'),
            'image_url': news.image_url,
            'author_name': news.author.name,
            'is_featured': news.is_featured
        }
        output.append(news_data)
    
    return jsonify({'category': category, 'news': output})

# Obtener una noticia por ID
def get_news(news_id):
    news = news_service.get_news_by_id(news_id)
    
    if not news:
        return jsonify({'message': 'News not found!'}), 404
    
    news_data = {
        'id': news.id,
        'title': news.title,
        'content': news.content,
        'publish_date': news.publish_date.strftime('%Y-%m-%d'),
        'image_url': news.image_url,
        'author_id': news.author_id,
        'author_name': news.author.name,
        'is_featured': news.is_featured,
        'category': news.category
    }
    
    # Obtener noticias relacionadas (misma categoría)
    related = news_service.get_related_news(news_id, news.category, limit=3)
    related_news = []
    
    for rel_news in related:
        related_news.append({
            'id': rel_news.id,
            'title': rel_news.title,
            'publish_date': rel_news.publish_date.strftime('%Y-%m-%d'),
            'image_url': rel_news.image_url
        })
    
    news_data['related_news'] = related_news
    
    return jsonify({'news': news_data})

# Actualizar una noticia (solo admin)
@token_required
@role_required(['admin'])
def update_news(current_user, news_id):
    data = request.get_json()
    
    news = news_service.get_news_by_id(news_id)
    
    if not news:
        return jsonify({'message': 'News not found!'}), 404
    
    # Actualizar campos
    if data.get('title'):
        news.title = data.get('title')
    
    if data.get('content'):
        news.content = data.get('content')
    
    if data.get('image_url'):
        news.image_url = data.get('image_url')
    
    if 'is_featured' in data:
        news.is_featured = bool(data.get('is_featured'))
    
    if data.get('category'):
        news.category = data.get('category')
    
    news_service.update_news(news)
    
    return jsonify({'message': 'News updated successfully!'})

# Eliminar una noticia (solo admin)
@token_required
@role_required(['admin'])
def delete_news(current_user, news_id):
    news = news_service.get_news_by_id(news_id)
    
    if not news:
        return jsonify({'message': 'News not found!'}), 404
    
    news_service.delete_news(news_id)
    
    return jsonify({'message': 'News deleted successfully!'})

# Obtener noticias exclusivas (solo para clientes VIP)
@token_required
@role_required(['admin', 'vip'])
def get_exclusive_news(current_user):
    news_list = news_service.get_exclusive_news()
    output = []
    
    for news in news_list:
        news_data = {
            'id': news.id,
            'title': news.title,
            'content_preview': news.content[:150] + '...' if len(news.content) > 150 else news.content,
            'publish_date': news.publish_date.strftime('%Y-%m-%d'),
            'image_url': news.image_url,
            'author_name': news.author.name,
            'category': news.category
        }
        output.append(news_data)
    
    return jsonify({'exclusive_news': output})