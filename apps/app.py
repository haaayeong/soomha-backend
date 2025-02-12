from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from apps.insertData import insert_data_to_db
from apps.naver_image_api import get_naver_image_thumbnail


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

    from apps.models import PlayAreas

    @app.route('/api/test', methods=['GET'])
    def test():
        return jsonify({"message": "Hello from Flask!"})


    @app.route('/api/insertDB', methods=['GET'])
    def insertDB():
        data = insert_data_to_db()  # insertData.py에서 데이터 가져오기
        
        if "error" in data:
            # 오류 발생시 반환
            return jsonify(data), 400
        else:
            # 정상적인 데이터 반환
            return jsonify({"message": "데이터 호출 성공"})
        
    @app.route('/api/place-card', methods=['GET'])
    def placeCard():
        try:
            # DB에서 랜덤한 레코드를 하나 꺼내옴
            random_place = db.session.query(PlayAreas).order_by(db.func.random()).first()

            # 레코드가 존재하면 해당 레코드를 JSON 형태로 반환
            if random_place:
                image_url = get_naver_image_thumbnail(random_place.pfctNm)
                place_data = random_place.to_dict()
                place_data['thumbnail'] = image_url if image_url else '/images/thumb.jpg'

                return jsonify(place_data), 200  # 랜덤 레코드 반환
            else:
                return jsonify({"message": "No records found."}), 404  # 레코드가 없을 경우
        except Exception as e:
            return jsonify({"error": str(e)}), 500  # 예외 처리      


    return app



if __name__ == '__main__':
    app = create_app()  # Flask 애플리케이션 객체 생성
    app.run(debug=True)
