import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📊 삼성전자 분석 데이터 (최근 100일)")

ticker = "005930"
start_date = (datetime.now() - timedelta(days=200)).strftime('%Y-%m-%d')
df = fdr.DataReader(ticker, start_date)

if not df.empty:
    # 1. 지표 계산
    df['일봉'] = df['Close']
    df['20일이평'] = df['일봉'].rolling(window=20).mean().round(0)
    df['기울기(%)'] = ((df['20일이평'] / df['20일이평'].shift(1)) - 1) * 100
    df['변동성(%)'] = (df['일봉'].rolling(window=20).std() / df['일봉']) * 100

    # 2. 주봉 데이터 처리 (공휴일 대응 로직)
    # 실제 데이터가 존재하는 날짜들의 연도-주차 정보를 생성
    df_temp = df.copy()
    df_temp['YearWeek'] = pd.to_datetime(df_temp.index).to_period('W')
    
    # 각 주차(YearWeek)별로 '실제 데이터가 있는 마지막 날'만 추출
    weekly_last_dates = df_temp.groupby('YearWeek').tail(1).index
    
    # 주봉 컬럼 생성 및 해당 날짜에만 일봉 값 기입
    df['주봉'] = None
    df.loc[weekly_last_dates, '주봉'] = df.loc[weekly_last_dates, '일봉']

    # 3. 최근 100일치 추출
    cols = ['일봉', '20일이평', '기울기(%)', '변동성(%)', '주봉']
    df_100 = df[cols].tail(100).copy()

    # 4. 색상 결정을 위한 변화량 계산
    df_diff = df_100[['일봉', '20일이평', '기울기(%)', '변동성(%)']].diff()

    # 5. 스타일 정의 함수 (작은 글씨 & 컬러)
    def apply_style(val_df):
        style_df = pd.DataFrame('font-size: 13px; color: black', index=val_df.index, columns=val_df.columns)
        for col in ['일봉', '20일이평', '기울기(%)', '변동성(%)']:
            style_df.loc[df_diff[col] > 0, col] += '; color: #FF0000'
            style_df.loc[df_diff[col] < 0, col] += '; color: #0000FF'
        return style_df

    # 6. 날짜 형식 변경 및 역순 정렬
    df_display = df_100.sort_index(ascending=False)
    df_display.index = [d.strftime('%Y-%m-%d') for d in df_display.index]
    
    # 7. 포맷팅 (주봉 빈 칸은 공백 처리)
    styled_df = df_display.style.apply(lambda x: apply_style(df_display), axis=None)\
        .format({
            '일봉': '{:,.0f}',
            '20일이평': '{:,.0f}',
            '기울기(%)': '{:+.2f}%',
            '변동성(%)': '{:.2f}%',
            '주봉': lambda x: f"{x:,.0f}" if pd.notnull(x) else "" # "-" 대신 ""(공백) 사용
        })

    # 8. 결과 출력
    st.metric(label="삼성전자 현재가", value=f"{df_100['일봉'].iloc[-1]:,.0f}원")
    st.dataframe(styled_df, use_container_width=True, height=3500)
    
else:
    st.error("데이터를 가져오지 못했습니다.")
