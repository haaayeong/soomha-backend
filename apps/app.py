from flask import Flask, jsonify,request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager
from flask_session import Session
from flask_mail import Mail
import random

from apps.insertData import insert_data_to_db
from apps.naver_image_api import get_naver_image_thumbnail
from apps.dust import get_nearest_station
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
        from apps.crud.models import Level
        from sqlalchemy.exc import OperationalError
        from sqlalchemy import inspect

        try:
            inspector = inspect(db.engine)
            # 테이블이 존재하는지 확인
            if inspector.has_table('level'):
                from apps.initialize import initialize_levels
                initialize_levels()
        except OperationalError:
            print("테이블이 아직 생성되지 않았음. initialize_levels() 실행을 건너뜀.")
        
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
                # air_quality = get_nearest_station(place.rgnCdNm)
                air_quality = {
                    'pm10': random.randint(0, 150),  # pm10 값을 0~150 범위의 랜덤 값으로 설정
                    'pm25': random.randint(0, 75)    # pm25 값을 0~75 범위의 랜덤 값으로 설정
                }
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
                    # air_quality = get_nearest_station(place.rgnCdNm)
                    air_quality = {
                    'pm10': random.randint(0, 250),  
                    'pm25': random.randint(0, 200)    # pm25 값을 0~75 범위의 랜덤 값으로 설정
                }
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
            # air_quality = get_nearest_station(place.rgnCdNm)
            air_quality = {
                'pm10': random.randint(0, 150),  # pm10 값을 0~150 범위의 랜덤 값으로 설정
                'pm25': random.randint(0, 75)    # pm25 값을 0~75 범위의 랜덤 값으로 설정
            }
            
            place_data['pm10'] = air_quality.get('pm10')  # 미세먼지 (PM10)
            place_data['pm25'] = air_quality.get('pm25')  # 초미세먼지 (PM2.5)

            return jsonify(place_data), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        


    @app.route('/api/place-cards-scroll', methods=['GET'])
    def placeCardsScroll():
        try:
            # 📌 페이징 처리용 파라미터
            count = int(request.args.get('count', 10))  # 가져올 데이터 개수
            offset = int(request.args.get('offset', 0))  # 시작 인덱스

            # 📌 필터 값 받아오기
            dust_level = request.args.get('dust', 'all')  # 미세먼지 농도
            category = request.args.get('category', 'all')  # 카테고리
            indoorOutdoor = request.args.get('indoorOutdoor', 'all')  # 실내/실외
            is_next_week = request.args.get('isNextWeek', 'false').lower() == 'true'  # 다음주 여부

            print(f'🟢 [필터 정보] dust: {dust_level}, category: {category}, indoorOutdoor: {indoorOutdoor}, isNextWeek: {is_next_week}')

            # 📌 기본 쿼리 생성 (미세먼지는 DB에서 필터링하지 않음)
            query = db.session.query(PlayAreas)

            # 📌 카테고리 필터 적용
            if category != 'all':
                query = query.filter(PlayAreas.instlPlaceCdNm == category)

            # 📌 실내/실외 필터 적용
            if indoorOutdoor != 'all':
                query = query.filter(db.func.lower(PlayAreas.idrodrCdNm) == indoorOutdoor.lower())

            # 📌 랜덤으로 장소 데이터 조회
            places_data = []
            candidate_places = query.order_by(db.func.random()).offset(offset).limit(count).all()

            for place in candidate_places:
                # 📌 실시간 미세먼지 데이터 조회 (API 호출)
                # air_quality = get_nearest_station(place.rgnCdNm)  # API에서 미세먼지 데이터 가져오기
                air_quality = {
                    'pm10': random.randint(0, 150),  # pm10 값을 0~150 범위의 랜덤 값으로 설정
                    'pm25': random.randint(0, 75)    # pm25 값을 0~75 범위의 랜덤 값으로 설정
                }

                if not air_quality:
                    continue  # air_quality 데이터가 없으면 해당 장소 제외

                pm10 = air_quality.get('pm10')
                pm25 = air_quality.get('pm25')

                 # 📌 pm10이 유효한 값인지 확인하고, 유효하지 않으면 필터링
                if pm10 == '-' or pm10 is None:
                    continue  # 미세먼지 값이 유효하지 않으면 해당 장소 제외

                pm10 = float(pm10)  # pm10을 float로 변환

                # 📌 미세먼지 필터 적용 (여기서 필터링)
                if dust_level != 'all':
                    dust_mapping = {
                        'good': (0, 30),
                        'normal': (31, 80),
                        'bad': (81, 150),
                        'very-bad': (151, 999)
                    }

                    # 📌 dust_level에 맞는 PM10 값 범위 확인
                    min_pm10, max_pm10 = dust_mapping.get(dust_level, (None, None))

                    if min_pm10 is not None and max_pm10 is not None:
                        # ✅ 미세먼지 수치가 해당 범위 내에 있는지 확인
                        if not (min_pm10 <= pm10 <= max_pm10):
                            continue  # 필터 조건을 만족하지 않으면 제외


                # 📌 이미지 URL 가져오기
                image_url = get_naver_image_thumbnail(place.pfctNm)

                # 📌 최종 데이터 정리
                place_data = place.to_dict()
                place_data['thumbnail'] = image_url if image_url else '/images/noImage.jpg'
                place_data['pm10'] = pm10
                place_data['pm25'] = pm25

                places_data.append(place_data)

            # 📌 최종 데이터 반환
            return jsonify(places_data), 200

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return jsonify({"error": str(e)}), 500





    return app

if __name__ == '__main__':
    app = create_app()  # Flask 애플리케이션 객체 생성
    app.run(debug=True)
