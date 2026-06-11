from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt  # type: ignore
from flask_login import LoginManager  # type: ignore[missing-import]
from flask_migrate import Migrate  # type: ignore
from sqlalchemy import MetaData
from config import Config
from typing import Any
import secrets

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class: Any=Config) -> None:  # type: ignore[unknown-name]
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Simple session-based CSRF token for non-WTF forms
    @app.before_request
    def _ensure_csrf_token() -> None:
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_urlsafe(32)

    @app.context_processor
    def _inject_csrf_token() -> dict:
        return {'csrf_token': session.get('csrf_token')}

    # Serve project-level assets directory at /assets/*
    from flask import send_from_directory
    import os

    @app.route('/assets/<path:filename>')
    def project_assets(filename: str):
        assets_dir = os.path.join(app.root_path, '..', 'assets')
        return send_from_directory(assets_dir, filename)

    return app  # type: ignore[BSK-E0013]
