
import requests

def get_naver_image_thumbnail(query):
    url = "https://openapi.naver.com/v1/search/image"  # 네이버 이미지 검색 API URL
    headers = {
        "X-Naver-Client-Id": "5JTLhCRqU_J3sSamRZHP",  # 네이버에서 발급받은 클라이언트 ID
        "X-Naver-Client-Secret": "i9WNPpNAfL"  # 네이버에서 발급받은 클라이언트 Secret
    }
    
    params = {
        'query': query,  # 검색할 장소 이름
        'display': 1,     # 결과 수 (썸네일 1개만 가져옴)
        'start': 1        # 시작 위치
    }
    
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get('items'):
            # 검색된 이미지 중 첫 번째 이미지를 썸네일로 사용
            return data['items'][0]['link']  # 이미지 URL 반환
        else:
            return None  # 이미지가 없을 경우
    else:
        return None  # API 호출 실패 시
