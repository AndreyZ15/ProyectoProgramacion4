from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps

from ..models.user import User
from ..services.user_service import UserService
from ..database.db_config import db_session
from ..config import SECRET_KEY

user_service = UserService()

# Decorator para verificar token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = user_service.get_user_by_id(data['user_id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

# Decorator para verificar roles
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user.role not in roles:
                return jsonify({'message': 'Unauthorized access!'}), 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

# Registro de usuario
def register_user():
    data = request.get_json()
    
    # Validar datos de entrada
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields!'}), 400
    
    # Verificar si el usuario ya existe
    if user_service.get_user_by_email(data.get('email')):
        return jsonify({'message': 'User already exists!'}), 409
    
    # Crear el usuario
    hashed_password = generate_password_hash(data.get('password'))
    
    new_user = User(
        name=data.get('name'),
        email=data.get('email'),
        password=hashed_password,
        role=data.get('role', 'client')  # Por defecto, rol cliente normal
    )
    
    user_id = user_service.create_user(new_user)
    
    return jsonify({'message': 'User created successfully!', 'user_id': user_id}), 201

# Login de usuario
def login_user():
    auth = request.get_json()
    
    if not auth or not auth.get('email') or not auth.get('password'):
        return jsonify({'message': 'Missing email or password!'}), 401
    
    user = user_service.get_user_by_email(auth.get('email'))
    
    if not user:
        return jsonify({'message': 'Could not verify user!'}), 401
    
    if check_password_hash(user.password, auth.get('password')):
        # Generar token JWT
        token = jwt.encode({
            'user_id': user.id,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")
        
        return jsonify({
            'token': token,
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        })
    
    return jsonify({'message': 'Invalid credentials!'}), 401

# Obtener todos los usuarios (solo admin)
@token_required
@role_required(['admin'])
def get_all_users(current_user):
    users = user_service.get_all_users()
    output = []
    
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role
        }
        output.append(user_data)
    
    return jsonify({'users': output})

# Obtener un usuario por ID
@token_required
def get_user(current_user, user_id):
    # Solo permitir al admin ver otros usuarios o al propio usuario ver su perfil
    if current_user.role != 'admin' and current_user.id != int(user_id):
        return jsonify({'message': 'Unauthorized access!'}), 403
    
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    
    user_data = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role
    }
    
    return jsonify({'user': user_data})

# Actualizar usuario
@token_required
def update_user(current_user, user_id):
    # Solo permitir al admin actualizar otros usuarios o al propio usuario actualizar su perfil
    if current_user.role != 'admin' and current_user.id != int(user_id):
        return jsonify({'message': 'Unauthorized access!'}), 403
    
    data = request.get_json()
    
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    
    # Actualizar campos
    if data.get('name'):
        user.name = data.get('name')
    
    if data.get('email'):
        user.email = data.get('email')
    
    if data.get('password'):
        user.password = generate_password_hash(data.get('password'))
    
    # Solo admin puede cambiar roles
    if current_user.role == 'admin' and data.get('role'):
        user.role = data.get('role')
    
    user_service.update_user(user)
    
    return jsonify({'message': 'User updated successfully!'})

# Eliminar usuario
@token_required
@role_required(['admin'])
def delete_user(current_user, user_id):
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'message': 'User not found!'}), 404
    
    user_service.delete_user(user_id)
    
    return jsonify({'message': 'User deleted successfully!'})