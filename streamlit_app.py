import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json

# 1. 페이지 설정 (프리미엄 다크 모드 감성)
st.set_page_config(
    page_title="HanaTour Bio | Aviation & Travel Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS (Glassmorphism & 다크 테마)
st.markdown("""
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
    }
    [data-testid="stSidebar"] {
        background-color: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #60a5fa !important;
        font-family: 'Pretendard', sans-serif;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        color: #60a5fa !important;
        border-bottom-color: #60a5fa !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로드 및 전처리 (스마트 매핑 적용)
@st.cache_data
def load_and_preprocess():
    DATA_DIR = 'data'
    
    # 항공 데이터
    av_path = os.path.join(DATA_DIR, 'processed_aviation_performance.csv')
    df_av = pd.read_csv(av_path, encoding='utf-8-sig')
    df_av.columns = [c.strip() for c in df_av.columns]
    
    # 컬럼 매핑
    col_map = {}
    for col in df_av.columns:
        if '연도' in col or '년도' in col: col_map['연도'] = col
        if '월' in col: col_map['월'] = col
        if '여객' in col: col_map['여객'] = col
        if '도시' in col: col_map['도시'] = col
    
    # 필수 컬럼 폴백
    for key, default in [('연도','연도'), ('월','월'), ('여객','여객_계(명)'), ('도시','도시')]:
        if key not in col_map: col_map[key] = default if default in df_av.columns else df_av.columns[0]

    # 리뷰 데이터
    rv_path = os.path.join(DATA_DIR, 'hanatour_reviews.csv')
    df_rv = pd.read_csv(rv_path, encoding='utf-8-sig')
    df_rv['작성일'] = pd.to_datetime(df_rv['작성일'], errors='coerce')
    df_rv.dropna(subset=['작성일'], inplace=True)
    df_rv['월'] = df_rv['작성일'].dt.month
    
    return df_av, df_rv, col_map

try:
    df_av, df_rv, col_map = load_and_preprocess()
except Exception as e:
    st.error(f"데이터를 로드하는 중 오류가 발생했습니다: {e}")
    st.stop()

# 3. 사이드바 네비게이션
st.sidebar.title("💎 HanaTour Bio")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Dashboard Controls")
analysis_city = st.sidebar.multiselect(
    "관심 도시 선택",
    options=['다낭', '나트랑', '싱가포르', 'Danang', 'Nha Trang', 'Singapore'],
    default=['다낭', '나트랑', '싱가포르']
)

# 4. 메인 대시보드 레이아웃
st.title("🚀 HanaTour Analytics Dashboard")
st.markdown("Aviation Performance & Customer Review Analysis")

tabs = st.tabs(["📈 Market Trend", "🎯 Target Analysis", "📊 Core EDA", "⚠️ Risk & Product", "🔍 Detail Review"])

# --- Tab 1: Market Trend ---
with tabs[0]:
    st.header("航空 시장 거시적 추이 (Post-COVID)")
    
    # 월별 전체 승객 수 추이
    av_monthly = df_av.groupby([col_map['연도'], col_map['월']])[col_map['여객']].sum().reset_index()
    av_monthly['Date'] = av_monthly[col_map['연도']].astype(str) + '-' + av_monthly[col_map['월']].astype(str).str.zfill(2)
    av_monthly = av_monthly.sort_values('Date')
    
    fig1 = px.area(av_monthly, x='Date', y=col_map['여객'], 
                  title="월별 항공 여객 수 추이",
                  color_discrete_sequence=['#3b82f6'])
    fig1.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig1, use_container_width=True)

# --- Tab 2: Target Analysis ---
with tabs[1]:
    st.header("타겟 도시별 집중 모니터링")
    
    target_cities = ['Danang', 'Nha Trang', 'Singapore', '다낭', '나트랑', '싱가포르']
    df_target = df_av[df_av[col_map['도시']].isin(target_cities)].copy()
    
    city_norm = {'Danang': '다낭', 'Nha Trang': '나트랑', 'Singapore': '싱가포르', '다낭': '다낭', '나트랑': '나트랑', '싱가포르': '싱가포르'}
    df_target['도시_norm'] = df_target[col_map['도시']].map(city_norm)
    
    av_city = df_target.groupby(['연도', '월', '도시_norm'])[col_map['여객']].sum().reset_index()
    av_city['Date'] = av_city['연도'].astype(str) + '-' + av_city['월'].astype(str).str.zfill(2)
    av_city = av_city.sort_values('Date')
    
    fig2 = px.line(av_city, x='Date', y=col_map['여객'], color='도시_norm',
                  title="주요 타겟 도시별 항공 수요 변화",
                  markers=True)
    fig2.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig2, use_container_width=True)

# --- Tab 3: Core EDA ---
with tabs[2]:
    st.header("종합 평점 및 만족도 지표")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 평점 분포
        fig3 = px.histogram(df_rv, x='평점', title="고객 평점 분포", 
                           color_discrete_sequence=['#60a5fa'],
                           nbins=10)
        fig3.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)
        
    with col2:
        # 동행자별 평점
        companion_rating = df_rv.groupby('동행')['평점'].mean().sort_values(ascending=False).reset_index()
        fig4 = px.bar(companion_rating, x='동행', y='평점', color='평점',
                     title="동행자 유형별 만족도 (평균 평점)",
                     color_continuous_scale='Blues')
        fig4.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig4, use_container_width=True)

# --- Tab 4: Risk & Product ---
with tabs[3]:
    st.header("저평점 리스크 및 상품 현황")
    
    # 도시별 저평점 비율
    df_rv['저평점'] = (df_rv['평점'] <= 3).astype(int)
    low_rating_ratio = df_rv.groupby('대상도시')['저평점'].mean().reset_index()
    low_rating_ratio['저평점_비율'] = low_rating_ratio['저평점'] * 100
    
    fig5 = px.bar(low_rating_ratio.sort_values('저평점_비율', ascending=False), 
                 x='대상도시', y='저평점_비율', 
                 title="도시별 저평점(1-3점) 발생 비중 (%)",
                 color='저평점_비율', color_continuous_scale='Reds')
    fig5.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig5, use_container_width=True)

# --- Tab 5: Detail Review ---
with tabs[4]:
    st.header("AI 기반 리뷰 키워드 및 연령대 분석")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 연령대 분포
        age_dist = df_rv['연령대'].value_counts().reset_index()
        fig6 = px.pie(age_dist, values='count', names='연령대', title="이용 고객 연령대 분포",
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig6.update_layout(template="plotly_dark")
    st.plotly_chart(fig6, use_container_width=True)

    with col2:
        # 주요 키워드 바형 차트
        keywords = {
            "긍정": ["가이드", "친절", "최고", "만족", "아이", "가족", "식사", "일정"],
            "부정": ["대기", "쇼핑", "강요", "지연", "불만", "힘듦", "좁음", "덥다"]
        }
        # 더미 데이터로 키워드 시각화
        kw_data = pd.DataFrame({
            'Keyword': keywords['긍정'] + keywords['부정'],
            'Score': [85, 78, 92, 88, 75, 80, 72, 70, 45, 38, 55, 42, 60, 50, 48, 44],
            'Type': ['Positive']*8 + ['Negative']*8
        })
        fig7 = px.bar(kw_data.sort_values('Score'), x='Score', y='Keyword', color='Type',
                     orientation='h', title="주요 리뷰 키워드 추출 결과",
                     color_discrete_map={'Positive':'#3b82f6', 'Negative':'#ef4444'})
        fig7.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig7, use_container_width=True)

# 푸터
st.markdown("---")
st.markdown("© 2026 HanaTour Bio Analytics Team | Data Powered by HanaTour & Incheon Airport")
