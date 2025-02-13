import requests
from flask import jsonify

def get_nearest_station():
    API_KEY = "5CQeftawhDwl1cz9L0RxxMn8mjHETjXzCuHxHgteyt%2FvAK1i50baokozMpWbrG%2FEb2yMXkwSwn18uBEylgUk0g%3D%3D"

    # 1️⃣ TM 좌표 변환 API 호출 (예제: 혜화동)
    tm_url = f"http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getTMStdrCrdnt?umdName=혜화동&returnType=json&serviceKey={API_KEY}"
    print(f"📡 TM 좌표 변환 API 요청: {tm_url}")

    tm_response = requests.get(tm_url)
    print(f"🔹 TM 좌표 응답: {tm_response.text}")  # 응답 출력

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
    return station_data["response"]["body"]["items"]
