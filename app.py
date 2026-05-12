import streamlit as st
import FinanceDataReader as fdr
from datetime import datetime, timedelta

st.title("📊 삼성전자 정밀 분석 (최근 100일)")

ticker = "005930"
# 120영업일 확보를 위해 200일 전부터 가져오기
start_date = (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d')
df = fdr.DataReader(ticker, start_date)

if not df.empty:
    # 1. 지표 계산
    # 20일 이동평균 (반올림 적용)
    df['20일이평'] = df['Close'].rolling(window=20).mean().round(0)
    
    # 이평 기울기(%): (현재 이평 / 직전 이평 - 1) * 100
    df['이평기울기(%)'] = ((df['20일이평'] / df['20일이평'].shift(1)) - 1) * 100
    
    # 변동성(%): (20일 표준편차 / 종가) * 100
    # 항목명 제안: '상대변동성' 또는 '변동성(%)'
    df['변동성(%)'] = (df['Close'].rolling(window=20).std() / df['Close']) * 100

    # 2. 최근 100일치만 추출 (항목 순서 조정)
    cols = ['Close', '20일이평', '이평기울기(%)', '변동성(%)']
    df_100 = df[cols].tail(100).copy()
    
    # 3. 날짜 형식 및 역순 정렬
    df_100.index = df_100.index.strftime('%Y-%m-%d')
    df_display = df_100.sort_index(ascending=False)

    # 4. 숫자 포맷팅
    # 이평은 정수, 기울기와 변동성은 소수점 2자리
    df_display['Close'] = df_display['Close'].apply(lambda x: f"{x:,.0f}")
    df_display['20일이평'] = df_display['20일이평'].apply(lambda x: f"{x:,.0f}")
    df_display['이평기울기(%)'] = df_display['이평기울기(%)'].apply(lambda x: f"{x:+.2f}%")
    df_display['변동성(%)'] = df_display['변동성(%)'].apply(lambda x: f"{x:.2f}%")

    # 5. 현재가 및 정보 표시
    st.metric(label="삼성전자 현재가", value=f"{df_100.iloc[0]['Close']:,.0f}원")
    
    # 6. 스크롤 없는 표 출력
    st.table(df_display)
    
else:
    st.error("데이터를 가져오지 못했습니다.")
