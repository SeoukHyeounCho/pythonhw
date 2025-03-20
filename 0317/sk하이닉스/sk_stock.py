import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout

# TSLA 주가 데이터 다운로드
tsla = yf.download('000660.KS', start='2023-03-19', end='2025-03-19')
df_tsla = pd.DataFrame(tsla['Close'])
df_tsla = df_tsla.reset_index()
df_tsla.columns = ['date', 'value']
df_tsla['date'] = pd.to_datetime(df_tsla['date'])
df_tsla.set_index('date', inplace=True)

#print(df_tsla.head())

df_tsla.reset_index( )
dataset_tsla = df_tsla.values
    #데이터 분할하기
df_tsla_train = dataset_tsla[:int(0.8*len(dataset_tsla)), :]
df_tsla_test = dataset_tsla[int(0.8*len(dataset_tsla)):, :]
#데이터 스케일링하기
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(0,1))
scaled_data=scaler.fit_transform(dataset_tsla)

df_tsla.reset_index( )
dataset_tsla = df_tsla.values
    #데이터 분할하기
df_tsla_train = dataset_tsla[:int(0.8*len(dataset_tsla)), :]
df_tsla_test = dataset_tsla[int(0.8*len(dataset_tsla)):, :]
#데이터 스케일링하기
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(0,1))
scaled_data=scaler.fit_transform(dataset_tsla)

x_train_data,y_train_data=[ ],[ ]
#28일을 기준으로 데이터 생성하기
for i in range(28,len(df_tsla_train)):
    x_train_data.append(scaled_data[i-28:i,0])
    y_train_data.append(scaled_data[i,0])
x_train_data, y_train_data = np.array(x_train_data), np.array(y_train_data)
x_train_data = np.reshape(x_train_data, (x_train_data.shape[0], x_train_data.shape[1],1))

lstm_tsla = Sequential( )
lstm_tsla.add(LSTM(units=28, return_sequences=True,input_shape=(x_train_data.shape[1],1)))
lstm_tsla.add(LSTM(units=28))
lstm_tsla.add(Dense(1))

#데이터 재가공하기
inputs_data = df_tsla[len(df_tsla) - len(df_tsla_test)-28:].values
inputs_data = inputs_data.reshape(-1,1)
inputs_data = scaler.transform(inputs_data)

#모형의 학습 방법 설정하여 학습 진행하기
lstm_tsla.compile(loss='mean_squared_error', optimizer='adam')
lstm_tsla.fit(x_train_data, y_train_data, epochs=100, batch_size=1, verbose=2)


X_test = [ ]
for i in range(28, inputs_data.shape[0]):
    X_test.append(inputs_data[i-28:i,0])
X_test = np.array(X_test)

X_test = np.reshape(X_test,(X_test.shape[0],X_test.shape[1],1))
predicted_value = lstm_tsla.predict(X_test)
predicted_value = scaler.inverse_transform(predicted_value)

# 예측값 배열의 길이 확인
print("예측값 길이:", len(predicted_value))
print("테스트 데이터 길이:", len(df_tsla_test_vis))

# 테스트 데이터의 길이를 예측값의 길이에 맞추어 슬라이싱
df_tsla_test_vis_subset = df_tsla_test_vis.iloc[:len(predicted_value)].copy()
df_tsla_test_vis_subset['Predictions'] = predicted_value

# 그래프 그리기
plt.plot(df_tsla_train_vis["Close"], label="train")
plt.plot(df_tsla_test_vis_subset["Close"], label="test")
plt.plot(df_tsla_test_vis_subset["Predictions"], label="Prediction")
plt.legend()
plt.show()
