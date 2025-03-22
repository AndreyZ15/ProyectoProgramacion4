from flask import request, jsonify
import os
from werkzeug.utils import secure_filename
from datetime import datetime

from ..models.package import Package
from ..services.package_service import PackageService
from ..config import UPLOAD_FOLDER
from . import token_required, role_required

package_service = PackageService()

# Crear un nuevo paquete turístico (solo admin)
@token_required
@role_required(['admin'])
def create_package(current_user):
    data = request.form
    
    # Validar datos de entrada
    if not data or not data.get('destination') or not data.get('price') or not data.get('duration'):
        return jsonify({'message': 'Missing required fields!'}), 400
    
    # Procesar imágenes
    images = []
    if 'images' in request.files:
        files = request.files.getlist('images')
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                images.append(unique_filename)
    
    # Crear el paquete
    new_package = Package(
        destination=data.get('destination'),
        description=data.get('description'),
        price=float(data.get('price')),
        duration=int(data.get('duration')),
        included_services=data.get('included_services'),
        images=','.join(images),
        availability=True
    )
    
    package_id = package_service.create_package(new_package)
    
    return jsonify({'message': 'Package created successfully!', 'package_id': package_id}), 201

# Obtener todos los paquetes
def get_all_packages():
    packages = package_service.get_all_packages()
    output = []
    
    for package in packages:
        package_data = {
            'id': package.id,
            'destination': package.destination,
            'description': package.description,
            'price': package.price,
            'duration': package.duration,
            'included_services': package.included_services,
            'images': package.images.split(',') if package.images else [],
            'availability': package.availability
        }
        output.append(package_data)
    
    return jsonify({'packages': output})

# Obtener un paquete por ID
def get_package(package_id):
    package = package_service.get_package_by_id(package_id)
    
    if not package:
        return jsonify({'message': 'Package not found!'}), 404
    
    # Preparar datos del paquete
    package_data = {
        'id': package.id,
        'destination': package.destination,
        'description': package.description,
        'price': package.price,
        'duration': package.duration,
        'included_services': package.included_services,
        'images': package.images.split(',') if package.images else [],
        'availability': package.availability
    }
    
    # Obtener reseñas relacionadas
    reviews = package_service.get_package_reviews(package_id)
    review_data = []
    
    for review in reviews:
        review_data.append({
            'id': review.id,
            'user_name': review.user.name,
            'comment': review.comment,
            'rating': review.rating,
            'date': review.date.strftime('%Y-%m-%d')
        })
    
    package_data['reviews'] = review_data
    
    # Calcular calificación promedio
    if review_data:
        avg_rating = sum(r['rating'] for r in review_data) / len(review_data)
        package_data['average_rating'] = round(avg_rating, 1)
    else:
        package_data['average_rating'] = 0
    
    return jsonify({'package': package_data})

# Actualizar un paquete (solo admin)
@token_required
@role_required(['admin'])
def update_package(current_user, package_id):
    data = request.form
    
    package = package_service.get_package_by_id(package_id)
    
    if not package:
        return jsonify({'message': 'Package not found!'}), 404
    
    # Actualizar campos
    if data.get('destination'):
        package.destination = data.get('destination')
    
    if data.get('description'):
        package.description = data.get('description')
    
    if data.get('price'):
        package.price = float(data.get('price'))
    
    if data.get('duration'):
        package.duration = int(data.get('duration'))
    
    if data.get('included_services'):
        package.included_services = data.get('included_services')
    
    if data.get('availability') is not None:
        package.availability = bool(data.get('availability'))
    
    # Procesar nuevas imágenes
    if 'images' in request.files:
        files = request.files.getlist('images')
        
        if files and files[0].filename:
            # Eliminar imágenes antiguas (opcional)
            # delete_old_images(package.images)
            
            images = []
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                    file.save(file_path)
                    images.append(unique_filename)
            
            package.images = ','.join(images)
    
    package_service.update_package(package)
    
    return jsonify({'message': 'Package updated successfully!'})

# Eliminar un paquete (solo admin)
@token_required
@role_required(['admin'])
def delete_package(current_user, package_id):
    package = package_service.get_package_by_id(package_id)
    
    if not package:
        return jsonify({'message': 'Package not found!'}), 404
    
    # Eliminar imágenes asociadas (opcional)
    # delete_old_images(package.images)
    
    package_service.delete_package(package_id)
    
    return jsonify({'message': 'Package deleted successfully!'})

# Función auxiliar para validar extensiones de archivo
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Función auxiliar para eliminar imágenes (opcional)
def delete_old_images(images_string):
    if not images_string:
        return
    
    images = images_string.split(',')
    for image in images:
        try:
            file_path = os.path.join(UPLOAD_FOLDER, image)
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting image {image}: {str(e)}")