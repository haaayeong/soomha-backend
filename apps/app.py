from flask import Flask, session
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_session import Session
from flask_jwt_extended import JWTManager
from datetime import timedelta

from apps.config import config
import os

config_key = os.environ.get('FLASK_CONFIG_KEY', 'local')

db = SQLAlchemy()
mail = Mail()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, static_folder='static')
    CORS(app, supports_credentials=True, resources={r'/*' : {'origins' : ['http://localhost:5173', 'http://127.0.0.1:5173']}})  # React에서 Flask API 호출 허용
    app.config['WTF_CSRF_ENABLED'] = False

    app.config.from_object(config['local'])

    app.config['JWT_SECRET_KEY'] = 'abcd'

    # 세션과 관련된 설정
    # app.secret_key= app.config['SECRET_KEY']
    app.secret_key = 'abcd'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_FILE_DIR'] = "./flask_session"

    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True
    Session(app)

    mail.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    Migrate(app, db)

    from apps.crud import views as crud_views
    app.register_blueprint(crud_views.bp, url_prefix='/crud')

    from apps.crud import auth as crud_auth
    app.register_blueprint(crud_auth.bp, url_prefix='/auth')

    with app.app_context():
        from apps.initialize import initialize_levels
        initialize_levels()

    return app
