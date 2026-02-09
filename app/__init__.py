import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # type: ignore[assignment]

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object("config.Config")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)

    from .routes import main
    from .auth import auth
    from .admin import admin

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)

    admin_email = os.getenv("ADMIN_EMAIL")
    if admin_email:
        from .models import User
        with app.app_context():
            user = User.query.filter_by(email=admin_email).first()
            if user and user.role != "admin":
                user.role = "admin"
                db.session.commit()

    return app
