from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

from ..models.user import User
from ..database.db_config import db_session

class UserService:
    """Servicio para gestionar operaciones relacionadas con usuarios"""

    def get_all_users(self):
        """Obtiene todos los usuarios del sistema"""
        try:
            return User.query.all()
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al obtener usuarios: {str(e)}")

    def get_user_by_id(self, user_id):
        """Obtiene un usuario por su ID"""
        try:
            return User.query.filter_by(id=user_id).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener usuario: {str(e)}")

    def get_user_by_email(self, email):
        """Obtiene un usuario por su correo electrónico"""
        try:
            return User.query.filter_by(email=email).first()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener usuario por email: {str(e)}")

    def create_user(self, user):
        """Crea un nuevo usuario en el sistema"""
        try:
            db_session.add(user)
            db_session.commit()
            return user.id
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al crear usuario: {str(e)}")

    def update_user(self, user):
        """Actualiza la información de un usuario existente"""
        try:
            db_session.commit()
            return True
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al actualizar usuario: {str(e)}")

    def delete_user(self, user_id):
        """Elimina un usuario del sistema"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                db_session.delete(user)
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al eliminar usuario: {str(e)}")

    def update_password(self, user_id, new_password):
        """Actualiza la contraseña de un usuario"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                user.password = generate_password_hash(new_password)
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al actualizar contraseña: {str(e)}")

    def update_last_login(self, user_id):
        """Actualiza la fecha del último inicio de sesión"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                user.last_login = datetime.utcnow()
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al actualizar último inicio de sesión: {str(e)}")

    def get_vip_users(self):
        """Obtiene todos los usuarios VIP"""
        try:
            return User.query.filter_by(role='vip').all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener usuarios VIP: {str(e)}")

    def get_admin_users(self):
        """Obtiene todos los usuarios administradores"""
        try:
            return User.query.filter_by(role='admin').all()
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener administradores: {str(e)}")

    def deactivate_user(self, user_id):
        """Desactiva un usuario (sin eliminarlo)"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                user.is_active = False
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al desactivar usuario: {str(e)}")

    def activate_user(self, user_id):
        """Activa un usuario previamente desactivado"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                user.is_active = True
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al activar usuario: {str(e)}")

    def change_user_role(self, user_id, new_role):
        """Cambia el rol de un usuario"""
        try:
            user = self.get_user_by_id(user_id)
            if user and new_role in ['admin', 'client', 'vip']:
                user.role = new_role
                db_session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db_session.rollback()
            raise Exception(f"Error al cambiar rol de usuario: {str(e)}")

    def count_users_by_role(self):
        """Cuenta usuarios por rol (para estadísticas)"""
        try:
            admin_count = User.query.filter_by(role='admin').count()
            client_count = User.query.filter_by(role='client').count()
            vip_count = User.query.filter_by(role='vip').count()
            
            return {
                'admin': admin_count,
                'client': client_count,
                'vip': vip_count,
                'total': admin_count + client_count + vip_count
            }
        except SQLAlchemyError as e:
            raise Exception(f"Error al contar usuarios por rol: {str(e)}")