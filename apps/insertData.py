import http.client
import ssl
import json
import time

# 한 번에 처리할 데이터 개수 (배치 크기)
BATCH_SIZE = 1000
BASE_ENDPOINT = "/1741000/pfc2/pfc/getPfctInfo2?serviceKey=5CQeftawhDwl1cz9L0RxxMn8mjHETjXzCuHxHgteyt%2FvAK1i50baokozMpWbrG%2FEb2yMXkwSwn18uBEylgUk0g%3D%3D&pageIndex={page_index}&recordCountPerPage={record_count}"

def insert_data_to_db():
    url = "apis.data.go.kr"
    page_index = 1  # 페이지 인덱스 초기화
    total_pages = 86  # 예상 페이지 수 (85804 / 1000)
    all_data = []  # 모든 데이터를 저장할 리스트

    try:
        context = ssl.create_default_context()
        context.set_ciphers('ALL:@SECLEVEL=1')

        while page_index <= total_pages:
            endpoint = BASE_ENDPOINT.format(page_index=page_index, record_count=BATCH_SIZE)
            retry_count = 0
            success = False

            while retry_count < 3 and not success:
                try:
                    conn = http.client.HTTPSConnection(url, context=context)
                    conn.request("GET", endpoint)
                    response = conn.getresponse()
                    
                    if response.status == 200:
                        data = response.read().decode("utf-8")
                        data_json = json.loads(data)
                        
# 응답에서 'body'와 'items'가 없다면 더 이상 데이터를 요청할 필요 없다고 판단
                        if data_json and 'response' in data_json and 'body' in data_json['response']:
                            body = data_json['response']['body']
                            items = body.get('items', [])
                            if items:
                                all_data.extend(items)
                                success = True
                            else:
                                print("더 이상 데이터가 없습니다. DB 저장 완료!")
                                return "모든 데이터 저장 완료"
                        else:
                            print("데이터 형식 오류: 응답에서 items를 찾을 수 없습니다. DB 저장 완료!")
                            return "모든 데이터 저장 완료"
                    elif response.status == 429:
                        print(f"Too many requests. Retrying in 10 seconds...")
                        time.sleep(10)  # 429 방지 대기 시간을 늘림
                        retry_count += 1
                    else:
                        print(f"Error: {response.status}. Retrying...")
                        time.sleep(5)
                        retry_count += 1
                except Exception as e:
                    print(f"API 호출 중 오류 발생: {e}")
                    break  # 오류가 발생하면 종료

            if not success:
                break  # 3회 재시도 실패 시 종료

            # 진행률 출력 (1000/85804 형식)
            print(f"{min(page_index * BATCH_SIZE, 85804)}/85804 데이터 받아오는 중...")

            # 일정량 이상의 데이터가 모이면 DB에 저장
            if len(all_data) >= BATCH_SIZE:
                save_to_db(all_data)
                all_data.clear()
            
            page_index += 1
            time.sleep(1)  # API 요청 간격 유지
        
        # 마지막에 남아있는 데이터 저장
        if all_data:
            save_to_db(all_data)
        
        print("모든 데이터 저장 완료")
        return "모든 데이터 저장 완료"
    
    except Exception as e:
        print(f"API 호출 중 오류 발생: {str(e)}")

def save_to_db(data):
    from apps.app import db  # 동적 임포트
    from apps.models import PlayAreas
    batch = []
    
    # 한번에 여러 개의 pfctSn을 조회해서 성능을 개선
    pfct_sns = [record.get("pfctSn") for record in data]
    existing_records = PlayAreas.query.filter(PlayAreas.pfctSn.in_(pfct_sns)).all()
    existing_records_dict = {record.pfctSn: record for record in existing_records}
    
    for record in data:
        pfctSn = record.get("pfctSn")
        existing_record = existing_records_dict.get(pfctSn)

        if existing_record:
            existing_record.pfctNm = record.get("pfctNm", "")
            existing_record.instlPlaceCdNm = record.get("instlPlaceCdNm", "")
            existing_record.operYnCd = record.get("operYnCd", "")
            existing_record.operYnCdNm = record.get("operYnCdNm", "")
            existing_record.dutyCd = record.get("dutyCd", "")
            existing_record.dutyCdNm = record.get("dutyCdNm", "")
            existing_record.prvtPblcYnCd = record.get("prvtPblcYnCd", "")
            existing_record.prvtPblcYnCdNm = record.get("prvtPblcYnCdNm", "")
            existing_record.ronaAddr = record.get("ronaAddr", "")
            existing_record.ronaDaddr = record.get("ronaDaddr", "")
            existing_record.instlYmd = record.get("instlYmd", "")
            existing_record.instlPlaceCd = record.get("instlPlaceCd", "")
            existing_record.idrodrCd = record.get("idrodrCd", "")
            existing_record.idrodrCdNm = record.get("idrodrCdNm", "")
            existing_record.rgnCd = record.get("rgnCd", "")
            existing_record.rgnCdNm = record.get("rgnCdNm", "")
            existing_record.latCrtsVl = record.get("latCrtsVl", "")
            existing_record.lotCrtsVl = record.get("lotCrtsVl", "")
        else:
            play_area = PlayAreas(
                pfctNm=record.get("pfctNm", ""),
                pfctSn=pfctSn,
                instlPlaceCdNm=record.get("instlPlaceCdNm", ""),
                operYnCd=record.get("operYnCd", ""),
                operYnCdNm=record.get("operYnCdNm", ""),
                dutyCd=record.get("dutyCd", ""),
                dutyCdNm=record.get("dutyCdNm", ""),
                prvtPblcYnCd=record.get("prvtPblcYnCd", ""),
                prvtPblcYnCdNm=record.get("prvtPblcYnCdNm", ""),
                ronaAddr=record.get("ronaAddr", ""),
                ronaDaddr=record.get("ronaDaddr", ""),
                instlYmd=record.get("instlYmd", ""),
                instlPlaceCd=record.get("instlPlaceCd", ""),
                idrodrCd=record.get("idrodrCd", ""),
                idrodrCdNm=record.get("idrodrCdNm", ""),
                rgnCd=record.get("rgnCd", ""),
                rgnCdNm=record.get("rgnCdNm", ""),
                latCrtsVl=record.get("latCrtsVl", ""),
                lotCrtsVl=record.get("lotCrtsVl", "")
            )
            batch.append(play_area)
        
        if len(batch) >= BATCH_SIZE:
            db.session.add_all(batch)
            db.session.commit()
            print(f"저장된 레코드: {len(batch)}개")
            batch.clear()
    
    if batch:
        db.session.add_all(batch)
        db.session.commit()
        print(f"저장된 레코드: {len(batch)}개")
    
    print("DB 저장 완료")
