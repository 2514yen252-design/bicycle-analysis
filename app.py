import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="서울시 따릉이 데이터 대시보드", layout="wide")
st.title("🚲 서울시 따릉이 이용 패턴 분석")

# 2. 데이터베이스 연결 확인
DB_PATH = 'bicycle.db'

if not os.path.exists(DB_PATH):
    st.error(f"⚠️ '{DB_PATH}' 파일을 찾을 수 없습니다. 데이터베이스 파일이 같은 폴더에 있는지 확인해주세요!")
    st.stop()

def run_query(q):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(q, conn)

# --- 차트 1: 월별 이용 패턴 ---
st.header("1. 월별 이용 패턴")
query1 = """
SELECT 대여일자, SUM(이용건수) as 총이용건수
FROM 이용정보
GROUP BY 대여일자
ORDER BY 대여일자
"""
df1 = run_query(query1)
fig1 = px.line(df1, x='대여일자', y='총이용건수', markers=True, title="월별 따릉이 이용 추이")
st.plotly_chart(fig1, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(query1, language='sql')
    st.write("- **인사이트**: 특정 월에 이용량이 급증하거나 급감하는 패턴을 확인할 수 있습니다. 주로 야외 활동이 적은 겨울철에 이용량이 낮아지는 경향이 있습니다.")

# --- 차트 2: 기온별 평균 이용량 ---
st.header("2. 기온별 평균 이용량 (5도 구간)")
query2 = """
SELECT 
    CAST(기온.평균기온 / 5 AS INT) * 5 as 기온구간,
    AVG(이용정보.이용건수) as 평균이용건수
FROM 이용정보
JOIN 기온 ON 이용정보.대여일자 = 기온.년월
GROUP BY 기온구간
"""
df2 = run_query(query2)
df2['기온구간_명'] = df2['기온구간'].astype(str) + "도 ~ " + (df2['기온구간']+5).astype(str) + "도"
fig2 = px.bar(df2, x='기온구간_명', y='평균이용건수', title="평균 기온 구간별 이용량", color='평균이용건수')
st.plotly_chart(fig2, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(query2, language='sql')
    st.write("- **인사이트**: 기온이 너무 낮거나 높을 때보다 활동하기 좋은 적정 온도 구간에서 평균 이용건수가 높게 나타납니다. 날씨와 이용량의 밀접한 상관관계를 보여줍니다.")

# --- 차트 3: 인기 대여소 TOP 10 ---
st.header("3. 인기 대여소 TOP 10")
query3 = """
SELECT 대여소.보관소명, SUM(이용정보.이용건수) as 총이용건수
FROM 이용정보
JOIN 대여소 ON 이용정보.대여소번호 = 대여소.대여소번호
GROUP BY 대여소.보관소명
ORDER BY 총이용건수 DESC
LIMIT 10
"""
df3 = run_query(query3)
fig3 = px.bar(df3, x='총이용건수', y='보관소명', orientation='h', title="가장 많이 이용하는 대여소 상위 10곳", color='총이용건수')
fig3.update_layout(yaxis={'categoryorder':'total ascending'}) # 높은 순서대로 정렬
st.plotly_chart(fig3, use_container_width=True)

with st.expander("사용한 SQL 및 인사이트 보기"):
    st.code(query3, language='sql')
    st.write("- **인사이트**: 유동인구가 많은 지하철역 인근이나 공원 근처 대여소가 상위권을 차지하고 있습니다. 해당 지역의 자전거 거치대 증설 검토 자료로 활용 가능합니다.")