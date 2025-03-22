from flask import Blueprint, request, jsonify
from ..controllers.review_controller import (
    create_review, get_package_reviews, get_user_reviews, 
    get_review, update_review, delete_review,
    get_recent_reviews, get_top_rated_reviews
)
from ..controllers import token_required, role_required

# Crear el Blueprint para las rutas de reseñas
review_bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')

# Ruta para crear una nueva reseña
@review_bp.route('', methods=['POST'])
@token_required
def add_review(current_user):
    return create_review(current_user)

# Ruta para obtener todas las reseñas de un paquete
@review_bp.route('/package/<int:package_id>', methods=['GET'])
def get_reviews_by_package(package_id):
    return get_package_reviews(package_id)

# Ruta para obtener todas las reseñas de un usuario
@review_bp.route('/user', methods=['GET'])
@token_required
def get_reviews_by_user(current_user):
    return get_user_reviews(current_user)

# Ruta para obtener una reseña específica
@review_bp.route('/<int:review_id>', methods=['GET'])
def get_review_by_id(review_id):
    return get_review(review_id)

# Ruta para actualizar una reseña
@review_bp.route('/<int:review_id>', methods=['PUT'])
@token_required
def update_review_by_id(current_user, review_id):
    return update_review(current_user, review_id)

# Ruta para eliminar una reseña
@review_bp.route('/<int:review_id>', methods=['DELETE'])
@token_required
def delete_review_by_id(current_user, review_id):
    return delete_review(current_user, review_id)

# Ruta para obtener las reseñas más recientes
@review_bp.route('/recent', methods=['GET'])
def get_recent():
    limit = request.args.get('limit', 5, type=int)
    
    # Esta función podría estar en el controlador con el parámetro limit
    # pero la implementamos aquí para mostrar cómo se puede hacer
    from ..services.review_service import ReviewService
    
    try:
        review_service = ReviewService()
        reviews = review_service.get_recent_reviews(limit)
        
        result = []
        for review in reviews:
            result.append({
                'id': review.id,
                'user_name': review.user.name,
                'package_destination': review.package.destination,
                'comment': review.comment[:100] + '...' if len(review.comment) > 100 else review.comment,
                'rating': review.rating,
                'date': review.date.strftime('%Y-%m-%d')
            })
        
        return jsonify({'recent_reviews': result})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para obtener las reseñas con mejor calificación
@review_bp.route('/top-rated', methods=['GET'])
def get_top_rated():
    limit = request.args.get('limit', 5, type=int)
    return get_top_rated_reviews(limit)

# Ruta para aprobar una reseña (solo admin)
@review_bp.route('/<int:review_id>/approve', methods=['PUT'])
@token_required
@role_required(['admin'])
def approve_review(current_user, review_id):
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.review_service import ReviewService
    
    try:
        review_service = ReviewService()
        result = review_service.approve_review(review_id)
        
        if result:
            return jsonify({'message': 'Review approved successfully!'})
        else:
            return jsonify({'message': 'Review not found!'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para rechazar una reseña (solo admin)
@review_bp.route('/<int:review_id>/reject', methods=['PUT'])
@token_required
@role_required(['admin'])
def reject_review(current_user, review_id):
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.review_service import ReviewService
    
    try:
        review_service = ReviewService()
        result = review_service.reject_review(review_id)
        
        if result:
            return jsonify({'message': 'Review rejected successfully!'})
        else:
            return jsonify({'message': 'Review not found!'}), 404
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para obtener reseñas pendientes de aprobación (solo admin)
@review_bp.route('/pending', methods=['GET'])
@token_required
@role_required(['admin'])
def get_pending_reviews(current_user):
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.review_service import ReviewService
    
    try:
        review_service = ReviewService()
        reviews = review_service.get_pending_reviews()
        
        result = []
        for review in reviews:
            result.append({
                'id': review.id,
                'user_id': review.user_id,
                'user_name': review.user.name,
                'package_id': review.package_id,
                'package_destination': review.package.destination,
                'comment': review.comment,
                'rating': review.rating,
                'date': review.date.strftime('%Y-%m-%d')
            })
        
        return jsonify({'pending_reviews': result})
    except Exception as e:
        return jsonify({'message': str(e)}), 500