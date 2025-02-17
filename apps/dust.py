import requests
from flask import jsonify
from datetime import datetime
import re

API_KEY = "5CQeftawhDwl1cz9L0RxxMn8mjHETjXzCuHxHgteyt%2FvAK1i50baokozMpWbrG%2FEb2yMXkwSwn18uBEylgUk0g%3D%3D"
def get_nearest_station(rgnCdNm):

    # 1️⃣ rgnCdNm에서 끝값 확인 및 처리
    if re.search(r"(읍|면|동)$", rgnCdNm):  # '읍', '면', '동'으로 끝나는 경우
        # 끝에 읍, 면, 동이 있으면 그 지역명만 사용
        umd_name = rgnCdNm.split()[-1]  # 끝에 있는 읍, 면, 동만 추출
    elif re.search(r"구$", rgnCdNm):  # '구'로 끝나는 경우
        # '구'로 끝나면, '구' 이전까지의 지역명을 사용
        umd_name = rgnCdNm.split()[-2]  # '구'가 끝나는 전 지역명만 사용
    else:
        # 예외 처리, 예상되는 값이 아닐 경우 전체 값 사용
        umd_name = rgnCdNm.split()[-2]  # '시' 또는 '구'만 추출

    # 2️⃣ TM 좌표 변환 API 요청
    print(f"📡 TM 이름 변경: {umd_name}")

    tm_url = f"http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getTMStdrCrdnt?umdName={umd_name}&returnType=json&serviceKey={API_KEY}"
    print(f"📡 TM 좌표 변환 API 요청: {tm_url}")

    # API 호출
    tm_response = requests.get(tm_url)
    print(f"🔹 TM 좌표 응답: {tm_response.text}")  # 응답 출력
    if tm_response.json()['response']['body']['totalCount'] == 0:
        umd_name = rgnCdNm.split()[-2]
        tm_url = f"http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getTMStdrCrdnt?umdName={umd_name}&returnType=json&serviceKey={API_KEY}"
        tm_response = requests.get(tm_url)
    try:
        tm_data = tm_response.json()

    except Exception as e:
        print(f"❌ TM 좌표 JSON 변환 오류: {e}")
        return {"error": "TM 좌표 응답이 올바른 JSON 형식이 아닙니다."}, 500

    if tm_data["response"]["header"]["resultCode"] != "00":
        print(f"❌ TM 좌표 변환 실패: {tm_data['response']['header']['resultMsg']}")
        return {"error": "TM 좌표 변환 실패"}, 500

    tm_x = tm_data["response"]["body"]["items"][0]["tmX"]
    tm_y = tm_data["response"]["body"]["items"][0]["tmY"]
    print(f"✅ 변환된 TM 좌표: tmX={tm_x}, tmY={tm_y}")

    # 2️⃣ 변환된 TM 좌표를 사용하여 근접 측정소 조회
    station_url = f"http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getNearbyMsrstnList?tmX={tm_x}&tmY={tm_y}&returnType=json&serviceKey={API_KEY}"
    print(f"📡 근접 측정소 API 요청: {station_url}")

    station_response = requests.get(station_url)
    print(f"🔹 근접 측정소 응답: {station_response.text}")  # 응답 출력

    try:
        station_data = station_response.json()
    except Exception as e:
        print(f"❌ 근접 측정소 JSON 변환 오류: {e}")
        return {"error": "근접 측정소 응답이 올바른 JSON 형식이 아닙니다."}, 500

    if station_data["response"]["header"]["resultCode"] != "00":
        print(f"❌ 근접 측정소 조회 실패: {station_data['response']['header']['resultMsg']}")
        return {"error": "근접 측정소 조회 실패"}, 500

    print(f"✅ 조회된 근접 측정소: {station_data['response']['body']['items']}")
    air_quality = get_air_quality(station_data["response"]["body"]["items"][0]["stationName"])
    
    if 'error' in air_quality:
        print(f"❌ 첫 번째 측정소에서 에러 발생: {air_quality['error']}. 두 번째 측정소로 재시도.")
        air_quality = get_air_quality(station_data["response"]["body"]["items"][1]["stationName"])

    return air_quality


def get_air_quality(station_name):
    print(f"📡 미세먼지 정보를 가져올 측정소: {station_name}")
    

 # 1️⃣ API 요청 URL 구성
    air_quality_url = (
        f"http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
        f"?stationName={station_name}&returnType=json&numOfRows=3&pageNo=1&dataTerm=Daily"
        f"&serviceKey={API_KEY}&ver=1.3"
    )
    print(f"📡 실시간 미세먼지 API 요청: {air_quality_url}")

    # 3️⃣ API 요청 및 응답 확인
    response = requests.get(air_quality_url)

    try:
        data = response.json()
    except Exception as e:
        print(f"❌ JSON 변환 오류: {e}")
        return {"error": "응답이 올바른 JSON 형식이 아닙니다."}

    # 4️⃣ API 응답 오류 확인
    if data["response"]["header"]["resultCode"] != "00":
        print(f"❌ API 호출 실패: {data['response']['header']['resultMsg']}")
        return {"error": "미세먼지 데이터를 가져오는 데 실패했습니다."}

    # 5️⃣ 데이터 파싱
    items = data["response"]["body"]["items"]
    if not items:
        print("❌ 오늘 날짜의 미세먼지 데이터가 없습니다.")
        return {"error": "오늘 날짜의 미세먼지 데이터가 없습니다."}
    
    latest_data = items[0]

    # 6️⃣ 최종 반환 데이터 구성
    air_quality = {
        "pm10": latest_data["pm10Value"],  # 미세먼지 (PM10)
        "pm25": latest_data["pm25Value"],  # 초미세먼지 (PM2.5)
    }


    return air_quality