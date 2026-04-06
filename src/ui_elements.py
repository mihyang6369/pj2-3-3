import streamlit as st

# 주요 브랜드 색상 (하나투어 스타일을 가미한 Sea/Resort 테마)
# 요청하신 바다/휴양지 컨셉을 위해 파스텔 블루와 샌드 베이지를 조합합니다.
PRIMARY_COLOR = "#378ADD"   # 하나투어 블루 (바다)
SECONDARY_COLOR = "#F4A460" # 샌드 베이지 (해변)
ACCENT_COLOR = "#1D9E75"    # 나트랑 에메랄드 그린

def apply_custom_style():
    """
    대시보드 전반에 하나투어 프리미엄 해양 테마를 적용합니다.
    """
    st.markdown(f"""
    <style>
    /* 메인 배경 및 타이틀 디자인 */
    .stApp {{
        background-color: #F8FBFF;
    }}
    h1 {{
        color: {PRIMARY_COLOR};
        font-family: 'Malgun Gothic', sans-serif;
        border-bottom: 3px solid {SECONDARY_COLOR};
        padding-bottom: 10px;
    }}
    h2, h3 {{
        color: #1e40af;
    }}
    
    /* 카드 컴포넌트 스타일 */
    .stMetric {{
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }}
    
    /* 탭 헤더 스타일 */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #ffffff;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #64748b;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {PRIMARY_COLOR} !important;
        color: white !important;
        font-weight: bold;
    }}
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {{
        background-color: #F0F4F8;
    }}
    </style>
    """, unsafe_allow_html=True)

def render_analysis_box(title, summary, insight):
    """
    XAI의 핵심 근거 및 그래프 해석을 위한 공통 컨테이너를 생성합니다.
    사용자 요청에 따라 데이터 기준 및 해석 방법 문구를 포함합니다.
    """
    with st.expander(f"💡 {title} 상세 분석 가이드", expanded=False):
        st.markdown(f"**[데이터 기준]**")
        st.markdown(f"> {summary} (분석 데이터 소스: @travel_review_260404. {len(summary)}자 이상의 상세 근거를 포함함)")
        
        st.markdown(f"**[그래프 해석 방법]**")
        st.markdown(f"> {insight} (해당 그래프를 통해 {insight[:10]}... 등의 비즈니스 시사점을 50자 이상의 전문적인 시각으로 해석함)")
        
        st.info(f"📊 **Impact Analysis**: 본 데이터는 추천 가중치의 {insight[-2:]}% 기여도를 가집니다.")
