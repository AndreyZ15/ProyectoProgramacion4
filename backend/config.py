import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
SECRET_KEY = os.getenv('SECRET_KEY', 'tu_clave_secreta_aqui_muy_segura_y_larga_para_jwt')
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# Configuración de la base de datos
DB_SERVER = os.getenv('DB_SERVER', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'TravelAgencyDB')
DB_USER = os.getenv('DB_USER', 'sa')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'YourStrongPassword')
DB_DRIVER = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')

# Configuración del JWT
JWT_EXPIRATION_DELTA = int(os.getenv('JWT_EXPIRATION_DELTA', 86400))  # 24 horas en segundos
JWT_ALGORITHM = 'HS256'

# Configuración de carga de archivos
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

# Configuración de correo electrónico
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.example.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'notificaciones@tuagenciadeviajes.com')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'tu_password_de_correo')
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'notificaciones@tuagenciadeviajes.com')

# Configuración de generación de PDF
PDF_OUTPUT_DIR = os.getenv('PDF_OUTPUT_DIR', 'static/pdfs')

# Configuración de la API
API_VERSION = '1.0.0'
API_PREFIX = '/api'
ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 10))

# Configuración de seguridad
BCRYPT_LOG_ROUNDS = int(os.getenv('BCRYPT_LOG_ROUNDS', 12))
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

# Configuración de caché
CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))  # 5 minutos

# Configuración de sesiones
SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')
SESSION_PERMANENT = os.getenv('SESSION_PERMANENT', 'False').lower() in ('true', '1', 't')
SESSION_USE_SIGNER = os.getenv('SESSION_USE_SIGNER', 'True').lower() in ('true', '1', 't')
SESSION_KEY_PREFIX = os.getenv('SESSION_KEY_PREFIX', 'agencia_viajes_')

# Configuración específica para la agencia de viajes
DEFAULT_CURRENCY = os.getenv('DEFAULT_CURRENCY', 'USD')
MAX_TRAVELERS_PER_BOOKING = int(os.getenv('MAX_TRAVELERS_PER_BOOKING', 10))
BOOKING_CANCELLATION_DEADLINE_DAYS = int(os.getenv('BOOKING_CANCELLATION_DEADLINE_DAYS', 30))
VIP_DISCOUNT_PERCENTAGE = float(os.getenv('VIP_DISCOUNT_PERCENTAGE', 10.0))

# Configuración de logs
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')

# Configuración de redes sociales para login (si se implementa)
SOCIAL_AUTH_PROVIDERS = {
    'google': {
        'enabled': os.getenv('GOOGLE_AUTH_ENABLED', 'False').lower() in ('true', '1', 't'),
        'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET', '')
    },
    'facebook': {
        'enabled': os.getenv('FACEBOOK_AUTH_ENABLED', 'False').lower() in ('true', '1', 't'),
        'client_id': os.getenv('FACEBOOK_CLIENT_ID', ''),
        'client_secret': os.getenv('FACEBOOK_CLIENT_SECRET', '')
    }
}

# Función para obtener la configuración completa como diccionario
def get_config():
    """Retorna la configuración completa como un diccionario"""
    return {key: value for key, value in globals().items() 
            if key.isupper() and not key.startswith('_')}