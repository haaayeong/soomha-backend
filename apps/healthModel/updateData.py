import pandas as pd
import json
import re

# ==================== 환자 데이터 전처리 ====================
# JSON 파일에서 매핑 정보 불러오기
with open("data/region_mapping.json", "r", encoding="utf-8") as f:
    region_mapping = json.load(f)



# 파일 경로 (CSV로 변경)
file_paths = {
    "asthma": "data/medical_asthma.csv",
    "atopy": "data/medical_atopy.csv",
    "rhinitis": "data/medical_rhinitis.csv"
}

# '연령군' 필터링 및 날짜, 연령군 전처리 함수 (새 컬럼 추가 포함)
def filter_by_date(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8')  # UTF-8 인코딩으로 CSV 파일 읽기
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')  # ISO-8859-1 인코딩으로 다시 시도

    # 열 이름에서 공백 제거
    df.columns = df.columns.str.strip()

    # '요양개시연월' -> 'YYYYMM' 형식으로 변환
    df["요양개시연월"] = pd.to_datetime(df["요양개시연월"], format="%Y-%m")
    df = df[df["요양개시연월"] >= "2010-01-01"]
    df["요양개시연월"] = df["요양개시연월"].dt.strftime("%Y%m")

    # '연령군'에서 1, 2, 3으로 시작하는 값만 필터링하고 숫자만 추출
    df = df[df["연령군"].astype(str).str.startswith(("1.", "2.", "3."))]
    df["연령군"] = df["연령군"].str.extract(r'(\d)')  # 예: "1. 0-5세" -> "1"

    # 새 컬럼 "광역시/도" 추가: "주소(시군구)" 코드에 따라 JSON 매핑 정보로 변환
    df["광역시/도"] = df["주소(시군구)"].astype(str).map(region_mapping)

    return df

# 모든 환자 데이터 전처리
filtered_data = {key: filter_by_date(path) for key, path in file_paths.items()}

# 환자 데이터 (asthma) 상위 10개 행 출력
print("\n=== asthma 데이터 (전처리 후) ===")
print(filtered_data["asthma"].head(10))


# ==================== 미세먼지 데이터 전처리 ====================
# 미세먼지 데이터 파일 불러오기
dust_df = pd.read_csv("data/month_dust.csv", encoding="utf-8")


# 열 이름 변환 함수: "2010년 1월" → "201001"
def convert_month_col(col_name):
    m = re.match(r'(\d+)년\s*(\d+)월', col_name)
    if m:
        year = m.group(1)
        month = int(m.group(2))
        return f"{year}{month:02d}"
    return col_name

# 모든 열 이름에 대해 변환 적용
new_columns = {col: convert_month_col(col) for col in dust_df.columns}
dust_df.rename(columns=new_columns, inplace=True)

# 불필요한 'No' 열 제거 (존재하는 경우)
if "No" in dust_df.columns:
    dust_df.drop(columns=["No"], inplace=True)

# '분류' 열을 '광역시/도'로 이름 변경 (환자 데이터와 매칭하기 위함)
if "분류" in dust_df.columns:
    dust_df.rename(columns={"분류": "광역시/도"}, inplace=True)



# 미세먼지 데이터 변환 (Wide → Long)
dust_df_long = dust_df.melt(id_vars=["광역시/도"], var_name="요양개시연월", value_name="미세먼지")

# ==================== 미세먼지 결측값 처리 ====================
# '미세먼지' 열을 문자열로 변환한 후, 별(*) 제거
dust_df_long["미세먼지"] = dust_df_long["미세먼지"].astype(str).str.replace('*', '', regex=False)

# '미세먼지' 열을 숫자로 변환 (변환할 수 없는 값은 NaN 처리)
dust_df_long["미세먼지"] = pd.to_numeric(dust_df_long["미세먼지"], errors='coerce')

# 월별 평균 계산
avg_dust_by_month = dust_df_long.groupby("요양개시연월")["미세먼지"].transform("mean")

# 1. 월별 평균으로 결측치 채우기
dust_df_long["미세먼지"] = dust_df_long["미세먼지"].fillna(avg_dust_by_month)

# 2. 여전히 결측치가 남아있는 경우 전체 평균으로 채우기
dust_df_long["미세먼지"] = dust_df_long["미세먼지"].fillna(dust_df_long["미세먼지"].mean())

# 결측치가 제대로 채워졌는지 확인
print("\n=== 미세먼지 데이터 (결측값 처리 후) ===")
print(dust_df_long.head())


# ==================== 환자 데이터 그룹화 ====================
for key in filtered_data:
    df = filtered_data[key]
    
    # 그룹화: 요양개시연월, 광역시/도, 연령군, 성별 기준으로 합산
    grouped_df = df.groupby(["요양개시연월", "광역시/도", "연령군", "성별"], as_index=False)["진료에피소드 건수"].sum()
    
    # 변환된 데이터 저장
    filtered_data[key] = grouped_df

# 결과 확인 (asthma 데이터)
print("\n=== asthma 데이터 (그룹화 후) ===")
print(filtered_data["asthma"].head(10))

# ==================== 미세먼지 데이터와 병합 ====================
merged_data = {}

for key in filtered_data:
    df = filtered_data[key]
    
    # 병합: 요양개시연월 + 광역시/도를 기준으로 미세먼지 데이터와 결합
    merged_df = df.merge(dust_df_long, on=["요양개시연월", "광역시/도"], how="left")
    
    # 변환된 데이터 저장
    merged_data[key] = merged_df

# 결과 확인 (asthma 데이터)
print("\n=== asthma 데이터 (미세먼지 병합 후) ===")
print(merged_data["asthma"].head(20))




# 전처리된 데이터를 CSV 파일로 저장 (UTF-8-SIG 인코딩)
for key in merged_data:
    output_path = f"data/{key}_processed.csv"
    merged_data[key].to_csv(output_path, index=False, encoding='utf-8-sig')  # UTF-8-SIG로 저장

    print(f"'{key}_processed.csv' 파일이 저장되었습니다.")
