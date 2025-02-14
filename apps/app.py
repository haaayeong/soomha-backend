from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_session import Session

from apps.config import config
import os

config_key = os.environ.get('FLASK_CONFIG_KEY')

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    CORS(app)  # React에서 Flask API 호출 허용
    app.config['WTF_CSRF_ENABLED'] = False

    app.config.from_object(config[config_key])

    # 세션과 관련된 설정
    app.config['SECRET_KEY'] = app.config['SESSION_COOKIE_SECRET']
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_FILE_DIR'] = "./flask_session"

    Session(app)

    mail.init_app(app)
    db.init_app(app)
    Migrate(app, db)

    from apps.crud import views as crud_views
    app.register_blueprint(crud_views.bp, url_prefix='/crud')

    with app.app_context():
        from apps.initialize import initialize_levels
        initialize_levels()

    return app
