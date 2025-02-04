from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)  # React에서 Flask API 호출 허용

    app.config.from_mapping(
        # mysql 연결
        SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://root:1234@localhost:3306/soomha',

        # SQLAlchemy가 변경 사항 추적하지 않도록 함.
        SQLALCHEMY_TRACK_MODIFICATIONS=False,

        # SQLAlchemy가 실행하는 SQL 쿼리를 콘솔에 출력하게 함.
        SQLALCHEMY_ECHO=True
    )

    db.init_app(app)
    Migrate(app, db)

    @app.route('/api/test', methods=['GET'])
    def test():
        return jsonify({"message": "Hello from Flask!"})

    return app

if __name__ == '__main__':
    app = create_app()  # Flask 애플리케이션 객체 생성
    app.run(debug=True)
