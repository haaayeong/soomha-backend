import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import StandardScaler
import joblib

# 데이터 로드 (비염, 천식, 아토피 데이터)
datasets = {
    "rhinitis": pd.read_csv("data/rhinitis_processed.csv", encoding="utf-8-sig"),
    "asthma": pd.read_csv("data/asthma_processed.csv", encoding="utf-8-sig"),
    "atopy": pd.read_csv("data/atopy_processed.csv", encoding="utf-8-sig")
}

# 전처리 함수
def preprocess_data(data):
    data['성별'] = data['성별'].map({'남자': 0, '여자': 1})
    data['광역시/도'] = data['광역시/도'].map({
        '경기도': 0, '경상남도': 1, '경상북도': 2, '광주광역시': 3, '대구광역시': 4,
        '대전광역시': 5, '부산광역시': 6, '서울특별시': 7, '세종특별자치시': 8, '울산광역시': 9,
        '인천광역시': 10, '전라남도': 11, '전라북도': 12, '제주특별자치도': 13, '충청남도': 14, '충청북도': 15
    })
    data['연령군'] = data['연령군'].map({1: 0, 2: 1, 3: 2})
    data['연도'] = data['요양개시연월'].astype(str).str[:4].astype(int)
    data['월'] = data['요양개시연월'].astype(str).str[4:6].astype(int)
    data = data.drop(['요양개시연월'], axis=1)
    return data

# 데이터 전처리 및 분리
for key in datasets:
    datasets[key] = preprocess_data(datasets[key])

def split_features_target(data):
    X = data.drop(columns=['진료에피소드 건수'])
    y = data['진료에피소드 건수']
    return X, y

data_splits = {key: split_features_target(datasets[key]) for key in datasets}

def scale_data(X, y):
    scaler_X = StandardScaler()
    X_scaled = scaler_X.fit_transform(X)
    
    scaler_y = StandardScaler()
    y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1))
    
    return X_scaled, y_scaled, scaler_X, scaler_y

scaled_data = {key: scale_data(*data_splits[key]) for key in datasets}

def create_model(input_dim):
    model = Sequential([
        Dense(256, input_dim=input_dim, activation='relu'),
        Dropout(0.2),
        Dense(128, activation='relu'),
        Dropout(0.2),
        Dense(64, activation='relu'),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(16, activation='relu'),
        Dense(1, activation='linear')
    ])
    model.compile(loss='mean_squared_error', optimizer=Adam(learning_rate=0.0005), metrics=['mae'])
    return model

def train_and_save_model(X, y, name):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = create_model(X_train.shape[1])
    early_stopping = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
    model.fit(X_train, y_train, epochs=300, batch_size=32,
              validation_data=(X_test, y_test), callbacks=[early_stopping])
    model.save(f"models/{name}_model.h5")
    joblib.dump((scaler_X, scaler_y), f"models/{name}_scalers.pkl")
    print(f"{name} 모델 저장 완료")

# 모델 학습 및 저장
for key in scaled_data:
    X_scaled, y_scaled, scaler_X, scaler_y = scaled_data[key]
    train_and_save_model(X_scaled, y_scaled, key)
