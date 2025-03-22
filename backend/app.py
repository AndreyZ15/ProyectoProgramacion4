from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración de la aplicación
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB por defecto
    
    # Inicializar extensiones
    CORS(app)  # Habilitar CORS para todas las rutas
    
    # Configurar la base de datos
    from .database.db_config import init_db, shutdown_session
    
    # Registrar función para cerrar la sesión de BD después de cada solicitud
    @app.teardown_appcontext
    def close_db_session(exception=None):
        shutdown_session(exception)
    
    # Inicializar la base de datos
    with app.app_context():
        init_db()
    
    # Registrar blueprints
    from .views.user_view import user_bp
    from .views.package_view import package_bp
    from .views.booking_view import booking_bp
    from .views.news_view import news_bp
    from .views.review_view import review_bp
    from .views.payment_view import payment_bp
    
    app.register_blueprint(user_bp)
    app.register_blueprint(package_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(payment_bp)
    
    # Ruta principal
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Welcome to Travel Agency API',
            'version': '1.0.0',
            'status': 'online'
        })
    
    # Manejador de errores 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'message': 'Resource not found!'}), 404
    
    # Manejador de errores 500
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'message': 'Internal server error!'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    app.run(host=host, port=port)