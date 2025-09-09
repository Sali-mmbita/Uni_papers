from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()  
def create_app(config_class="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    bcrypt.init_app(app)  # ✅ register bcrypt
    
    # ✅ Initialize LoginManager
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # redirect here if not logged in
    login_manager.login_message_category = "info"  # flash message style

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    # from .main import main as main_blueprint
    # app.register_blueprint(main_blueprint)
    
    from .main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)


    return app

# ✅ User loader function
from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
