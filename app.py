import streamlit as st
import financedatareader as fdr
from datetime import datetime, timedelta

# 모바일 친화적인 레이아웃 설정
st.set_page_config(
    page_title="주가 데이터 추출기",
    layout="centered",  # 모바일에서는 centered가 보기 좋습니다
    initial_sidebar_state="collapsed"
)

st.title("📊 주가 데이터 추출기")
st.caption("티커를 입력하고 기간을 설정하면 일별 종가를 조회합니다.")

# --- 입력 필드 섹션 ---
st.subheader("1. 조건 입력")

# 대문자 자동 변환으로 모바일 입력 편의성 제공
ticker = st.text_input("티커 (예: AAPL, TSLA, 005930)", value="005930").strip().upper()

# 기간 설정 (기본값: 최근 1개월)
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작일", datetime.today() - timedelta(days=30))
with col2:
    end_date = st.date_input("종료일", datetime.today())

# --- 데이터 조회 및 처리 ---
if st.button("데이터 조회하기", use_container_width=True):
    if not ticker:
        st.error("티커를 입력해주세요.")
    else:
        try:
            with st.spinner("데이터를 가져오는 중..."):
                # FinanceDataReader로 데이터 다운로드
                df = fdr.DataReader(ticker, start=start_date, end=end_date)
            
            if df.empty:
                st.warning("해당 기간에 데이터가 존재하지 않습니다.")
            else:
                # 엑셀 복붙용 데이터 정제 (날짜와 종가만 추출)
                # 날짜가 인덱스로 들어오므로 포맷팅 후 컬럼으로 변경
                df_close = df[['Close']].copy()
                df_close.index = df_close.index.strftime('%Y-%m-%d')
                df_close = df_close.reset_index()
                df_close.columns = ['날짜', '종가']
                
                # 최신 날짜가 위로 오도록 정렬 (선택 사항, 원치 않으면 삭제 가능)
                df_close = df_close.sort_values(by='날짜', ascending=False)

                # --- 결과 출력 섹션 ---
                st.success(f"조회 완료: {ticker}")
                
                # 1. 표(DataFrame) 형태로 보여주기 (웹 확인용)
                st.subheader("2. 일별 종가 확인")
                st.dataframe(df_close, use_container_width=True, hide_index=True)
                
                # 2. 엑셀 복붙용 텍스트 영역 (모바일 핵심 기능)
                st.subheader("3. 엑셀 복사 구역")
                st.markdown(
                    "<small>아래 박스 안의 내용을 전체 선택(Ctrl+A) 후 복사하여 "
                    "엑셀에 붙여넣기(Ctrl+V) 하시면 칸이 딱 맞게 들어갑니다.</small>", 
                    unsafe_allow_html=True
                )
                
                # TSV(Tab Separated Values) 형태로 변환하여 텍스트 상자에 삽입
                tsv_data = df_close.to_csv(sep='\t', index=False)
                st.text_area(
                    label="탭 구분 데이터 (모바일 카피용)", 
                    value=tsv_data, 
                    height=250,
                    help="전체 선택 후 복사하세요."
                )
                
        except Exception as e:
            st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
