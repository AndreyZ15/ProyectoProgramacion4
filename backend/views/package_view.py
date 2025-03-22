from flask import Blueprint, request, jsonify
from ..controllers.package_controller import (
    create_package, get_all_packages, get_package, update_package,
    delete_package
)
from ..controllers import token_required, role_required

# Crear el Blueprint para las rutas de paquetes
package_bp = Blueprint('packages', __name__, url_prefix='/api/packages')

# Ruta para obtener todos los paquetes
@package_bp.route('', methods=['GET'])
def get_packages():
    return get_all_packages()

# Ruta para obtener un paquete específico
@package_bp.route('/<int:package_id>', methods=['GET'])
def get_package_by_id(package_id):
    return get_package(package_id)

# Ruta para crear un nuevo paquete (solo admin)
@package_bp.route('', methods=['POST'])
@token_required
@role_required(['admin'])
def add_package(current_user):
    return create_package(current_user)

# Ruta para actualizar un paquete (solo admin)
@package_bp.route('/<int:package_id>', methods=['PUT'])
@token_required
@role_required(['admin'])
def update_package_by_id(current_user, package_id):
    return update_package(current_user, package_id)

# Ruta para eliminar un paquete (solo admin)
@package_bp.route('/<int:package_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_package_by_id(current_user, package_id):
    return delete_package(current_user, package_id)

# Ruta para buscar paquetes
@package_bp.route('/search', methods=['GET'])
def search_packages():
    query = request.args.get('q', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_duration = request.args.get('min_duration', type=int)
    max_duration = request.args.get('max_duration', type=int)
    difficulty = request.args.get('difficulty')
    season = request.args.get('season')
    
    filters = {}
    if min_price is not None:
        filters['min_price'] = min_price
    if max_price is not None:
        filters['max_price'] = max_price
    if min_duration is not None:
        filters['min_duration'] = min_duration
    if max_duration is not None:
        filters['max_duration'] = max_duration
    if difficulty:
        filters['difficulty'] = difficulty
    if season:
        filters['season'] = season
    
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.package_service import PackageService
    
    try:
        package_service = PackageService()
        packages = package_service.search_packages(query, filters)
        
        result = []
        for package in packages:
            result.append({
                'id': package.id,
                'destination': package.destination,
                'description': package.description[:150] + '...' if len(package.description) > 150 else package.description,
                'price': package.price,
                'duration': package.duration,
                'images': package.images.split(',')[0] if package.images else None,
                'average_rating': package.get_average_rating()
            })
        
        return jsonify({'packages': result})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para obtener los paquetes mejor calificados
@package_bp.route('/top-rated', methods=['GET'])
def get_top_rated():
    limit = request.args.get('limit', 5, type=int)
    
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.package_service import PackageService
    
    try:
        package_service = PackageService()
        packages = package_service.get_top_rated_packages(limit)
        
        result = []
        for package in packages:
            result.append({
                'id': package.id,
                'destination': package.destination,
                'price': package.price,
                'duration': package.duration,
                'images': package.images.split(',')[0] if package.images else None,
                'average_rating': package.get_average_rating()
            })
        
        return jsonify({'top_rated_packages': result})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Ruta para obtener paquetes similares
@package_bp.route('/<int:package_id>/similar', methods=['GET'])
def get_similar_packages(package_id):
    limit = request.args.get('limit', 3, type=int)
    
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from ..services.package_service import PackageService
    
    try:
        package_service = PackageService()
        packages = package_service.get_similar_packages(package_id, limit)
        
        result = []
        for package in packages:
            result.append({
                'id': package.id,
                'destination': package.destination,
                'price': package.price,
                'duration': package.duration,
                'images': package.images.split(',')[0] if package.images else None
            })
        
        return jsonify({'similar_packages': result})
    except Exception as e:
        return jsonify({'message': str(e)}), 500