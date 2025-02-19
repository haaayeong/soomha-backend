
import requests

def is_valid_image(url):
    """이미지 URL이 유효한지 확인하는 함수"""
    try:
        # URL의 확장자 추출
        ext = url.split('.')[-1].lower()
        
        # 이미지 확장자 목록
        valid_image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']
        
        if ext not in valid_image_extensions:
            return False
        
        # HEAD 요청으로 빠르게 확인
        response = requests.head(url, timeout=3)
        
        # 서버 응답이 이미지일 경우 status_code가 200이고, Content-Type이 이미지 관련이어야 함
        content_type = response.headers.get('Content-Type', '')
        if response.status_code == 200 and 'image' in content_type:
            return True
        return False
        
    except requests.RequestException:
        return False

def get_naver_image_thumbnail(query, count=1):
    """네이버 이미지 검색 API를 호출하여 유효한 썸네일 이미지를 가져오는 함수"""
    url = "https://openapi.naver.com/v1/search/image"
    headers = {
        "X-Naver-Client-Id": "5JTLhCRqU_J3sSamRZHP",
        "X-Naver-Client-Secret": "i9WNPpNAfL"
    }
    
    params = {
        'query': query,  
        'display': 10,  # 여러 개 가져와서 깨지지 않은 것 선택
        'start': 1,     
        'sort': 'sim'   
    }
    
    valid_images = []  # 유효한 이미지 저장 리스트
    max_images = min(count, 7)  # 최대 7장까지만 반환


    try:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if data.get('items'):
                for item in data['items']:  
                    image_url = item['link']
                    if is_valid_image(image_url):
                        valid_images.append(image_url)
                    if len(valid_images) >= max_images:
                        break  # 원하는 개수만큼 이미지를 얻으면 중단
        return valid_images if count > 1 else (valid_images[0] if valid_images else None)
     
    except Exception as e:
        print(f"네이버 이미지 API 오류: {e}")
        return None  
