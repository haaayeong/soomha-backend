# 1차 개선 레코드 조회
    # @app.route('/api/place-cards', methods=['GET'])
    # def placeCards():
    #     try:
    #         count = int(request.args.get('count', 10))  # 기본 10개 가져오기
    #         max_id = db.session.query(db.func.max(PlayAreas.id)).scalar()

    #         # (1) 미세먼지 30 이하인 장소 찾기 (최대 5개)
    #         low_pm_places = []
    #         while len(low_pm_places) < 5:
    #             random_place = db.session.query(PlayAreas).order_by(db.func.random()).first()
    #             if not random_place:  # 혹시 데이터가 없는 경우 방어 코드
    #                 break
                
    #             # 미세먼지 정보 조회
    #             air_quality = get_nearest_station(random_place.rgnCdNm)
    #             pm10_value = air_quality.get('pm10', 999)  # 기본값 999로 설정하여 필터링 방지
                
    #             if pm10_value <= 30:  # 미세먼지 조건 만족하는 경우만 추가
    #                 place_data = random_place.to_dict()
    #                 place_data['pm10'] = pm10_value
    #                 place_data['pm25'] = air_quality.get('pm25')
                    
    #                 # 썸네일 추가
    #                 image_url = get_naver_image_thumbnail(random_place.pfctNm)
    #                 place_data['thumbnail'] = image_url if image_url else '/images/noImage.jpg'
                    
    #                 low_pm_places.append(place_data)

    #         # (2) 나머지 5개는 기존 방식대로 랜덤하게 가져오되, 중복 방지
    #         remaining_count = count - len(low_pm_places)  # 남은 개수 (최대 5개)
    #         random_places = []
            
    #         if remaining_count > 0:
    #             random_places = db.session.query(PlayAreas).filter(
    #                 ~PlayAreas.id.in_([place['id'] for place in low_pm_places])  # 중복 방지
    #             ).order_by(db.func.random()).limit(remaining_count).all()

    #         # (3) 랜덤 장소에 대해서도 썸네일 및 미세먼지 정보 추가
    #         places_data = low_pm_places  # 미세먼지 30 이하 장소 먼저 추가

    #         for place in random_places:
    #             image_url = get_naver_image_thumbnail(place.pfctNm)
    #             place_data = place.to_dict()
    #             place_data['thumbnail'] = image_url if image_url else '/images/noImage.jpg'

    #             air_quality = get_nearest_station(place.rgnCdNm)
    #             place_data['pm10'] = air_quality.get('pm10')
    #             place_data['pm25'] = air_quality.get('pm25')

    #             places_data.append(place_data)

    #         return jsonify(places_data), 200

    #     except Exception as e:
    #         return jsonify({"error": str(e)}), 500



# 기존 place_cards
    # @app.route('/api/place-cards', methods=['GET'])
    # def placeCards():
    #     try:
    #         count = int(request.args.get('count', 10))  # 기본 10개 가져오기
    #         max_id = db.session.query(db.func.max(PlayAreas.id)).scalar()
    #         random_places = db.session.query(PlayAreas).filter(
    #             PlayAreas.id >= db.func.floor(db.func.random() * max_id)
    #         ).limit(count).all()

    #         places_data = []
    #         # 레코드가 존재하면 해당 레코드를 JSON 형태로 반환
    #         for place in random_places:
    #             image_url = get_naver_image_thumbnail(place.pfctNm)
    #             place_data = place.to_dict()
    #             place_data['thumbnail'] = image_url if image_url else '/images/noImage.jpg'

    #             air_quality = get_nearest_station(place.rgnCdNm)
    #             print("🟢 [API 응답] ",air_quality)
    #             place_data['pm10'] = air_quality.get('pm10')  # pm10 값
    #             place_data['pm25'] = air_quality.get('pm25')

    #             places_data.append(place_data)

    #         return jsonify(places_data), 200

    #     except Exception as e:
    #         return jsonify({"error": str(e)}), 500