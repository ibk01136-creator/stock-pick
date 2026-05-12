import streamlit as st
import FinanceDataReader as fdr
from datetime import datetime, timedelta

st.title("⚡ 최적화된 삼성전자 분석 (최근 100일)")

ticker = "005930"

# 1. 200일 전 날짜 계산 (필요한 120영업일을 확보하기에 가장 적절한 기간)
# 오늘 날짜로부터 딱 200일 전까지만 서버에 요청합니다.
start_date = (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d')

# 2. 지정된 날짜부터 데이터 가져오기
df = fdr.DataReader(ticker, start_date)

if not df.empty:
    # 3. 가져온 데이터에서 지표 계산 (20일 이평, 표준편차)
    # df 안에는 약 140~150일치 데이터가 들어있을 것이므로 20이평 계산에 문제없음
    df['20일이평'] = df['Close'].rolling(window=20).mean()
    df['표준편차'] = df['Close'].rolling(window=20).std()

    # 4. 최종적으로 표에 보여줄 최근 100일치만 추출
    df_100 = df[['Close', '20일이평', '표준편차']].tail(100).copy()
    
    # 5. 날짜 형식 및 역순 정렬
    df_100.index = df_100.index.strftime('%Y-%m-%d')
    df_display = df_100.sort_index(ascending=False)

    # 6. 숫자 포맷팅 (콤마 및 소수점)
    df_display['Close'] = df_display['Close'].apply(lambda x: f"{x:,.0f}")
    df_display['20일이평'] = df_display['20일이평'].apply(lambda x: f"{x:,.2f}")
    df_display['표준편차'] = df_display['표준편차'].apply(lambda x: f"{x:,.2f}")

    # 7. 스크롤 없는 표 출력
    st.table(df_display)
    
else:
    st.error("데이터를 가져오는 데 실패했습니다.")
