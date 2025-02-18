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

            # (1) 미세먼지 PM10 수치가 30 이하인 장소 최대 5개 조회
            low_pm_places = []
            candidate_places = db.session.query(PlayAreas).order_by(db.func.random()).limit(20).all()
            for place in candidate_places:
                if len(low_pm_places) >= 5:
                    break
                air_quality = get_nearest_station(place.rgnCdNm)
                if not air_quality:
                    continue  # air_quality가 없으면 이 장소는 건너뜀

                pm10_value = air_quality.get('pm10', 999)

                # pm10_value가 '-'인 경우를 처리
                if pm10_value == '-':
                    pm10_value = 10  # 혹은 다른 값으로 설정
                    
                # pm10_value가 숫자 문자열일 경우 숫자로 변환
                try:
                    pm10_value = float(pm10_value)  # float로 변환 (정수로 변환할 수도 있지만, 소수점도 고려할 경우 float가 안전)
                except ValueError:
                    pm10_value = 10  

                # pm10_value가 숫자인지 확인하고 비교
                if pm10_value <= 30 and len(low_pm_places) < 5:
                    image_url = get_naver_image_thumbnail(place.pfctNm)
                    place_data = place.to_dict()
                    place_data['thumbnail'] = image_url if image_url else '/images/noImage.jpg'
                    place_data['pm10'] = pm10_value
                    place_data['pm25'] = air_quality.get('pm25')
                    low_pm_places.append(place_data)

            # (2) 나머지 개수만큼 랜덤 조회 (중복 방지)
            remaining_count = max(count - len(low_pm_places), 0)
            random_places = []
            if remaining_count > 0:
                excluded_ids = [p['id'] for p in low_pm_places]
                query = db.session.query(PlayAreas)
                if excluded_ids:
                    query = query.filter(~PlayAreas.id.in_(excluded_ids))
                random_places_query = query.order_by(db.func.random()).limit(remaining_count).all()

                for place in random_places_query:
                    air_quality = get_nearest_station(place.rgnCdNm)
                    if not air_quality:
                        continue  # air_quality가 없으면 이 장소는 건너뜀

                    image_url = get_naver_image_thumbnail(place.pfctNm)
                    place_data = place.to_dict()
                    place_data['thumbnail'] = image_url if image_url else '/images/noImage.jpg'
                    place_data['pm10'] = air_quality.get('pm10')
                    place_data['pm25'] = air_quality.get('pm25')
                    random_places.append(place_data)

            # 최종적으로 low_pm_places와 random_places 결합
            places_data = low_pm_places + random_places

            return jsonify(places_data), 200

        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({"error": str(e)}), 500


        
    @app.route('/api/place-detail/<int:id>', methods=['GET'])
    def place_detail(id):
        try:
            # ID에 해당하는 데이터 조회
            place = db.session.query(PlayAreas).filter_by(id=id).first()
            # print("🟢 [장소 상세] ",place)

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
        
    @app.route('/api/place-cards-scroll', methods=['GET'])
    def placeCardsScroll():
        try:
            # 페이징 처리용 파라미터
            count = int(request.args.get('count', 10))  # 요청 시 가져올 데이터 개수 (기본값 10)
            offset = int(request.args.get('offset', 0))  # 시작 인덱스 (기본값 0)

            # 장소 데이터 조회
            places_data = []
            candidate_places = db.session.query(PlayAreas).offset(offset).limit(count).all()

            for place in candidate_places:

                # air_quality = get_nearest_station(place.rgnCdNm)
                air_quality = {
                    "pm10": 10,
                    "pm25": 5
                }
                if not air_quality:
                    continue  # air_quality가 없으면 이 장소는 건너뜀

                image_url = get_naver_image_thumbnail(place.pfctNm)
                place_data = place.to_dict()
                place_data['thumbnail'] = image_url if image_url else '/images/noImage.jpg'
                place_data['pm10'] = air_quality.get('pm10')
                place_data['pm25'] = air_quality.get('pm25')

                places_data.append(place_data)

            # 최종 데이터 반환
            return jsonify(places_data), 200

        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({"error": str(e)}), 500




    return app



if __name__ == '__main__':
    app = create_app()  # Flask 애플리케이션 객체 생성
    app.run(debug=True)
