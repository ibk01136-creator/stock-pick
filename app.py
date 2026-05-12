import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📊 삼성전자 분석 데이터 (최근 100일)")

ticker = "005930"
# 계산을 위해 200일 전부터 데이터 가져오기
start_date = (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d')

# 1. 일봉 데이터 하나만 가져오기
df = fdr.DataReader(ticker, start_date)

if not df.empty:
    # 2. 지표 계산
    df['일봉'] = df['Close']
    df['20일이평'] = df['일봉'].rolling(window=20).mean().round(0)
    df['기울기(%)'] = ((df['20일이평'] / df['20일이평'].shift(1)) - 1) * 100
    df['변동성(%)'] = (df['일봉'].rolling(window=20).std() / df['일봉']) * 100

    # 3. 주봉 데이터 생성 (에러 없는 판다스 방식)
    # 일봉 데이터를 주간(W-FRI, 금요일 기준)으로 리샘플링하여 마지막 종가만 추출
    weekly_df = df['일봉'].resample('W-FRI').last().to_frame()
    weekly_df.columns = ['주봉']
    
    # 4. 일봉 표와 주봉 표 합치기
    # 일봉 데이터 왼쪽에 주봉을 붙입니다. (날짜가 일치하는 행에만 값이 들어감)
    df = df.join(weekly_df)

    # 5. 최근 100일치 추출
    cols = ['일봉', '20일이평', '기울기(%)', '변동성(%)', '주봉']
    df_100 = df[cols].tail(100).copy()

    # 6. 색상 결정을 위한 변화량 계산
    df_diff = df_100[['일봉', '20일이평', '기울기(%)', '변동성(%)']].diff()

    # 7. 스타일 정의 함수 (작은 글씨 & 컬러)
    def apply_style(val_df):
        style_df = pd.DataFrame('font-size: 13px; color: black', index=val_df.index, columns=val_df.columns)
        for col in ['일봉', '20일이평', '기울기(%)', '변동성(%)']:
            style_df.loc[df_diff[col] > 0, col] += '; color: #FF0000'
            style_df.loc[df_diff[col] < 0, col] += '; color: #0000FF'
        return style_df

    # 8. 날짜 형식 변경 및 역순 정렬
    df_display = df_100.sort_index(ascending=False)
    df_display.index = [d.strftime('%Y-%m-%d') for d in df_display.index]
    
    # 9. 포맷팅 및 출력
    styled_df = df_display.style.apply(lambda x: apply_style(df_display), axis=None)\
        .format({
            '일봉': '{:,.0f}',
            '20일이평': '{:,.0f}',
            '기울기(%)': '{:+.2f}%',
            '변동성(%)': '{:.2f}%',
            '주봉': lambda x: f"{x:,.0f}" if pd.notnull(x) else "-"
        })

    st.metric(label="삼성전자 현재가", value=f"{df_100['일봉'].iloc[-1]:,.0f}원")
    st.dataframe(styled_df, use_container_width=True, height=3500)
    
else:
    st.error("데이터를 가져오지 못했습니다.")
