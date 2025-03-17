import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import matplotlib.pyplot as plt
import re

# Selenium 설정 (Colab 전용)
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)

url = "https://www.weather.go.kr/w/observation/land/past-obs/obs-by-day.do?stn=119&yy=1993&mm=1&obs=1"
driver.get(url)
time.sleep(3)

days, avg_temps, max_temps, min_temps = [], [], [], []
current_day = 1  # 1월이므로 1일부터 시작

# 실제 데이터를 담고 있는 tr 위치
rows = [2, 4, 6, 8, 10, 12]

for week in rows:
    for day in range(1, 8):
        try:
            xpath = f"/html/body/div[2]/section/div/div[2]/div[2]/div[3]/div/table/tbody/tr[{week}]/td[{day}]"
            data = driver.find_element(By.XPATH, xpath).text.strip()

            if data:
                lines = data.split('\n')

                # 기온정보가 있는 경우 처리 (최소 3개 이상 라인 존재 시)
                if len(lines) >= 3:
                    avg_temp = float(re.findall(r'[-]?\d+\.\d+', lines[0])[0])
                    max_temp = float(re.findall(r'[-]?\d+\.\d+', lines[1])[0])
                    min_temp = float(re.findall(r'[-]?\d+\.\d+', lines[2])[0])

                    # 날짜 데이터 추가
                    days.append(current_day)
                    avg_temps.append(avg_temp)
                    max_temps.append(max_temp)
                    min_temps.append(min_temp)

                    current_day += 1  # 날짜 증가 (자동으로 다음 날로)

                    # 31일 이후는 중단
                    if current_day > 31:
                        break

        except Exception as e:
            print(f"오류 발생: {e}")

driver.quit()

# 데이터 정리
df = pd.DataFrame({
    '일': days,
    '평균기온': avg_temps,
    '최고기온': max_temps,
    '최저기온': min_temps
})

print(df)

# 시각화
plt.figure(figsize=(14,7))
plt.plot(df['일'], df['최고기온'], marker='o', color='red', label='최고기온')
plt.plot(df['일'], df['평균기온'], marker='o', color='orange', label='평균기온')
plt.plot(df['일'], df['최저기온'], marker='o', color='blue', label='최저기온')

# 한글 폰트 설정 (Colab 환경용)
!apt-get install fonts-nanum -qq
plt.rc('font', family='NanumBarunGothic')
plt.rcParams['axes.unicode_minus'] = False

plt.title('1993년 1월 수원시 기온 변화', fontsize=15)
plt.xlabel('일', fontsize=13)
plt.ylabel('기온(℃)', fontsize=13)
plt.xticks(range(1,32))
plt.grid(True, alpha=0.4)
plt.legend()
plt.tight_layout()
plt.show()
