import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📊 삼성전자 분석 데이터 (최근 100일)")

ticker = "005930"
start_date = (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d')

# 1. 데이터 가져오기 (일봉과 주봉을 각각 준비)
df_daily = fdr.DataReader(ticker, start_date)
# 'W' 옵션을 주면 fdr이 알아서 주봉(각 주의 마지막 영업일 종가)을 계산해서 줍니다.
df_weekly = fdr.DataReader(ticker, start_date, unit='W')[['Close']]
df_weekly.columns = ['주봉']

if not df_daily.empty:
    # 2. 일봉 지표 계산
    df_daily['일봉'] = df_daily['Close']
    df_daily['20일이평'] = df_daily['일봉'].rolling(window=20).mean().round(0)
    df_daily['기울기(%)'] = ((df_daily['20일이평'] / df_daily['20일이평'].shift(1)) - 1) * 100
    df_daily['변동성(%)'] = (df_daily['일봉'].rolling(window=20).std() / df_daily['일봉']) * 100

    # 3. 일봉 데이터와 주봉 데이터를 합치기 (Join)
    # 일봉 날짜와 주봉 날짜가 일치하는 행에만 주봉 값이 들어갑니다.
    df = df_daily.join(df_weekly)

    # 4. 최근 100일치 데이터 추출
    cols = ['일봉', '20일이평', '기울기(%)', '변동성(%)', '주봉']
    df_100 = df[cols].tail(100).copy()

    # 5. 색상 결정을 위한 변화량 계산
    df_diff = df_100[['일봉', '20일이평', '기울기(%)', '변동성(%)']].diff()

    # 6. 스타일 정의 함수 (작은 글씨 & 컬러)
    def apply_style(val_df):
        style_df = pd.DataFrame('font-size: 13px; color: black', index=val_df.index, columns=val_df.columns)
        for col in ['일봉', '20일이평', '기울기(%)', '변동성(%)']:
            style_df.loc[df_diff[col] > 0, col] += '; color: #FF0000'
            style_df.loc[df_diff[col] < 0, col] += '; color: #0000FF'
        return style_df

    # 7. 날짜 형식 변경 및 역순 정렬
    df_display = df_100.sort_index(ascending=False)
    df_display.index = [d.strftime('%Y-%m-%d') for d in df_display.index]
    
    # 8. 데이터 포맷팅
    styled_df = df_display.style.apply(lambda x: apply_style(df_display), axis=None)\
        .format({
            '일봉': '{:,.0f}',
            '20일이평': '{:,.0f}',
            '기울기(%)': '{:+.2f}%',
            '변동성(%)': '{:.2f}%',
            '주봉': lambda x: f"{x:,.0f}" if pd.notnull(x) else "-"
        })

    # 9. 결과 출력
    st.metric(label="삼성전자 현재가", value=f"{df_100['일봉'].iloc[-1]:,.0f}원")
    st.dataframe(styled_df, use_container_width=True, height=3500)
    
else:
    st.error("데이터를 가져오지 못했습니다.")
