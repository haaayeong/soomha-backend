
import requests

def is_valid_image(url):
    """이미지 URL이 유효한지 확인하는 함수"""
    try:
        response = requests.head(url, timeout=3)  # HEAD 요청으로 빠르게 확인
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_naver_image_thumbnail(query):
    """네이버 이미지 검색 API를 호출하여 유효한 썸네일 이미지를 가져오는 함수"""
    url = "https://openapi.naver.com/v1/search/image"
    headers = {
        "X-Naver-Client-Id": "5JTLhCRqU_J3sSamRZHP",
        "X-Naver-Client-Secret": "i9WNPpNAfL"
    }
    
    params = {
        'query': query,  
        'display': 5,  # 여러 개 가져와서 깨지지 않은 것 선택
        'start': 1,     
        'sort': 'sim'   
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                for item in data['items']:  
                    image_url = item['link']
                    if is_valid_image(image_url):  
                        return image_url  # 정상적인 이미지 반환
        return None  
    except Exception as e:
        print(f"네이버 이미지 API 오류: {e}")
        return None  
