from flask import Blueprint, request, jsonify
from ..controllers.user_controller import (
    register_user, login_user, get_all_users, get_user, 
    update_user, delete_user
)
from ..controllers import token_required, role_required

# Crear el Blueprint para las rutas de usuarios
user_bp = Blueprint('users', __name__, url_prefix='/api/users')

# Ruta para registrar un nuevo usuario
@user_bp.route('/register', methods=['POST'])
def register():
    return register_user()

# Ruta para iniciar sesión
@user_bp.route('/login', methods=['POST'])
def login():
    return login_user()

# Ruta para obtener todos los usuarios (solo admin)
@user_bp.route('', methods=['GET'])
@token_required
@role_required(['admin'])
def get_users(current_user):
    return get_all_users(current_user)

# Ruta para obtener un usuario específico por ID
@user_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user_by_id(current_user, user_id):
    return get_user(current_user, user_id)

# Ruta para actualizar un usuario
@user_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user_by_id(current_user, user_id):
    return update_user(current_user, user_id)

# Ruta para eliminar un usuario
@user_bp.route('/<int:user_id>', methods=['DELETE'])
@token_required
@role_required(['admin'])
def delete_user_by_id(current_user, user_id):
    return delete_user(current_user, user_id)

# Ruta para obtener el perfil del usuario actual
@user_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return get_user(current_user, current_user.id)

# Ruta para actualizar el perfil del usuario actual
@user_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    return update_user(current_user, current_user.id)

# Ruta para cambiar contraseña
@user_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    data = request.get_json()
    
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'message': 'Missing required fields!'}), 400
    
    # Esta función debería estar en el controlador, pero la incluimos aquí como ejemplo
    from werkzeug.security import check_password_hash, generate_password_hash
    from ..services.user_service import UserService
    
    user_service = UserService()
    
    # Verificar contraseña actual
    if not check_password_hash(current_user.password, data.get('current_password')):
        return jsonify({'message': 'Current password is incorrect!'}), 401
    
    # Actualizar a nueva contraseña
    current_user.password = generate_password_hash(data.get('new_password'))
    user_service.update_user(current_user)
    
    return jsonify({'message': 'Password updated successfully!'})