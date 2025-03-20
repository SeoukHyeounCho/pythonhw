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
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
webdriver_service = Service('/usr/bin/chromedriver')
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

# CSV 파일 읽어오기 (제목만 추출하여 텍스트 분석)
with open(filename, 'r', encoding='utf-8-sig') as f:
    rdr = csv.reader(f)
    all_titles = ''
    # 첫 줄은 헤더이므로 건너뜁니다.
    next(rdr)
    for line in rdr:
        all_titles += ' ' + line[2]  # 제목 컬럼 (인덱스 2)

all_titles = all_titles.strip()
print(all_titles)

exclude_words = {'엘앤', '에프', '테슬라'}

# 단어 길이가 1보다 크고 제외 리스트에 없는 단어만 선택
words = [n for n in nouns if len(n) > 1 and n not in exclude_words]

# 문자열 분석 및 워드클라우드 생성
okt = Okt()
nouns = okt.nouns(all_titles)
words = [n for n in nouns if len(n) > 1]
c = Counter(words)

stopwords = {'엘앤', '에프', '테슬라'}
wc = WordCloud(font_path='/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
               scale=2.0, colormap='Spectral',
               stopwords=stopwords)
gen = wc.generate_from_frequencies(c)
plt.figure()
plt.imshow(gen)
plt.axis('off')
plt.show()
