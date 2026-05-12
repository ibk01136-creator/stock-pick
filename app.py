import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide") # 표를 넓게 보기 위해 설정
st.title("📊 삼성전자 정밀 분석 (컬러 지표)")

ticker = "005930"
start_date = (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d')
df = fdr.DataReader(ticker, start_date)

if not df.empty:
    # 1. 지표 계산
    df['20일이평'] = df['Close'].rolling(window=20).mean().round(0)
    df['이평기울기(%)'] = ((df['20일이평'] / df['20일이평'].shift(1)) - 1) * 100
    df['표준편차'] = df['Close'].rolling(window=20).std()
    df['변동성(%)'] = (df['표준편차'] / df['Close']) * 100

    # 2. 최근 100일치 데이터 추출
    cols = ['Close', '20일이평', '이평기울기(%)', '표준편차', '변동성(%)']
    df_100 = df[cols].tail(100).copy()

    # 3. 색상 결정을 위한 전날 대비 변화량 계산 (Style 적용용)
    df_diff = df_100.diff()

    # 4. 스타일 정의 함수
    def color_delta(val_df):
        # 기본 검정색
        colors = pd.DataFrame('color: black', index=val_df.index, columns=val_df.columns)
        
        for col in val_df.columns:
            # 표준편차는 변동성과 연동하여 색상 결정
            target_diff = df_diff['변동성(%)'] if col in ['표준편차', '변동성(%)'] else df_diff[col]
            
            colors.loc[target_diff > 0, col] = 'color: #FF0000' # 상승: 빨강
            colors.loc[target_diff < 0, col] = 'color: #0000FF' # 하락: 파랑
        return colors

    # 5. 데이터 포맷팅 및 역순 정렬
    df_display = df_100.sort_index(ascending=False)
    
    # 스타일 적용
    styled_df = df_display.style.apply(lambda x: color_delta(df_display), axis=None)\
        .format({
            'Close': '{:,.0f}',
            '20일이평': '{:,.0f}',
            '이평기울기(%)': '{:+.2f}%',
            '표준편차': '{:,.2f}',
            '변동성(%)': '{:.2f}%'
        })

    # 6. 결과 출력
    st.metric(label="삼성전자 현재가", value=f"{df_100.iloc[-1]['Close']:,.0f}원")
    
    st.write("### 최근 100영업일 분석 (빨강: 상승 / 파랑: 하락)")
    # 스크롤 없이 크게 보기 위해 height를 넉넉히 설정
    st.dataframe(styled_df, use_container_width=True, height=3500)
    
else:
    st.error("데이터를 가져오지 못했습니다.")
