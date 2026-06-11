from flask import Flask
from flask_login import LoginManager
from app.config import Config
from app.models import db, User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Import and register blueprints
    from app.auth.routes import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from app.tasks.routes import tasks as tasks_blueprint
    app.register_blueprint(tasks_blueprint)
    
    # Context processor to expose modern date functions to templates
    @app.context_processor
    def inject_now():
        from datetime import date
        return {'today': date.today()}

    # Create tables
    with app.app_context():
        db.create_all()
        
    return app
