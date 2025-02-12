from apps.app import db

class PlayAreas(db.Model):
    __tablename__ = 'play_areas'  # 테이블 이름 정의
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 기본 키
    pfctNm = db.Column(db.String(255), nullable=False)  # 시설 이름
    pfctSn = db.Column(db.String(50), nullable=False)  # 시설 고유 번호
    instlPlaceCdNm = db.Column(db.String(255), nullable=True)  # 설치 장소 코드 이름
    operYnCd = db.Column(db.String(50), nullable=True)  # 운영 여부 코드
    operYnCdNm = db.Column(db.String(255), nullable=True)  # 운영 여부 코드 이름
    dutyCd = db.Column(db.String(50), nullable=True)  # 의무 코드
    dutyCdNm = db.Column(db.String(255), nullable=True)  # 의무 코드 이름
    prvtPblcYnCd = db.Column(db.String(50), nullable=True)  # 공공/민간 여부 코드
    prvtPblcYnCdNm = db.Column(db.String(255), nullable=True)  # 공공/민간 여부 코드 이름
    ronaAddr = db.Column(db.String(255), nullable=True)  # 도로명 주소
    ronaDaddr = db.Column(db.String(255), nullable=True)  # 도로명 상세 주소
    instlYmd = db.Column(db.String(50), nullable=True)  # 설치일
    instlPlaceCd = db.Column(db.String(50), nullable=True)  # 설치 장소 코드
    idrodrCd = db.Column(db.String(50), nullable=True)  # 실내/실외 여부 코드
    idrodrCdNm = db.Column(db.String(255), nullable=True)  # 실내/실외 여부 코드 이름
    rgnCd = db.Column(db.String(50), nullable=True)  # 지역 코드
    rgnCdNm = db.Column(db.String(255), nullable=True)  # 지역 이름
    latCrtsVl = db.Column(db.String(50), nullable=True)  # 위도
    lotCrtsVl = db.Column(db.String(50), nullable=True)  # 경도
    