import os
from typing import Any


class Config:
    SECRET_KEY: Any = os.environ.get('SECRET_KEY') or 'super-secret-pure-weaves-key'  # type: ignore[unknown-name]
    SQLALCHEMY_DATABASE_URI: Any = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'  # type: ignore[unknown-name]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_EXPIRY_HOURS = 24
    MAX_LOGIN_ATTEMPTS = 5
    ADMIN_PANEL_SECRET: Any = os.environ.get('ADMIN_PANEL_SECRET', 'pureweaves2024')  # type: ignore[unknown-name]
