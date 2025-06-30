from flask import Flask, session
from flask_login import LoginManager
from .config import Config
from .routes.auth import auth_bp
from .routes.documents import documents_bp
from .models import User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Cargar usuario para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        username = session.get('username')
        is_superuser = session.get('is_superuser', False)
        department_id = session.get('department_id')
        role = session.get('role')
        if username:
            return User(user_id, username, is_superuser, department_id, role)
        return None
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    
    return app