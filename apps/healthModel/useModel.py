import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import joblib
import os

# 저장된 모델 및 스케일러 로드 함수
def load_models_and_scalers():
    diseases = ["rhinitis", "asthma", "atopy"]
    path = os.path.join(os.path.dirname(__file__), 'models', 'asthma_model.h5')
    models = {disease: load_model(os.path.join(os.path.dirname(__file__), 'models', f'{disease}_model.h5' )) for disease in diseases}
    scalers = {disease: joblib.load(os.path.join(os.path.dirname(__file__), 'models', f"{disease}_scalers.pkl" )) for disease in diseases}
    return models, scalers

# 예측 함수
def predict_health_warning(gender, region, age_group, year, month, pm25):
    print('함수요청까지 성공함',year)
    models, scalers = load_models_and_scalers()

    # 예측할 데이터 입력
    sample_data = pd.DataFrame({
        '성별': [gender],         
        '광역시/도': [region],   
        '연령군': [age_group],     
        '연도': [year],    
        '월': [month],         
        '미세먼지': [pm25]   
    })



    # 학습 데이터와 동일한 피처 순서 유지
    feature_order = ['광역시/도','연령군','성별','미세먼지','연도', '월', ]
    sample_data = sample_data[feature_order]

    # 각 질환별 예측 수행
    predictions = {}
    for disease in models.keys():
        scaler_X, scaler_y = scalers[disease]  # 튜플 언패킹

        # 예측 시 사용될 데이터가 정확한 순서로 정렬되어 있는지 확인
        sample_data = sample_data[feature_order]
        
        # 특성 데이터를 스케일링
        sample_scaled = scaler_X.transform(sample_data)

        # 예측 수행
        pred_scaled = models[disease].predict(sample_scaled)

        # 결과 역변환
        pred = scaler_y.inverse_transform(pred_scaled)
        predictions[disease] = pred[0][0]
    return predictions
