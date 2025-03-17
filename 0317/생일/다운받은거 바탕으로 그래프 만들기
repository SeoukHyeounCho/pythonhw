import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일 읽기: 상단의 불필요한 텍스트(검색조건 등)를 건너뛰기 위해 skiprows 사용
df = pd.read_csv('birthday.csv', encoding='cp949', skiprows=7)
df.info()
print(df.head())

# 결측치는 전방 채움으로 처리
df2 = df.ffill()

# 열 이름 변경: '평균기온(℃)', '최저기온(℃)', '최고기온(℃)'를 각각 'avg_temp', 'min_temp', 'max_temp'로 변경
df2.rename(columns={'최저기온(℃)': 'min_temp'}, inplace=True)
df2.rename(columns={'평균기온(℃)': 'avg_temp'}, inplace=True)
df2.rename(columns={'최고기온(℃)': 'max_temp'}, inplace=True)

# '날짜' 열의 좌우 공백 제거 및 datetime 형식으로 변환 (선택사항)
df2['날짜'] = pd.to_datetime(df2['날짜'].str.strip())

# 날짜 순으로 정렬 (필요시)
df2.sort_values(by='날짜', inplace=True)

# 그래프 그리기
plt.rc('font', family='NanumGothic')
plt.rcParams['axes.unicode_minus'] = False
plt.figure(figsize=(12,6))
plt.title('수원시 1993년 1월 기온 변화')
# x축은 데이터 행 번호(1일부터 해당 일자까지)를 사용합니다.
plt.plot(range(1, len(df2)+1), df2['max_temp'], label='최고기온', color='red')
plt.plot(range(1, len(df2)+1), df2['avg_temp'], label='평균기온', color='yellow')
plt.plot(range(1, len(df2)+1), df2['min_temp'], label='최저기온', color='blue')
plt.xlabel('일')
plt.ylabel('기온 (℃)')
plt.legend()
plt.tight_layout()
plt.savefig('수원기온.png')
plt.show()
