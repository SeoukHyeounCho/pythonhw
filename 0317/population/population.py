#!sudo apt-get install -y fonts-nanum
#!sudo fc-cache -fv
#!rm ~/.cache/matplotlib -rf
#import matplotlib.pyplot as plt
#plt.rc('font', family='NanumBarunGothic')
#plt.rcParams['axes.unicode_minus'] =False



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rc('font', family='NanumBarunGothic')

# 두 번째 헤더 행 건너뛰기: 첫 번째 행은 날짜 헤더, 이후부터 실제 데이터가 시작됩니다.
df = pd.read_csv('행정구역_시군구_별__성별_인구수_20250320170318.csv', 
                 encoding='cp949', skiprows=[1])
# df의 첫 번째 열은 지역명, 나머지 열은 각 월의 인구수
print(df.head())
print("DataFrame shape:", df.shape)

# 열 이름 목록 생성 (필요하다면 특정 열 제거 가능)
columns = list(df.columns)
# 예전 코드에서 del columns[1]을 사용한 것은 두 번째 헤더 행에 해당하는 불필요한 열을 제거하기 위함이었는데,
# skiprows 옵션을 사용하면 이제 필요하지 않습니다.

# 인구 증감 차이(popDiff) 계산: 각 지역의 첫 번째 열(지역명)은 유지하고,
# 두 번째 열부터는 이전 달과의 차이를 계산
popDiff = []
for i in range(len(df)):  # 이제 실제 데이터 행은 0부터 시작
    row = [df.iloc[i, 0]]  # 지역명
    for j in range(2, len(df.columns)):  # 두 번째 열(인덱스 1)은 시작점으로 사용
        diff = int(df.iloc[i, j]) - int(df.iloc[i, j - 1])
        row.append(diff)
    popDiff.append(row)

# 계산된 데이터 DataFrame으로 저장 및 CSV 내보내기
dfPopDiff = pd.DataFrame(popDiff, columns=[columns[0]] + columns[2:])
dfPopDiff.to_csv('populationDiff.csv', encoding='cp949', index=False)

# 인구 증가율(popIncreaseRate) 계산
popIncreaseRate = []
for i in range(len(df)):
    row = [df.iloc[i, 0]]
    for j in range(2, len(df.columns)):
        prev = int(df.iloc[i, j - 1])
        # 0으로 나누는 경우 방지
        if prev == 0:
            rate = 0.0
        else:
            rate = float((int(df.iloc[i, j]) - prev) / prev) * 100.0
        row.append(rate)
    popIncreaseRate.append(row)

dfPopIncreaseRate = pd.DataFrame(popIncreaseRate, columns=[columns[0]] + columns[2:])
dfPopIncreaseRate.to_csv('populationIncreaseRate.csv', encoding='cp949', index=False)

# popDiff를 이용해 각 지역의 특정 구간(예: 인덱스 108~113)의 인구 증감 데이터를 추출하려면,
# 우선 DataFrame의 각 행 길이를 확인합니다.
# 예를 들어, 각 행의 길이가 132이면, popDiff[0]은 "용인시", popDiff[1]은 "화성시"에 해당합니다.
print("각 행의 길이:", [len(row) for row in popDiff])

# x축에 표시할 값 (예: 202201 ~ 202206)
x_values = []
for i in range(1, 7):
    yyyymm = '20220' + str(i)
    x_values.append(yyyymm)

# 지역별 인구 증감 데이터 추출 (여기서는 예시로 인덱스 108~114 구간을 사용)
# 데이터의 열 수가 충분한지 확인 후 슬라이싱
y_region1 = popDiff[0][108:114]
y_region2 = popDiff[1][108:114]
# 간단한 막대그래프 예제 (두 지역만 표시)
plt.figure(figsize=(10, 6))
x = np.arange(len(x_values))
bar_width = 0.35

plt.bar(x, y_region1, bar_width, label=popDiff[0][0])
plt.bar(x + bar_width, y_region2, bar_width, label=popDiff[1][0])

plt.xlabel('월')
plt.ylabel('인구 증감수')
plt.xticks(x + bar_width / 2, x_values)
plt.legend()
plt.show()
