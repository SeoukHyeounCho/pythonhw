!pip install yfinance requests beautifulsoup4 lxml --quiet

import requests
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup

plt.rc('font', family='NanumBarunGothic')  # 한글 폰트 (Windows/Colab 등)

################################################################################
# (A) 섹터 라벨 사전: "영문\n(한글)" (영문을 Key로)
################################################################################
SECTOR_LABELS = {
    "Information Technology": "Information Technology\n(정보기술)",
    "Health Care": "Health Care\n(헬스케어)",
    "Financials": "Financials\n(금융)",
    "Industrials": "Industrials\n(산업재)",
    "Consumer Discretionary": "Consumer Discretionary\n(경기소비재)",
    "Consumer Staples": "Consumer Staples\n(필수소비재)",
    "Energy": "Energy\n(에너지)",
    "Utilities": "Utilities\n(유틸리티)",
    "Real Estate": "Real Estate\n(부동산)",
    "Communication Services": "Communication Services\n(커뮤니케이션 서비스)",
    "Materials": "Materials\n(소재)"
}
VALID_GICS_SECTORS = set(SECTOR_LABELS.keys())

################################################################################
# (B) 위키피디아에서 현재 S&P 500 종목 + 섹터 목록 가져오기
################################################################################
def fetch_sp500_wikipedia():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(requests.get(url).text)
    df = tables[0]
    df = df.rename(columns={
        "Symbol": "Symbol",
        "Security": "Security",
        "GICS Sector": "GICS Sector"
    })
    df["Symbol"] = df["Symbol"].str.replace(".", "-", regex=False).str.upper()
    df.drop_duplicates(subset=["Symbol"], inplace=True)
    return df[["Symbol", "Security", "GICS Sector"]]

################################################################################
# (C) S&P 500 중 11개 GICS 섹터만 필터링
################################################################################
def filter_11sectors(df):
    mask = df["GICS Sector"].isin(VALID_GICS_SECTORS)
    return df[mask].copy()

################################################################################
# (D) 2004~2024 월간 데이터 다운로드
################################################################################
def download_monthly_data(tickers, start="2004-01-01", end="2024-12-31"):
    df = yf.download(tickers, start=start, end=end, interval="1mo", progress=False, group_by="ticker")
    if "Adj Close" in df.columns:
        df = df["Adj Close"]
    else:
        # 혹은 df.xs("Close", level=1, axis=1)
        df = df.xs("Close", axis=1, level=1, drop_level=True)
    df.sort_index(inplace=True)
    df = df.ffill().bfill()
    return df

################################################################################
# (E) 각 티커의 '최초 유효 데이터 날짜(2004년~)' 찾기
################################################################################
def get_earliest_date_in_2004on(series):
    """
    series: index=날짜, value=주가
    첫 유효값의 날짜 반환. 없으면 None.
    """
    idx = series.first_valid_index()
    if idx is None:
        return None
    return idx

################################################################################
# (F) 섹터별 주가 합: 중간 상장 시점부터 반영
################################################################################
def make_sector_sum_with_inclusion(prices_df, sp500_info, earliest_map):
    # 티커 -> 섹터
    sector_map = dict(zip(sp500_info["Symbol"], sp500_info["GICS Sector"]))

    records = []
    for date in prices_df.index:
        row = prices_df.loc[date]
        sector_sums = {}
        for ticker in prices_df.columns:
            start_d = earliest_map.get(ticker, None)
            if start_d is None:
                # 이 티커는 유효 데이터가 전혀 없음
                continue
            # start_d <= date => 해당 시점부터 주가 반영
            if start_d <= date:
                val = row[ticker]
                if not np.isnan(val):
                    gics = sector_map.get(ticker, None)
                    if gics:
                        sector_sums[gics] = sector_sums.get(gics, 0.0) + val

        for sec, s_val in sector_sums.items():
            records.append({"Date": date, "Sector": sec, "SumValue": s_val})

    df_rec = pd.DataFrame(records)
    pivot_df = df_rec.pivot(index="Date", columns="Sector", values="SumValue")
    pivot_df.sort_index(inplace=True)
    pivot_df = pivot_df.ffill().bfill()
    return pivot_df

################################################################################
# (G) 성장률(%) 변환
################################################################################
def calculate_growth(df):
    out = df.copy()
    first_row = out.iloc[0]
    for c in out.columns:
        out[c] = (out[c] / first_row[c]) * 100.0
    return out

################################################################################
# (H) 최종 성장률 테이블 출력 함수
################################################################################
def print_final_growth_tables(sector_growth_df):
    """
    섹터별 최종 성장률(%)을 표로 정리해 출력.
    (마지막 날짜 기준, 내림차순 정렬)
    그리고 (최종-100) 순증(%)도 함께 확인.
    """
    final_date = sector_growth_df.index[-1]
    final_values = sector_growth_df.loc[final_date]

    df_final = pd.DataFrame({
        "Sector": final_values.index,
        "Final Growth (%)": final_values.values
    })
    # 라벨을 영어->"영문\n(한글)"
    df_final["Sector"] = df_final["Sector"].apply(lambda x: SECTOR_LABELS.get(x, x))

    df_final.sort_values("Final Growth (%)", ascending=False, inplace=True)
    df_final.reset_index(drop=True, inplace=True)

    print("=== [최종 성장률(%) 표] ===")
    print(df_final)
    print()

    df_final["Net Increase (%)"] = df_final["Final Growth (%)"] - 100
    print("=== [최종 성장률 + 순증(%) 표] ===")
    print(df_final)
    print()

################################################################################
# (I) 메인 실행
################################################################################
if __name__ == "__main__":
    # 1) S&P 500 현재 구성
    sp500_all = fetch_sp500_wikipedia()
    # 2) 11개 섹터만
    sp500_df = filter_11sectors(sp500_all)
    sp500_df.reset_index(drop=True, inplace=True)

    # 3) 월간 데이터 다운로드
    tickers = sp500_df["Symbol"].unique().tolist()
    prices_df = download_monthly_data(tickers)

    # 4) 각 티커의 '데이터 시작(2004년 이후)' 인덱스
    earliest_map = {}
    for col in prices_df.columns:
        earliest_map[col] = get_earliest_date_in_2004on(prices_df[col])

    # 5) 섹터별 합(중간 상장 시점 포함)
    sector_sum_df = make_sector_sum_with_inclusion(prices_df, sp500_df, earliest_map)

    # 6) 성장률 계산
    sector_growth_df = calculate_growth(sector_sum_df)

    # 7) 최종 성장률 테이블 출력
    print_final_growth_tables(sector_growth_df)

    # (옵션) SPY와 비교 그래프, 상관관계 등 추가하려면
    # 스크립트 확장 가능
