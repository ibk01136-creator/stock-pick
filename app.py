import streamlit as st
import FinanceDataReader as fdr

st.title("📊 삼성전자 최근 150영업일 종가 (fdr)")

# 1. 삼성전자(005930) 데이터 바로 가져오기
# 리스트 거치지 않고 코드를 직접 넣으면 에러 확률이 확 줄어듭니다.
ticker = "005930"
data = fdr.DataReader(ticker)

if not data.empty:
    # 2. 최근 150영업일 데이터만 슬라이싱 ('Close' 컬럼만)
    df_150 = data[['Close']].tail(150)
    
    # 3. 표에서 보기 좋게 날짜 형식 변경 (index가 날짜임)
    df_150.index = df_150.index.strftime('%Y-%m-%d')
    
    # 4. 최신 날짜가 위로 오도록 역순 정렬
    df_150 = df_150.sort_index(ascending=False)

    # 5. 현재가 및 등락 표시
    current_price = df_150.iloc[0]['Close']
    prev_price = df_150.iloc[1]['Close']
    change = current_price - prev_price
    
    st.metric(label="삼성전자 현재가", value=f"{current_price:,.0f}원", delta=f"{change:,.0f}원")

    # 6. 표로 출력
    st.write("### 최근 150영업일 데이터 내역")
    st.dataframe(df_150, use_container_width=True) # 스크롤 가능한 깔끔한 표
    
else:
    st.error("데이터를 불러오지 못했습니다. fdr 설치 상태나 종목 코드를 확인하세요.")
