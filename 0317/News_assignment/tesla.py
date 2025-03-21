#import sys
#!sudo add-apt-repository ppa:saiarcot895/chromium-beta
##실행 결과에서 Enter 입력
#!sudo apt remove chromium-browser
#!sudo snap remove chromium
#!sudo apt install chromium-browser
#!pip3 install selenium
#!apt-get update
#!apt install chromium-chromedriver
#!cp /usr/lib/chromium-browser/chromedriver /usr/bin
#sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')

#!sudo apt-get install -y fonts-nanum
#!sudo fc-cache -fv
#!rm ~/.cache/matplotlib -rf
#!pip install konlpy





import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
from konlpy.tag import Okt
import numpy as np
import pandas as pd
from urllib.parse import quote

# 검색어와 URL 설정 (예: 테슬라)
topic = "테슬라"
encoded_topic = quote(topic)
url = f"https://search.naver.com/search.naver?sm=tab_hty.top&where=news&ssc=tab.news.all&query={encoded_topic}&nso=so%3Add%2Cp%3A1w&sort=1"

# Selenium 옵션 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless') #백그라운드 실행
options.add_argument('--no-sandbox') #샌드박스 보안기능 비활성화
options.add_argument('--disable-dev-shm-usage') # 공유 메모리 사용 제한 옵션(리눅스나 도크에서 주로 사용)
webdriver_service = Service('/usr/bin/chromedriver') #크롬드라이버의 실행 경로를 지정
driver = webdriver.Chrome(service=webdriver_service, options=options)
driver.get(url)
time.sleep(1)

# (옵션) 스크롤하여 뉴스 데이터를 로딩
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# 데이터 추출 (최대 30개 기사)
columns = ['순위', '원본시간', '제목', '미리보기']
rank = []
pub_time_list = []
title_list = []
preview_list = []
max_articles = 30

for i in range(1, max_articles + 1):
    try:
        rank.append(i)
        pub_time = driver.find_element(By.XPATH, f"/html/body/div[3]/div[2]/div/div[1]/section/div/div[2]/ul/li[{i}]/div/div/div[1]/div[2]/span").text.strip()
        title_text = driver.find_element(By.XPATH, f"/html/body/div[3]/div[2]/div/div[1]/section/div/div[2]/ul/li[{i}]//a[@class='news_tit']").text.strip()
        preview_text = driver.find_element(By.XPATH, f"/html/body/div[3]/div[2]/div/div[1]/section/div/div[2]/ul/li[{i}]/div/div/div[2]/div/div/a").text.strip()
        pub_time_list.append(pub_time)
        title_list.append(title_text)
        preview_list.append(preview_text)
    except Exception as e:
        print(f"{i}번째 기사는 더 이상 추출할 수 없어 종료합니다.")
        break

driver.quit()

# DataFrame 생성 및 CSV 저장
df = pd.DataFrame({
    columns[0]: rank,
    columns[1]: pub_time_list,
    columns[2]: title_list,
    columns[3]: preview_list
}, columns=columns)
print(df.head())

filename = f"{topic}_news.csv"
df.to_csv(filename, index=False, encoding='utf-8-sig')
print(f"CSV 파일 저장 완료: '{filename}' (기사 수: {len(df)}개)")

# CSV 파일 읽어오기
filename = '테슬라_news.csv'  # 실제 저장된 파일명으로 변경
f = open(filename, 'r', encoding='utf-8-sig')
rdr = csv.reader(f)
next(rdr)  # 첫 줄(헤더) 건너뛰기

title = ''
for line in rdr:
    title = title + ' ' + line[2]  # 제목 컬럼 (인덱스 2)

f.close()  # 파일 닫기

print(title)

# 기존 코드와 동일하게 문자열 처리
title = title[6:]
print(title)

# 형태소 분석 및 단어 빈도수 계산
okt = Okt()
nouns = okt.nouns(title)
words = [n for n in nouns if len(n) > 1]  # 길이가 1보다 큰 단어만 사용
c = Counter(words)

# 워드클라우드 생성
wc = WordCloud(font_path='/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
               scale=2.0, colormap='Spectral')
gen = wc.generate_from_frequencies(c)

plt.figure()
plt.imshow(gen)
plt.axis('off')
plt.show()
