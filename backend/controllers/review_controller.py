from flask import request, jsonify
from datetime import datetime

from ..models.review import Review
from ..services.review_service import ReviewService
from ..services.booking_service import BookingService
from . import token_required

review_service = ReviewService()
booking_service = BookingService()

# Crear una nueva reseña
@token_required
def create_review(current_user):
    data = request.get_json()
    
    # Validar datos de entrada
    if not data or not data.get('package_id') or not data.get('comment') or 'rating' not in data:
        return jsonify({'message': 'Missing required fields!'}), 400
    
    # Validar calificación entre 1 y 5
    rating = data.get('rating')
    if rating < 1 or rating > 5:
        return jsonify({'message': 'Rating must be between 1 and 5!'}), 400
    
    # Verificar que el usuario ha reservado y completado el viaje
    # (Esto es opcional, pero recomendado para asegurar reseñas genuinas)
    has_traveled = booking_service.has_user_traveled(current_user.id, data.get('package_id'))
    
    if not has_traveled and current_user.role != 'admin':
        return jsonify({'message': 'You must have completed the trip to leave a review!'}), 403
    
    # Verificar si el usuario ya ha dejado una reseña para este paquete
    existing_review = review_service.get_user_package_review(current_user.id, data.get('package_id'))
    
    if existing_review:
        return jsonify({'message': 'You have already reviewed this package!'}), 409
    
    # Crear la reseña
    new_review = Review(
        user_id=current_user.id,
        package_id=data.get('package_id'),
        comment=data.get('comment'),
        rating=rating,
        date=datetime.now()
    )
    
    review_id = review_service.create_review(new_review)
    
    return jsonify({'message': 'Review created successfully!', 'review_id': review_id}), 201

# Obtener todas las reseñas de un paquete
def get_package_reviews(package_id):
    reviews = review_service.get_package_reviews(package_id)
    output = []
    
    for review in reviews:
        review_data = {
            'id': review.id,
            'user_id': review.user_id,
            'user_name': review.user.name,
            'comment': review.comment,
            'rating': review.rating,
            'date': review.date.strftime('%Y-%m-%d')
        }
        output.append(review_data)
    
    # Calcular calificación promedio
    avg_rating = 0
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
    
    return jsonify({
        'package_id': package_id,
        'reviews': output,
        'review_count': len(output),
        'average_rating': round(avg_rating, 1)
    })

# Obtener todas las reseñas de un usuario
@token_required
def get_user_reviews(current_user):
    # Un usuario solo puede ver sus propias reseñas a menos que sea admin
    user_id = current_user.id
    
    reviews = review_service.get_user_reviews(user_id)
    output = []
    
    for review in reviews:
        review_data = {
            'id': review.id,
            'package_id': review.package_id,
            'package_destination': review.package.destination,
            'comment': review.comment,
            'rating': review.rating,
            'date': review.date.strftime('%Y-%m-%d')
        }
        output.append(review_data)
    
    return jsonify({'reviews': output})

# Obtener una reseña específica
def get_review(review_id):
    review = review_service.get_review_by_id(review_id)
    
    if not review:
        return jsonify({'message': 'Review not found!'}), 404
    
    review_data = {
        'id': review.id,
        'user_id': review.user_id,
        'user_name': review.user.name,
        'package_id': review.package_id,
        'package_destination': review.package.destination,
        'comment': review.comment,
        'rating': review.rating,
        'date': review.date.strftime('%Y-%m-%d')
    }
    
    return jsonify({'review': review_data})

# Actualizar una reseña
@token_required
def update_review(current_user, review_id):
    data = request.get_json()
    
    review = review_service.get_review_by_id(review_id)
    
    if not review:
        return jsonify({'message': 'Review not found!'}), 404
    
    # Solo el autor o un admin puede editar una reseña
    if review.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized to edit this review!'}), 403
    
    # Actualizar campos
    if data.get('comment'):
        review.comment = data.get('comment')
    
    if 'rating' in data:
        rating = data.get('rating')
        if rating < 1 or rating > 5:
            return jsonify({'message': 'Rating must be between 1 and 5!'}), 400
        review.rating = rating
    
    review_service.update_review(review)
    
    return jsonify({'message': 'Review updated successfully!'})

# Eliminar una reseña
@token_required
def delete_review(current_user, review_id):
    review = review_service.get_review_by_id(review_id)
    
    if not review:
        return jsonify({'message': 'Review not found!'}), 404
    
    # Solo el autor o un admin puede eliminar una reseña
    if review.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'message': 'Unauthorized to delete this review!'}), 403
    
    review_service.delete_review(review_id)
    
    return jsonify({'message': 'Review deleted successfully!'})

# Obtener las reseñas más recientes (para la página principal)
def get_recent_reviews(limit=5):
    reviews = review_service.get_recent_reviews(limit)
    output = []
    
    for review in reviews:
        review_data = {
            'id': review.id,
            'user_name': review.user.name,
            'package_destination': review.package.destination,
            'comment': review.comment[:100] + '...' if len(review.comment) > 100 else review.comment,
            'rating': review.rating,
            'date': review.date.strftime('%Y-%m-%d')
        }
        output.append(review_data)
    
    return jsonify({'recent_reviews': output})

# Obtener las reseñas con mejor calificación
def get_top_rated_reviews(limit=5):
    reviews = review_service.get_top_rated_reviews(limit)
    output = []
    
    for review in reviews:
        review_data = {
            'id': review.id,
            'user_name': review.user.name,
            'package_destination': review.package.destination,
            'comment': review.comment[:100] + '...' if len(review.comment) > 100 else review.comment,
            'rating': review.rating,
            'date': review.date.strftime('%Y-%m-%d')
        }
        output.append(review_data)
    
    return jsonify({'top_rated_reviews': output})