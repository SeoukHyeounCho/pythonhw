import time
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from urllib.parse import quote

def group_time(pub_time):
    if re.search(r"(시간|분) 전", pub_time):
        return "1일 전"
    match = re.search(r"(\d+)일 전", pub_time)
    return f"{match.group(1)}일 전" if match else "기타"

def crawl_naver_news_xpath(topic):
    encoded_topic = quote(topic)
    # 최신 제공 URL 구조 반영
    url = f"https://search.naver.com/search.naver?sm=tab_hty.top&where=news&ssc=tab.news.all&query={encoded_topic}&nso=so%3Add%2Cp%3A1w&sort=1"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=options)

    print(f"\n[{topic}] 페이지 로딩 시작...")
    driver.get(url)
    time.sleep(1)

    # 스크롤 처리
    print(f"[{topic}] 스크롤하여 뉴스 데이터를 로딩 중...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_count = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        scroll_count += 1
        print(f"[{topic}] 스크롤 {scroll_count}회 진행 (높이: {new_height})")

        if new_height == last_height:
            print(f"[{topic}] 모든 뉴스가 로딩 완료됨. 총 스크롤 {scroll_count}회.")
            break
        last_height = new_height

    news_data = []
    idx = 1
    print(f"[{topic}] 뉴스 데이터 추출 시작...")
    while True:
        try:
            # 업데이트된 XPath 적용 (안정적 클래스 기반)
            time_xpath = f"/html/body/div[3]/div[2]/div/div[1]/section/div/div[2]/ul/li[{idx}]/div/div/div[1]/div[2]/span"
            title_xpath = f"/html/body/div[3]/div[2]/div/div[1]/section/div/div[2]/ul/li[{idx}]//a[@class='news_tit']"
            preview_xpath = f"/html/body/div[3]/div[2]/div/div[1]/section/div/div[2]/ul/li[{idx}]/div/div/div[2]/div/div/a"

            pub_time = driver.find_element(By.XPATH, time_xpath).text.strip()
            title = driver.find_element(By.XPATH, title_xpath).text.strip()
            preview = driver.find_element(By.XPATH, preview_xpath).text.strip()

            grouped_time = group_time(pub_time)

            news_data.append({
                "기준시간": grouped_time,
                "원본시간": pub_time,
                "제목": title,
                "미리보기": preview
            })

            print(f"[{topic}] {idx}번째 기사 추출 완료: {title[:30]}...")
            idx += 1
        except Exception as e:
            print(f"[{topic}] 추출 종료: 총 {idx-1}개의 기사를 추출함.")
            break

    driver.quit()

    # CSV로 저장
    df = pd.DataFrame(news_data)
    day_order = ["1일 전", "2일 전", "3일 전", "4일 전", "5일 전", "6일 전", "7일 전", "기타"]
    df['기준시간'] = pd.Categorical(df['기준시간'], categories=day_order, ordered=True)
    df.sort_values(by='기준시간', inplace=True)

    filename = f"{topic}_news.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"[{topic}] CSV 저장 완료: '{filename}' (기사 수: {len(df)}개)\n")

topics = ["주식", "우크라이나", "BTC", "AI", "관세", "반도체"]

for topic in topics:
    crawl_naver_news_xpath(topic)
