import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

st.title("📱 fdr 주식 계산기")

# 1. 종목 코드 입력 받기 (삼성전자 기본값)
# fdr은 국내 주식의 경우 숫자만 입력해도 잘 작동합니다.
ticker = st.text_input("종목 코드를 입력하세요 (예: 005930, AAPL)", "005930")

# 2. 데이터 가져오기 (시작 날짜를 지정하는 방식이 일반적입니다)
# 최근 1개월 데이터를 가져오기 위해 시작 날짜를 설정합니다.
data = fdr.DataReader(ticker) 

if not data.empty:
    # 3. 간단한 계산
    current_price = data['Close'].iloc[-1] # 최근 종가
    prev_price = data['Close'].iloc[-2]    # 전날 종가
    change = current_price - prev_price    # 변동폭

    # 4. 화면 표시
    # fdr은 국내 주식 가격을 숫자로 잘 가져오므로 콤마(,) 처리를 해줍니다.
    st.metric(label=f"{ticker} 현재가", value=f"{current_price:,.0f}원", delta=f"{change:,.0f}원")
    
    st.subheader("최근 주가 흐름 (전체)")
    st.line_chart(data['Close']) # 선 그래프
else:
    st.error("데이터를 불러오지 못했습니다. 종목 코드를 확인해주세요.")
