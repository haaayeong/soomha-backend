from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

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

    mail.init_app(app)

    db.init_app(app)
    Migrate(app, db)

    from apps.crud import views as crud_views
    app.register_blueprint(crud_views.bp, url_prefix='/crud')

    with app.app_context():
        from apps.initialize import initialize_levels
        initialize_levels()

    return app
