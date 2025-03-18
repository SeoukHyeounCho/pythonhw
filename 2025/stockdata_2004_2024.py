
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup

plt.rc('font', family='NanumBarunGothic')  # 한글폰트 적용(Windows/Colab 등)

################################################################################
# (A) 섹터 라벨 사전: "영문\n(한글)"
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
# (B) 위키피디아에서 S&P 500 종목 + 섹터 수집
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
# (C) 2004~2024 월간 데이터 다운로드
################################################################################
def download_monthly_data(tickers, start="2004-01-01", end="2024-12-31"):
    df = yf.download(tickers, start=start, end=end, interval="1mo", progress=False, group_by="ticker")
    if "Adj Close" in df.columns:
        df = df["Adj Close"]
    else:
        df = df.xs("Close", axis=1, level=1, drop_level=True)
    df.sort_index(inplace=True)
    df = df.ffill().bfill()
    return df

################################################################################
# (D) '최초 유효 데이터 날짜' (2004년 이후)
################################################################################
def get_earliest_date_in_2004on(series):
    notnull_idx = series.first_valid_index()
    if notnull_idx is None:
        return None
    return notnull_idx

################################################################################
# (E) 섹터별 주가 합(중간 상장 시점부터 반영)
################################################################################
def make_sector_sum_with_inclusion(prices, sp500_info, earliest_map):
    # 티커 -> 섹터
    sector_map = dict(zip(sp500_info["Symbol"], sp500_info["GICS Sector"]))

    records = []
    for date in prices.index:
        row = prices.loc[date]
        sector_sums = {}
        for ticker in prices.columns:
            start_d = earliest_map.get(ticker, None)
            if start_d is None:
                continue
            # start_d <= date => 해당 날짜부터 반영
            if start_d <= date:
                val = row[ticker]
                if not np.isnan(val):
                    sec = sector_map.get(ticker, None)
                    if sec is not None:
                        sector_sums[sec] = sector_sums.get(sec, 0.0) + val
        
        for sec, total_val in sector_sums.items():
            records.append({"Date": date, "Sector": sec, "SumValue": total_val})
    
    df_rec = pd.DataFrame(records)
    pivot = df_rec.pivot(index="Date", columns="Sector", values="SumValue")
    pivot.sort_index(inplace=True)
    pivot = pivot.ffill().bfill()
    return pivot

################################################################################
# (F) 성장률(%)로 변환
################################################################################
def calculate_growth(df):
    out = df.copy()
    first_row = out.iloc[0]
    for c in out.columns:
        out[c] = (out[c] / first_row[c]) * 100.0
    return out

################################################################################
# (G) 시각화 함수들
################################################################################
def plot_market_cap_trends(spy_series, sector_data):
    """
    모든 섹터 vs SPY 하나의 그래프
    """
    # x축 라벨 대신 범례에 영문+한글 표기
    # 열 이름을 영문+한글로 변환
    mapped_cols = [SECTOR_LABELS.get(x,x) for x in sector_data.columns]
    
    plt.figure(figsize=(12,6))
    # 각각 섹터 라벨 적용해 플롯
    for orig_col, new_label in zip(sector_data.columns, mapped_cols):
        plt.plot(sector_data.index, sector_data[orig_col], label=new_label)
    plt.plot(spy_series.index, spy_series, label="S&P 500 (SPY)", color="black", linewidth=2)
    
    plt.title("2004년 기준, 중간 상장 시점부터 합산한 섹터별 주가 성장률")
    plt.xlabel("Date")
    plt.ylabel("Growth (%)")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_all_sectors_vs_spy(sector_data, spy_data):
    """
    섹터별 vs SPY 개별 그래프
    """
    for col in sector_data.columns:
        label_text = SECTOR_LABELS.get(col, col)
        plt.figure(figsize=(10,5))
        plt.plot(sector_data.index, sector_data[col], label=label_text, color="blue")
        plt.plot(spy_data.index, spy_data, label="S&P 500 (SPY)", color="red")
        plt.title(f"[{label_text}] vs SPY (중간 상장 포함)")
        plt.xlabel("Date")
        plt.ylabel("Growth (%)")
        plt.legend()
        plt.grid(True)
        plt.show()

def analyze_sector_correlation(df):
    """
    5년 단위 상관관계 히트맵:
    영어+한글 라벨을 히트맵 축에도 적용
    """
    start_year = 2004
    end_year = 2024
    step = 5
    for y in range(start_year, end_year, step):
        start_date = f"{y}-01-01"
        end_date = f"{y+step}-01-01"
        df_slice = df.loc[start_date:end_date].dropna(axis=1, how="all")
        if df_slice.shape[1] < 2:
            print(f"{start_date}~{end_date}: 섹터 2개 미만 -> 스킵")
            continue
        
        corr_mat = df_slice.corr()
        
        # 상관행렬 축 라벨 영문->"영문\n(한글)"
        new_index = [SECTOR_LABELS.get(x, x) for x in corr_mat.index]
        new_cols = [SECTOR_LABELS.get(x, x) for x in corr_mat.columns]
        corr_mat.index = new_index
        corr_mat.columns = new_cols
        
        plt.figure(figsize=(10,8))
        sns.heatmap(corr_mat, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
        plt.title(f"{y}~{y+step} 섹터 상관관계 (중간상장 포함)")
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=45)
        plt.tight_layout()
        plt.show()


################################################################################
# (H) 메인 실행부
################################################################################
if __name__ == "__main__":
    # 1) 위키피디아 S&P 500 로드
    sp500_all = fetch_sp500_wikipedia()
    # 2) 11개 섹터만 남김
    mask = sp500_all["GICS Sector"].isin(VALID_GICS_SECTORS)
    sp500_df = sp500_all[mask].copy().reset_index(drop=True)

    # 3) 월간 데이터 다운로드 (2004~2024)
    tickers = sp500_df["Symbol"].unique().tolist()
    prices_df = download_monthly_data(tickers)

    # 4) 각 티커 최초 유효 날짜(2004년 이후) 찾기
    earliest_map = {}
    for col in prices_df.columns:
        earliest_map[col] = get_earliest_date_in_2004on(prices_df[col])

    # 5) 섹터별로 중간 상장 시점부터 합산
    sector_sum_df = make_sector_sum_with_inclusion(prices_df, sp500_df, earliest_map)

    # 6) 성장률(%) 변환
    sector_growth_df = calculate_growth(sector_sum_df)

    # 7) SPY 성장률
    spy_raw = yf.download("SPY", start="2004-01-01", end="2024-12-31", interval="1mo", progress=False)
    if "Adj Close" in spy_raw.columns:
        spy_series = spy_raw["Adj Close"].ffill().bfill()
    else:
        spy_series = spy_raw["Close"].ffill().bfill()

    spy_series = spy_series.sort_index()
    spy_growth = (spy_series / spy_series.iloc[0]) * 100.0

    # 8) 그래프(전체 vs SPY)
    plot_market_cap_trends(spy_growth, sector_growth_df)

    # 9) 그래프(섹터별 vs SPY)
    plot_all_sectors_vs_spy(sector_growth_df, spy_growth)

    # 10) 5년 단위 상관관계
    analyze_sector_correlation(sector_growth_df)
