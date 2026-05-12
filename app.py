import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

# 페이지 넓게 설정
st.set_page_config(layout="wide")
st.title("📊 삼성전자 분석 데이터 (최근 100일)")

ticker = "005930"
# 계산을 위해 200일 전부터 데이터 가져오기
start_date = (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d')
df = fdr.DataReader(ticker, start_date)

if not df.empty:
    # 1. 지표 계산
    df['일봉'] = df['Close']
    df['20일이평'] = df['일봉'].rolling(window=20).mean().round(0)
    df['기울기(%)'] = ((df['20일이평'] / df['20일이평'].shift(1)) - 1) * 100
    df['변동성(%)'] = (df['일봉'].rolling(window=20).std() / df['일봉']) * 100

    # 2. 주봉 데이터 처리
    # 각 주(W)의 마지막(last) 영업일 데이터의 날짜들을 추출
    weekly_last_days = df.resample('W').last().index
    # 주봉 컬럼 생성: 주 마지막 날이면 일봉 값을 넣고, 아니면 NaN
    df['주봉'] = df.index.where(df.index.isin(weekly_last_days), None)
    df.loc[df['주봉'].notnull(), '주봉'] = df['일봉']

    # 3. 최근 100일치 데이터 추출
    cols = ['일봉', '20일이평', '기울기(%)', '변동성(%)', '주봉']
    df_100 = df[cols].tail(100).copy()

    # 4. 색상 결정을 위한 변화량 계산 (일봉 기준)
    df_diff = df_100.diff()

    # 5. 스타일 정의 함수 (작은 글씨 & 컬러)
    def apply_style(val_df):
        style_df = pd.DataFrame('font-size: 13px; color: black', index=val_df.index, columns=val_df.columns)
        
        for col in val_df.columns:
            if col == '주봉': continue # 주봉은 색상 변화 제외
            style_df.loc[df_diff[col] > 0, col] += '; color: #FF0000' # 상승: 빨강
            style_df.loc[df_diff[col] < 0, col] += '; color: #0000FF' # 하락: 파랑
        return style_df

    # 6. 날짜 형식 변경 및 역순 정렬
    df_100.index = df_100.index.strftime('%Y-%m-%d')
    df_display = df_100.sort_index(ascending=False)
    
    # 7. 데이터 포맷팅
    styled_df = df_display.style.apply(lambda x: apply_style(df_display), axis=None)\
        .format({
            '일봉': '{:,.0f}',
            '20일이평': '{:,.0f}',
            '기울기(%)': '{:+.2f}%',
            '변동성(%)': '{:.2f}%',
            '주봉': lambda x: f"{x:,.0f}" if pd.notnull(x) else "-" # 주봉만 따로 처리
        })

    # 8. 결과 출력
    current_price = df_100['일봉'].iloc[-1]
    st.metric(label="삼성전자 현재가", value=f"{current_price:,.0f}원")
    
    st.write("### 최근 100영업일 상세 분석")
    st.dataframe(styled_df, use_container_width=True, height=3500)
    
else:
    st.error("데이터를 가져오지 못했습니다.")
