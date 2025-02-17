from flask import Flask, jsonify,request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from apps.insertData import insert_data_to_db
from apps.naver_image_api import get_naver_image_thumbnail
from apps.dust import get_nearest_station


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
        
    @app.route('/api/place-cards', methods=['GET'])
    def placeCards():
        try:
            count = int(request.args.get('count', 10))  # 기본 10개 가져오기
            max_id = db.session.query(db.func.max(PlayAreas.id)).scalar()
            random_places = db.session.query(PlayAreas).filter(
                PlayAreas.id >= db.func.floor(db.func.random() * max_id)
            ).limit(count).all()

            places_data = []
            # 레코드가 존재하면 해당 레코드를 JSON 형태로 반환
            for place in random_places:
                image_url = get_naver_image_thumbnail(place.pfctNm)
                place_data = place.to_dict()
                place_data['thumbnail'] = image_url if image_url else '/images/noImage.jpg'

                air_quality = get_nearest_station(place.rgnCdNm)
                print("🟢 [API 응답] ",air_quality)
                place_data['pm10'] = air_quality.get('pm10')  # pm10 값
                place_data['pm25'] = air_quality.get('pm25')

                places_data.append(place_data)

            return jsonify(places_data), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route('/api/place-detail/<int:id>', methods=['GET'])
    def place_detail(id):
        try:
            # ID에 해당하는 데이터 조회
            place = db.session.query(PlayAreas).filter_by(id=id).first()
            print("🟢 [장소 상세] ",place)

            if not place:
                return jsonify({"error": "해당 ID의 장소를 찾을 수 없습니다."}), 404

            # 기본 데이터 구성
            place_data = place.to_dict()

            # 네이버 이미지 썸네일 추가
            image_url = get_naver_image_thumbnail(place.pfctNm, count=7)
            place_data['thumbnail'] = image_url if image_url else '/images/noImage.jpg'

            # 미세먼지 정보 추가
            air_quality = get_nearest_station(place.rgnCdNm)
            place_data['pm10'] = air_quality.get('pm10')  # 미세먼지 (PM10)
            place_data['pm25'] = air_quality.get('pm25')  # 초미세먼지 (PM2.5)

            return jsonify(place_data), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500


    return app



if __name__ == '__main__':
    app = create_app()  # Flask 애플리케이션 객체 생성
    app.run(debug=True)
