import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📱 초간단 주식 계산기")

# 1. 종목 코드 입력 받기 (삼성전자 기본값)
ticker = st.text_input("종목 코드를 입력하세요 (예: 005930.KS, AAPL)", "005930.KS")

# 2. 데이터 가져오기
data = yf.download(ticker, period="1mo") # 최근 1개월 데이터

if not data.empty:
    # 3. 간단한 계산
    current_price = data['Close'].iloc[-1] # 최근 종가
    prev_price = data['Close'].iloc[-2]    # 전날 종가
    change = current_price - prev_price    # 변동폭

    # 4. 화면 표시
    st.metric(label=f"{ticker} 현재가", value=f"{current_price:,.0f}원", delta=f"{change:,.0f}원")
    
    st.subheader("최근 주가 흐름")
    st.line_chart(data['Close']) # 간단한 선 그래프
else:
    st.error("데이터를 불러오지 못했습니다. 종목 코드를 확인해주세요.")
