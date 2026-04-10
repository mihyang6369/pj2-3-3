"""
하나투어 대시보드 UI 구성 요소 모듈 (UI Elements)

이 모듈은 대시보드의 시각적 스타일(CSS)과 공통적으로 사용되는 
UI 컴포넌트(분석 박스, 메트릭 카드 등)를 정의합니다. 

주요 기능:
1. 브랜드 아이덴티티를 반영한 커스텀 CSS 스타일 적용
2. 데이터 근거와 해석을 포함하는 표준 분석 박스 렌더링
3. 사이드바 필터 및 핵심 KPI 메트릭 카드 생성
"""

import streamlit as st # 웹 UI 제작을 위한 기본 라이브러리
from typing import Optional, List, Any # 타입 힌팅을 위한 모듈

# 하나투어 대시보드 전용 색상 테마 정의 (브랜드 가이드라인 준수)
PRIMARY_COLOR = "#AED9E0"   # 부드러운 하늘색: 휴양지와 항공의 느낌을 전달
SECONDARY_COLOR = "#F5E6BE"  # 따뜻한 모래색: 해변과 모래사장의 따스함을 표현
TEXT_COLOR = "#2C3E50"       # 짙은 청회색: 가독성이 높고 신뢰감을 주는 텍스트 색상
CARD_BG = "#FFFFFF"          # 순백색: 깔끔한 카드 배경색

def apply_custom_style():
    """
    모던한 카드형 UI와 브랜드 전용 색상 테마를 대시보드 전체에 적용합니다.
    Streamlit의 기본 디자인을 HTML/CSS를 통해 커스텀화합니다.
    """
    st.markdown(f"""
        <style>
            /* 1. 메인 배경색 및 텍스트 기본 설정 */
            .main {{
                background-color: #F9FBFF; /* 눈이 편안한 밝은 블루톤 배경 */
                color: {TEXT_COLOR};
            }}
            
            /* 2. 카드 스타일 정의 (그림자 및 테두리 효과) */
            .metric-card {{
                background-color: {CARD_BG};
                padding: 1.5rem;
                border-radius: 15px; /* 둥근 모서리로 부드러운 인상 제공 */
                box-shadow: 0 4px 6px rgba(0,0,0,0.05); /* 은은한 그림자 효과 */
                border-left: 5px solid {PRIMARY_COLOR}; /* 좌측 강조선으로 시선 집중 */
                margin-bottom: 1rem;
            }}
            
            /* 3. 데이터 분석 레이블 스타일 (Data Basis & Interpretation) */
            .data-basis-label {{
                font-weight: bold;
                color: #5D6D7E;
                font-size: 0.85rem;
                margin-top: 0.5rem;
                text-transform: uppercase; /* 영문 레이블 대문자화 */
            }}
            
            .interpretation-label {{
                font-weight: bold;
                color: #1E8449; /* 통찰력(Insight)을 상징하는 초록색 계열 */
                font-size: 0.85rem;
                margin-top: 0.3rem;
            }}
            
            /* 4. 탭 메뉴 폰트 강화 */
            .stTabs [data-baseweb="tab"] {{
                font-weight: bold;
                color: {TEXT_COLOR};
            }}
        </style>
    """, unsafe_allow_html=True)

def render_analysis_box(title: str, basis: str, interpretation: str, extra: Optional[str] = None):
    """
    차트 하단에 위치하여 데이터의 근거와 분석 결과를 체계적으로 보여주는 박스를 렌더링합니다.
    
    Args:
        title (str): 분석 항목의 제목 (예: '연도별 성장성 분석')
        basis (str): 데이터의 출처 및 계산 근거 (Data Basis)
        interpretation (str): 데이터가 시사하는 핵심 결과 및 비즈니스 인사이트 (Interpretation)
        extra (str, optional): 추가적인 상세 정보나 제언 사항
    """
    # 추가 내용이 있는 경우, 기존 해석 텍스트 뒤에 두 줄 띄우고 합칩니다.
    full_interpretation = interpretation
    if extra:
        full_interpretation += f"\n\n{extra}"

    # HTML 템플릿을 사용하여 사전에 정의된 CSS 클래스(.metric-card 등)를 적용합니다.
    st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin-top:0; color: #34495E;">📊 {title}</h4>
            <div class="data-basis-label">📍 데이터 근거 (Data Basis)</div>
            <p style="font-size: 0.9rem; color: #5D6D7E; line-height: 1.6; white-space: pre-wrap;">{basis}</p>
            <div class="interpretation-label">💡 그래프 해석 (Interpretation)</div>
            <p style="font-size: 0.9rem; color: #2C3E50; line-height: 1.6; font-style: italic; white-space: pre-wrap;">{full_interpretation}</p>
        </div>
    """, unsafe_allow_html=True)

def render_xai_card(label: str, value: Any, delta: Optional[str] = None):
    """
    핵심 성과 지표(KPI)를 강조하여 표시하는 디자인 카드를 생성합니다.
    
    Args:
        label (str): 지표명 (예: '전체 평균 평점')
        value (Any): 실제 수치값 (예: 4.5)
        delta (str, optional): 전년 대비 변동량 등 보조 정보
    """
    with st.container():
        # HTML 태그로 카드의 시작을 알립니다.
        st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
        # Streamlit의 내장 metric 함수를 사용하여 수치를 렌더링합니다.
        st.metric(label=label, value=value, delta=delta)
        # HTML 태그로 카드를 닫습니다.
        st.markdown('</div>', unsafe_allow_html=True)

def display_sidebar_filters(cities: List[str]):
    """
    대시보드 좌측 사이드바에 사용자가 데이터를 조절할 수 있는 필터 위젯들을 배치합니다.
    
    Args:
        cities (List[str]): 필터에 표시할 도시 리스트 (예: ['다낭', '나트랑', '싱가포르'])
        
    Returns:
        Tuple: 사용자가 선택한 도시 리스트, 분석 기간(월), 최소 평점 기준값
    """
    # 하나투어 공식 로고를 상단에 배치합니다.
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/ko/c/c5/Hanatour_logo.png", width=150)
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 분석 필터")
    
    # 1. 대상 지역 선택 필터 (다중 선택 가능)
    selected_city = st.sidebar.multiselect("대상 지역 선택", options=cities, default=cities)
    
    # 2. 분석 기간 선택 슬라이더 (1월~12월 범위)
    selected_period = st.sidebar.slider("분석 기간(월)", 1, 12, (1, 12))
    
    # 3. 최소 만족도 선택 박스 (4점을 기본값으로 설정하여 우량 상품 위주 분석 유도)
    min_rating = st.sidebar.selectbox("최소 만족도(평점)", options=[1, 2, 3, 4, 5], index=3)
    
    return selected_city, selected_period, min_rating
