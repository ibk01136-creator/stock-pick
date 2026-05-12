import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

# 페이지 넓게 설정 및 타이틀
st.set_page_config(layout="wide")
st.title("📊 삼성전자 분석 데이터 (최근 100일)")

ticker = "005930"
# 필요한 데이터를 확보하기 위해 200일 전부터 가져오기
start_date = (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d')
df = fdr.DataReader(ticker, start_date)

if not df.empty:
    # 1. 지표 계산
    df['20일이평'] = df['Close'].rolling(window=20).mean().round(0)
    # 항목명 '기울기'로 변경
    df['기울기(%)'] = ((df['20일이평'] / df['20일이평'].shift(1)) - 1) * 100
    # 변동성 계산 (표준편차는 계산에만 쓰고 나중에 제외)
    df['변동성(%)'] = (df['Close'].rolling(window=20).std() / df['Close']) * 100

    # 2. 최근 100일치 데이터 추출 (표준편차 제외)
    cols = ['Close', '20일이평', '기울기(%)', '변동성(%)']
    df_100 = df[cols].tail(100).copy()

    # 3. 색상 결정을 위한 변화량 계산
    df_diff = df_100.diff()

    # 4. 스타일 정의 함수
    def apply_style(val_df):
        # 전체 폰트 크기 한 포인트 작게 설정 (약 13-14px)
        style_df = pd.DataFrame('font-size: 13px; color: black', index=val_df.index, columns=val_df.columns)
        
        for col in val_df.columns:
            style_df.loc[df_diff[col] > 0, col] += '; color: #FF0000' # 상승: 빨강
            style_df.loc[df_diff[col] < 0, col] += '; color: #0000FF' # 하락: 파랑
        return style_df

    # 5. 날짜 형식 변경 (시간 제외) 및 역순 정렬
    df_100.index = df_100.index.strftime('%Y-%m-%d')
    df_display = df_100.sort_index(ascending=False)
    
    # 스타일 및 포맷 적용
    styled_df = df_display.style.apply(lambda x: apply_style(df_display), axis=None)\
        .format({
            'Close': '{:,.0f}',
            '20일이평': '{:,.0f}',
            '기울기(%)': '{:+.2f}%',
            '변동성(%)': '{:.2f}%'
        })

    # 6. 결과 출력
    st.metric(label="삼성전자 현재가", value=f"{df_100.iloc[-1]['Close']:,.0f}원")
    
    st.write("### 최근 100영업일 지표 (글자 크기 축소 및 컬러 적용)")
    # 스크롤 없이 전체 출력
    st.dataframe(styled_df, use_container_width=True, height=3500)
    
else:
    st.error("데이터를 가져오지 못했습니다.")
