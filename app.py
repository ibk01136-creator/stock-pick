import streamlit as st
import FinanceDataReader as fdr

st.title("🏆 시총 상위 20등 분석기")

# 데이터 가져오기 및 시총 순 정렬
df_krx = fdr.StockListing('NASDAQ')
df_sorted = df_krx.sort_values(by='MarCap', ascending=False)

# 시총 상위 20개 종목 이름만 추출
top_20_names = df_sorted['Name'].head(100).tolist()

# 선택 박스에 상위 20개만 넣어주기
target_name = st.selectbox("종목을 선택하세요 (시총 상위 20위)", top_20_names)

# 선택한 이름으로 코드(Ticker) 찾기
ticker = df_krx[df_krx['Name'] == target_name]['Code'].values[0]

# 주가 데이터 불러오기
df = fdr.DataReader(ticker, '2024')

st.line_chart(df['Close'])
