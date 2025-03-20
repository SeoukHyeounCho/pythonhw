import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# CSV 파일 읽어오기: 두 번째 헤더 행 건너뛰기
df = pd.read_csv('행정구역_시군구_별__성별_인구수_20250320172339.csv', 
                 encoding='cp949', skiprows=[1])
columns = list(df.columns)
# 첫 번째 컬럼은 지역명, 나머지 컬럼은 날짜 정보

# 인구수 증감 계산 (popDiff)
popDiff = []
for i in range(len(df)):
    # 위치 기반 인덱싱 사용: iloc[i, 0]는 지역명
    row = [df.iloc[i, 0]]
    for j in range(2, len(columns)):
        try:
            pop = int(df.iloc[i, j]) - int(df.iloc[i, j - 1])
        except Exception as e:
            pop = 0
        row.append(pop)
    popDiff.append(row)
# 새 DataFrame: 첫 번째 열은 지역명, 이후는 인구 증감 데이터 (날짜는 원래 2번째 컬럼부터)
new_columns = [columns[0]] + columns[2:]
dfPopDiff = pd.DataFrame(popDiff, columns=new_columns)
dfPopDiff.to_csv('populationDiff.csv', encoding='cp949', index=False)

# 인구 증가율 계산 (popIncreaseRate)
popIncreaseRate = []
for i in range(len(df)):
    row = [df.iloc[i, 0]]
    for j in range(2, len(columns)):
        try:
            prev = int(df.iloc[i, j - 1])
            curr = int(df.iloc[i, j])
            rate = (curr - prev) / prev * 100.0 if prev != 0 else 0.0
        except Exception as e:
            rate = 0.0
        row.append(rate)
    popIncreaseRate.append(row)
dfPopIncreaseRate = pd.DataFrame(popIncreaseRate, columns=new_columns)
dfPopIncreaseRate.to_csv('populationIncreaseRate.csv', encoding='cp949', index=False)

# CSV 파일에서 인구수 증감 데이터 다시 읽어오기
df_diff = pd.read_csv('populationDiff.csv', encoding='cp949')
popDiff = []
for i in range(len(df_diff)):
    popDiff.append(list(df_diff.iloc[i]))

# x축에 표시할 값 생성 (예: 202201 ~ 202206)
x_values = []
for i in range(1, 7):
    yyyymm = '20220' + str(i)
    x_values.append(yyyymm)

# 각 지역별 월별 인구 증감 수치 추출 (예시로 인덱스 108~113 사용)
def get_slice(row, start=108, end=114):
    try:
        return row[start:end]
    except IndexError:
        return []


y_seoul = popDiff[0][108:114]
y_bs    = popDiff[1][108:114]
y_dg    = popDiff[2][108:114]
y_ic    = popDiff[3][108:114]
y_gj    = popDiff[4][108:114]
y_dj    = popDiff[5][108:114]
y_us    = popDiff[6][108:114]
y_sj    = popDiff[7][108:114]
y_gg    = popDiff[8][108:114]
y_gw    = popDiff[9][108:114]
y_cb    = popDiff[10][108:114]
y_cn    = popDiff[11][108:114]
y_jb    = popDiff[12][108:114]
y_jn    = popDiff[13][108:114]
y_gb    = popDiff[14][108:114]
y_gn    = popDiff[15][108:114]
y_jj    = popDiff[16][108:114]

# 그래프 그리기
plt.figure(figsize=(12, 8))
ax = plt.subplot()
bar_width = 0.05
x = np.arange(len(x_values))
ax.set_xticks(x)
ax.set_xticklabels(x_values)

p1  = plt.bar(x,                  y_seoul, bar_width)
p2  = plt.bar(x + bar_width,      y_bs,    bar_width)
p3  = plt.bar(x + bar_width*2,    y_dg,    bar_width)
p4  = plt.bar(x + bar_width*3,    y_ic,    bar_width)
p5  = plt.bar(x + bar_width*4,    y_gj,    bar_width)
p6  = plt.bar(x + bar_width*5,    y_dj,    bar_width)
p7  = plt.bar(x + bar_width*6,    y_us,    bar_width)
p8  = plt.bar(x + bar_width*7,    y_sj,    bar_width)
p9  = plt.bar(x + bar_width*8,    y_gg,    bar_width)
p10 = plt.bar(x + bar_width*9,    y_gw,    bar_width)
p11 = plt.bar(x + bar_width*10,   y_cb,    bar_width)
p12 = plt.bar(x + bar_width*11,   y_cn,    bar_width)
p13 = plt.bar(x + bar_width*12,   y_jb,    bar_width)
p14 = plt.bar(x + bar_width*13,   y_jn,    bar_width)
p15 = plt.bar(x + bar_width*14,   y_gb,    bar_width)
p16 = plt.bar(x + bar_width*15,   y_gn,    bar_width)
p17 = plt.bar(x + bar_width*16,   y_jj,    bar_width)

plt.legend(['Seoul', 'Busan', 'Daegu', 'Incheon', 'Gwangju', 'Daejeon', 'Ulsan',
            'Sejong', 'Gyeonggi', 'Gangwon', 'Chungbuk', 'Chungnam', 'Jeonbuk',
            'Jeonnam', 'Gyeongbuk', 'Gyeongnam', 'Jeju'], loc=(1.0, 0))
plt.show()
