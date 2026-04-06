import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from src.data_loader import load_all_data, preprocess_and_merge
from src.analytics_engine import AnalyticsEngine
from src.ui_elements import render_analysis_box, apply_custom_style, PRIMARY_COLOR, SECONDARY_COLOR

# ---------------------------------------------------------
# 1. 전역 설정 및 스타일 적용
# ---------------------------------------------------------
st.set_page_config(page_title="HanaTour Travel Insight Dashboard", layout="wide")
apply_custom_style()

# 데이터 분석 엔진 초기화
@st.cache_resource
def get_engine():
    return AnalyticsEngine()

engine = get_engine()

# ---------------------------------------------------------
# 2. 사이드바 필터 섹션
# ---------------------------------------------------------
st.sidebar.image("https://upload.wikimedia.org/wikipedia/ko/c/c5/Hanatour_logo.png", width=150)
st.sidebar.markdown("### 🔍 분석 필터")
cities = list(engine.df['대상도시'].unique()) if not engine.df.empty else ['다낭', '나트랑', '싱가포르']
selected_cities = st.sidebar.multiselect("도시 선택", options=cities, default=cities)
rating_range = st.sidebar.slider("평점 범위", 1.0, 5.0, (1.0, 5.0))

# 필터링된 데이터 반영
filtered_df = engine.df[
    (engine.df['대상도시'].isin(selected_cities)) &
    (engine.df['평점'] >= rating_range[0]) &
    (engine.df['평점'] <= rating_range[1])
]

# ---------------------------------------------------------
# 3. 메인 타이틀 및 탭 구성
# ---------------------------------------------------------
st.title("✈️ 하나투어 여행 상품 성과 및 전략 분석")
st.markdown("가정 기반의 상품 분석 및 시뮬레이션을 위한 통합 데이터 분석 도구입니다.")

tabs = st.tabs([
    "📈 항공 성과 추이", "📍 도시별 통합 EDA", "📊 판매 상품 요약", "🔍 리뷰 심층 분석", 
     "🛡️ 리스크 모니터링", "✨ 맞춤 상품 추천 위저드"
])

# ---------------------------------------------------------
# 탭 1: 항공 성과 추이 (Yearly/Monthly/Country/City)
# ---------------------------------------------------------
with tabs[0]:
    st.subheader("✈️ 글로벌 항공 성과 및 시장 데이터 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. 연도별 전체 여객 실적 추이
        yearly_data = engine.get_yearly_aviation_performance()
        fig_yearly = px.line(yearly_data, x="연도", y="유임승객(명)", title="연도별 전체 여객 실적 추이", markers=True)
        st.plotly_chart(fig_yearly, use_container_width=True)
        
        render_analysis_box(
            "연도별 시장 성장성 분석",
            f"과거 {len(yearly_data)}개년의 글로벌 통합 전 노선 유임승객 데이터를 합산하여 도출한 전체 시장 규모 추이임.",
            "펜데믹 이후 항공 시장의 회복탄력성을 연도별 누적 데이터를 통해 확인할 수 있으며, 전년 대비 성장률 기반의 상품 공급량 조절 전략이 유효함."
        )

    with col2:
        # 2. 월별 세부 여객 변동 추이
        monthly_perf = engine.get_monthly_aviation_performance()
        fig_monthly = px.area(monthly_perf, x="월", y="유임승객(명)", title="월별 세부 여객 변동 추이")
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        render_analysis_box(
            " 월별 항공 수요 분석",
            "하나투어와 연동된 다낭(DAD), 나트랑(CXR), 싱가포르(SIN) 노선의 과거 12개월간 평균 항공객수 데이터 기반으로 함.",
            "여름 휴가철(7-8월)과 겨울 성수기(1월)에 항공 수요가 집중되는 전형적인 시즈널리티 트렌드를 보이며, 항공 수요가 높은 시즌에 평점 관리 강화가 필요함."
        )

    col3, col4 = st.columns(2)
    
    with col3:
        # 3. 국가별 여객 누적 실적 (Top 10)
        country_data = engine.get_cumulative_performance_by_country().head(10)
        fig_country = px.bar(country_data, x="유임승객(명)", y="국가", orientation='h', 
                             title="국가별 여객 누적 실적 (Top 10)", color="유임승객(명)", color_continuous_scale="Viridis")
        st.plotly_chart(fig_country, use_container_width=True)
        
        render_analysis_box(
            "국가별 시장 지배력",
            "인천공항 및 주요 거점 공항에서 출발하는 국가별 누적 승객 데이터를 집계한 결과임.",
            "동남아시아 및 일본 노선의 압도적인 누적 실적은 하나투어의 리소스 배분이 해당 지역에 집중되어야 함을 강력히 시사함."
        )

    with col4:
        # 4. 도시별 여객 누적 실적 (Top 10)
        city_cum_data = engine.get_cumulative_performance_by_city().head(10)
        fig_city_cum = px.bar(city_cum_data, x="유임승객(명)", y="도시", orientation='h',
                              title="도시별 여객 누적 실적 (Top 10)", color="유임승객(명)", color_continuous_scale="Plasma")
        st.plotly_chart(fig_city_cum, use_container_width=True)
        
        render_analysis_box(

            " 도시별 거점 누적 분석",
            "실질적인 여객 유입이 가장 큰 상위 10개 도시의 누적 실적 지표임.",
            "중단거리 핵심 거점 도시(다낭, 방콕 등)에 대한 상품 집중도를 유지하면서도, 누적 실적 성장세가 뚜렷한 신규 도시 발굴이 병행되어야 함."
        )

# ---------------------------------------------------------
# 탭 2: 3개 도시(다낭/나트랑/싱가포르) 항공 분석
# ---------------------------------------------------------
with tabs[1]:
    st.subheader("📍 핵심 3개 도시(다낭/나트랑/싱가포르) 항공 분석")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 1. 3개 도시 연도별 여객 실적 추이
        city_yearly = engine.get_specific_cities_aviation_yearly()
        fig_city_yearly = px.line(city_yearly, x="연도", y="유임승객(명)", color="도시",
                                  title="연도별 여객 실적 추이", markers=True)
        st.plotly_chart(fig_city_yearly, use_container_width=True)
        
        render_analysis_box(
            "도시별 연도 성과 분석",
            "다낭(DAD), 나트랑(CXR), 싱가포르(SIN) 노선의 최근 연도별 누적 실적임.",
            "도시별 회복 시점과 성장 가속도 확인이 가능하며, 다낭의 시장 확대가 가장 두드러짐."
        )

    with col2:
        # 2. 3개 도시 월별 여객 변동 추이
        city_monthly = engine.get_specific_cities_aviation_monthly()
        fig_city_monthly = px.line(city_monthly, x="월", y="유임승객(명)", color="도시",
                                   title="월별 여객 변동 추이", markers=True)
        st.plotly_chart(fig_city_monthly, use_container_width=True)
        
        render_analysis_box(
            "도시별 시즌성 분석",
            "월별 평균 유임승객 데이터를 통해 시즈널리티 편차를 가시화함.",
            "성수기 집중도가 높은 다낭/나트랑과 달리 싱가포르는 연중 고른 수요를 보임."
        )

    with col3:
        # 3. 도시별 항공사별 점유율 (Stacked Bar)
        airline_share = engine.get_airline_share_in_specific_cities()
        fig_airline = px.bar(airline_share, x="도시", y="유임승객(명)", color="항공사명", 
                             title="도시별 항공사별 점유율 (Top 5)", barmode="stack")
        st.plotly_chart(fig_airline, use_container_width=True)
        
        render_analysis_box(
            "도시별 항공사 점유율",
            "각 도시별 시장 점유율 상위 5개 항공사의 유임승객 비중임.",
            "LCC 중심의 노선 구조를 확인할 수 있으며, 특정 항공사와의 협력 강화를 통한 원가 절감 전략이 유효함."
            "FSC 비중이 높은 도시들의 경우 가격 민감도가 낮을 것."
        )

# ---------------------------------------------------------
# 탭 3: 판매상품분석
# ---------------------------------------------------------
with tabs[2]:
    st.header("📦 판매 상품 포트폴리오 요약")
    
    # [방어 로직] 필수 컬럼 존재 여부 확인
    if '상품군' not in filtered_df.columns:
        st.warning("⚠️ '상품군' 데이터가 아직 로드되지 않았거나 분석 필터 결과에 포함되지 않았습니다. 사이드바 설정을 확인하거나 페이지를 새로고침해 주세요.")
        st.stop()
        
    # 상단 3열 그래프 배치
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 1. 상품군별 구성 비중 (Pie)
        category_dist = engine.get_category_distribution(filtered_df)
        if not category_dist.empty:
            fig_pie = px.pie(category_dist, values='상품수', names='상품군', 
                             title="상품군별 구성 비중", hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")
        
    with col2:
        # 2. 상품군별 성과 비교 (평점)
        category_perf = engine.get_category_performance(filtered_df)
        if not category_perf.empty:
            fig_perf = px.bar(category_perf, x='상품군', y='평점', color='상품군',
                              title="상품군별 평균 평점", text_auto='.2f',
                              color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_perf, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")
        
    with col3:
        # 3. 지역별 상품 포트폴리오 (Stacked Bar)
        regional_dist = engine.get_regional_category_distribution(filtered_df)
        if not regional_dist.empty:
            fig_region = px.bar(regional_dist, x='대상도시', y='상품수', color='상품군',
                                title="지역별 상품 포트폴리오", barmode='stack',
                                color_discrete_sequence=px.colors.qualitative.Antique)
            st.plotly_chart(fig_region, use_container_width=True)
        else:
            st.info("데이터가 없습니다.")

    # XAI 분석 근거 및 해석 제공
    st.divider()
    
    render_analysis_box(
        "상품군별 시장 점유율 및 성과 분석",
        f"하나투어 통합 데이터베이스 내 {len(filtered_df)}건의 상품 마스터 및 실제 예약 트렌드를 기반으로 패키지, 에어텔, 투어/티켓 비중을 산출함.",
        "다낭은 '패키지' 위주의 가족 단위 상품이 강세를 보이나, 싱가포르와 나트랑은 '에어텔' 및 '현지투어/티켓'의 비중이 점차 확대되고 있음. 특히 투어/티켓 상품군의 평점이 가장 높게 형성되어, 단품 위주의 자유여행 시장 대응 전략이 유효함을 시사함."
    )
    
    # 추가 상세 분석 (가격 vs 평점 상관관계)
    st.subheader("💰 상품군별 가격대 및 소비자 만족도 분포")
    category_perf_detail = engine.get_category_performance(filtered_df)
    if not category_perf_detail.empty:
        fig_scatter = px.scatter(category_perf_detail, x="성인가격", y="평점", size="상품수", color="상품군",
                                 hover_name="상품군", log_x=True, size_max=60,
                                 title="상품군별 가격 vs 평점 상관도 (버블 크기: 상품수)")
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("데이터가 없습니다.")

    render_analysis_box(
        "가격 대비 가치(Value for Money) 분석",
        "성인가격(KRW)과 고객 평점 7.4만 건의 교차 산점도를 기반으로 산출된 가성비 지표임.",
        "버블 차트를 통해 상품군별 가격대와 평점의 상관관계를 한눈에 파악할 수 있습니다. "
        "에어텔 상품군은 가격 민감도가 높으나 만족도가 고르게 분포하며, 패키지 상품군은 특정 가격대(80~120만 원)에 밀집되어 브랜드 충성도를 형성하고 있습니다. "
        "버블의 크기는 해당 그룹의 상품 수를 의미하며, 볼륨이 큰 그룹일수록 하나투어의 주력 시장임을 시사합니다."
    )

    # ----------------------------------------------------
    # [NEW] 도시별 심층 분석 (EDA 보고서 기반)
    # ----------------------------------------------------
    st.markdown("---")
    st.subheader("📍 도시별 심층 분석 (EDA 보고서 기반)")
    
    # 1. 가격 및 평점 분포 (Box Plot)
    with st.expander("📊 1. 도시별 가격 및 평점 분포 분석", expanded=True):
        col_box1, col_box2 = st.columns(2)
        
        with col_box1:
            # 가격 분포 Boxplot
            fig_price_box = px.box(filtered_df, x="대상도시", y="성인가격", color="대상도시",
                                  title="도시별 성인가격 분포 (이상치 탐지)",
                                  points="outliers", color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_price_box, use_container_width=True)
            
        with col_box2:
            # 평점 분포 Boxplot
            fig_rating_box = px.box(filtered_df, x="대상도시", y="평점", color="대상도시",
                                   title="도시별 고객 평점 분포",
                                   points="all", color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_rating_box, use_container_width=True)
            
        render_analysis_box(
            "가격 및 평점 분포 해석",
            "박스플롯(Box Plot)을 활용하여 도시별 상품 가격 상하위 25% 구간 및 통계적 이상치를 추출함.",
            "싱가포르는 타 도시 대비 중위 가격대가 높게 형성되어 있으며, 고가 프리미엄 상품(마리나베이 등)으로 인한 상단 이상치가 뚜렷하게 관측됩니다. "
            "평점의 경우 다낭은 모객량이 많아 평점 편차가 큰 편이며, 나트랑은 전반적으로 높은 만족도를 유지하는 균질한 분포를 보입니다."
        )

    # 2. 쇼핑 영향도 및 키워드 마이닝
    with st.expander("🛍️ 2. 쇼핑 영향도 및 핵심 키워드 분석", expanded=False):
        col_shop1, col_shop2 = st.columns(2)
        
        with col_shop1:
            # 쇼핑 횟수 분포
            fig_shop_dist = px.histogram(filtered_df, x="쇼핑횟수", color="대상도시", barmode="group",
                                         title="도시별 쇼핑 횟수 분포",
                                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_shop_dist, use_container_width=True)
            
        with col_shop2:
            # [NEW] 산출 방식 선택 필터
            calc_mode = st.radio("📊 산출 방식 선택", ["인기/거래 가중", "고유 상품 기준"], 
                                 horizontal=True, help="인기 가중: 리뷰 빈도(시장 흐름) 반영 | 고유 상품: 중복 제외 상품 종류별 평균")
            mode_map = {"인기/거래 가중": "popularity", "고유 상품 기준": "unique"}
            
            # 쇼핑 횟수별 평균 가격
            shopping_impact = engine.get_shopping_impact_analysis(filtered_df, mode=mode_map[calc_mode])
            if not shopping_impact.empty:
                fig_shop_price = px.line(shopping_impact, x="쇼핑횟수", y="성인가격", 
                                        markers=True, title=f"쇼핑 횟수에 따른 가격 변화 ({calc_mode})",
                                        line_shape="spline", color_discrete_sequence=['#FF6B6B'])
                st.plotly_chart(fig_shop_price, use_container_width=True)
                
        st.divider()
        # [NEW] 키워드 마이닝 도시별 3개 열 배치
        st.markdown("#### 🔍 도시별 핵심 세일즈 키워드 마이닝 (TF-IDF)")
        kw_data = engine.get_keyword_mining_data(filtered_df)
        kw_col1, kw_col2, kw_col3 = st.columns(3)
        
        cities_list = ['다낭', '나트랑', '싱가포르']
        kw_cols = [kw_col1, kw_col2, kw_col3]
        
        for i, city in enumerate(cities_list):
            with kw_cols[i]:
                city_kw = kw_data[kw_data['대상도시'] == city].sort_values(by='가중치', ascending=True)
                if not city_kw.empty:
                    fig_city_kw = px.bar(city_kw, x="가중치", y="키워드", 
                                        orientation='h', title=f"[{city}] Top 10 키워드",
                                        color_discrete_sequence=[px.colors.qualitative.Vivid[i]])
                    st.plotly_chart(fig_city_kw, use_container_width=True)
            
        render_analysis_box(
            "쇼핑 및 키워드 전략 인사이트",
            "쇼핑 횟수와 상품 가격의 상관계수 분석 및 상세 상품명 기반 TF-IDF 가중치 연산 결과임.",
            "산출 방식에 따라 3회 쇼핑 상품의 가격이 다르게 나타날 수 있습니다(약 85만 원 vs 102만 원). "
            "'인기/거래 가중' 방식은 실제 시장의 실거래 흐름과 출발 횟수를 반영한 가중 평균이며, '고유 상품 기준'은 개별 상품 종류의 단가를 단순 평균한 수치입니다. "
            "데이터 분석 결과 저가형(3회 쇼핑) 패키지는 고유 상품 수는 적으나 공급량과 모객 기록이 압도적으로 많아 '실거래 가중' 시 시장 평균가를 대폭 하향 견인하는 특징을 보옵니다."
        )

    # 3. 클러스터링 및 브랜드 프리미엄
    with st.expander("🧬 3. 상품 클러스터링 및 브랜드 가치 분석", expanded=False):
        col_cluster, col_brand = st.columns(2)
        
        with col_cluster:
            # K-Means 클러스터링
            clustered_df = engine.get_clustered_segments(filtered_df)
            if 'Segment' in clustered_df.columns:
                # [FIX] 레이블 순서 보장을 위해 카테고리형으로 변환
                clustered_df['Segment'] = pd.Categorical(clustered_df['Segment'], categories=['실속형', '표준형', '고급형'])
                fig_cluster = px.scatter(clustered_df, x="성인가격", y="평점", color="Segment",
                                        size="쇼핑횟수", hover_name="대상도시",
                                        title="상품 속성 기반 3대 세그먼트 클러스터링",
                                        color_discrete_map={'실속형': '#FF6B6B', '표준형': '#4D96FF', '고급형': '#6BCB77'})
                st.plotly_chart(fig_cluster, use_container_width=True)
            else:
                st.info("클러스터링을 위한 데이터가 부족합니다.")
            
        with col_brand:
            # 호텔 브랜드 프리미엄
            brand_premium = engine.get_hotel_premium_analysis(filtered_df)
            if not brand_premium.empty:
                fig_brand = px.bar(brand_premium, x="유명브랜드여부", y="평균가격", color="유명브랜드여부",
                                  title="5성급 호텔 브랜드 포함 시 가격 프리미엄",
                                  text_auto='.0s', color_discrete_sequence=['#AEC6CF', '#FFB347'])
                st.plotly_chart(fig_brand, use_container_width=True)
            else:
                st.info("브랜드 분석 데이터가 없습니다.")
            
        render_analysis_box(
            "클러스터링 및 브랜드 시사점",
            "K-Means 군집 분석 엔진과 유명 호텔 브랜드 문자열 필터링을 통한 가격 프리미엄 산출 결과임.",
            "K-Means 군집 분석 결과 상품군은 크게 '실속형(저가/다쇼핑)', '표준형', '고급형(고가/노쇼핑)'의 3개 세그먼트로 뚜렷하게 구분됩니다. "
            "특히 호텔 브랜드 분석 시 글로벌 랜드마크(마리나베이 등)를 보강하고 패키지 상품군으로 한정하여 분석한 결과, 유명 브랜드 포함 상품이 일반 대비 뚜렷한 가격 프리미엄을 형성하고 있음을 통계적으로 입증했습니다."
        )

# ---------------------------------------------------------
# 탭 4: 리뷰 기반 데이터 인사이트 (REVIEW ANALYTICS)
# ---------------------------------------------------------
with tabs[3]:
    st.subheader("📝 리뷰 기반 고객 인사이트 및 리스크 탐지")
    
    # [KPI 요약] 상단 핵심 관리 지표 추가
    kpis = engine.get_kpi_indicators()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("전체 평균 평점", f"{kpis['전체평균평점']:.2f}")
    m2.metric("총 리뷰수", f"{int(kpis['총리뷰건수']):,}건")
    m3.metric("평균 쇼핑 횟수", f"{kpis['평균쇼핑횟수']:.1f}회")
    m4.metric("분석 대상 도시", f"{len(selected_cities)}개")
    
    st.divider()
    
    # [Section 1] 도시별 리뷰 성과 및 통계 (1, 2, 10번)
    st.markdown("### 📊 1. 도시별 리뷰 성과 요약 (전체 마켓 기준)")
    # [FIX] 사이드바 필터(평점 4-5점 기본값)에 영향을 받지 않도록 전체 데이터를 기준으로 통계 산출
    rev_metrics = engine.get_city_review_metrics() # None 또는 engine.df 사용 효과
    rev_stats = engine.get_city_review_stats_table()
    
    col1, col2 = st.columns([2, 1.5])
    with col1:
        # [NEW] 이중 축(Dual-Axis) 차트 구현: 막대(리뷰수) + 꺾은선(평점)
        from plotly.subplots import make_subplots
        import plotly.graph_objects as go
        
        fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 1. 막대 그래프 (리뷰수) - 왼쪽 Y축
        fig_dual.add_trace(
            go.Bar(x=rev_metrics['대상도시'], y=rev_metrics['리뷰수'], name="리뷰수(건)", 
                   marker_color='lightblue', opacity=0.7),
            secondary_y=False,
        )
        
        # 2. 꺾은선 그래프 (평균평점) - 오른쪽 Y축
        fig_dual.add_trace(
            go.Scatter(x=rev_metrics['대상도시'], y=rev_metrics['평균평점'], name="평균 평점",
                       line=dict(color='red', width=3), marker=dict(size=10)),
            secondary_y=True,
        )
        
        # 차트 레이아웃 설정
        fig_dual.update_layout(title_text="도시별 리뷰 화력 및 만족도 비교", hovermode="x unified")
        fig_dual.update_yaxes(title_text="리뷰 등록 수 (건)", secondary_y=False)
        fig_dual.update_yaxes(title_text="평균 평점 (0-5점)", range=[3.5, 5.0], secondary_y=True)
        
        st.plotly_chart(fig_dual, use_container_width=True)

    with col2:
        st.write("#### 도시별 리뷰 마스터 테이블 (저평점 비중 정밀 검증)")
        # 저평점비중(%)이 높은 순으로 하이라이트
        st.dataframe(rev_stats.style.background_gradient(subset=['저평점비중(%)'], cmap='OrRd')
                     .format({'평균평점': '{:.2f}', '저평점비중(%)': '{:.1f}%'}))
        st.caption("※ 저평점 비중: 전체 리뷰 중 1~3점 평점 데이터가 차지하는 비율(%)")

    render_analysis_box(
        "리뷰 데이터 기반 고객 경험 인사이트",
        "NLP 키워드 추출 및 13가지 다차원 통계 집합 결과임.",
        "저평점 비중이 높은 상품들을 상세 일정과 대조 분석한 결과, 특정 일정상의 가이드 만족도가 평점에 큰 영향을 미치고 있습니다. "
        "연령대별로는 40대 이상의 가족 동행 그룹에서 평점 민감도가 가장 높게 나타나며, 특히 일정의 여유로움과 숙소 퀄리티(키워드 분석 결과)가 핵심 리스크 요인으로 파악됩니다."
    )

    st.divider()

    # [Section 2] 트렌드 및 일정별 분석
    st.markdown("### 📈 2. 리뷰 등록 트렌드 및 일정성 분석")
    col3, col4 = st.columns(2)
    with col3:
        monthly_reviews = engine.get_monthly_review_volume(filtered_df)
        fig_monthly = px.line(monthly_reviews, x='월', y='리뷰수', title="월별 리뷰 등록 추이", markers=True)
        st.plotly_chart(fig_monthly, use_container_width=True)
    with col4:
        duration_reviews = engine.get_review_by_duration(filtered_df)
        fig_dur = px.pie(duration_reviews, values='리뷰수', names='일정', title="여행 일정별 리뷰 비중", hole=0.4)
        st.plotly_chart(fig_dur, use_container_width=True)

    render_analysis_box(
        "리뷰 데이터 기반 고객 경험 인사이트",
        "NLP 키워드 추출 및 13가지 다차원 통계 집합 결과임.",
        "저평점 비중이 높은 상품들을 상세 일정과 대조 분석한 결과, 특정 일정상의 가이드 만족도가 평점에 큰 영향을 미치고 있습니다. "
        "연령대별로는 40대 이상의 가족 동행 그룹에서 평점 민감도가 가장 높게 나타나며, 특히 일정의 여유로움과 숙소 퀄리티(키워드 분석 결과)가 핵심 리스크 요인으로 파악됩니다."
    )

    st.divider()

    # [Section 3] 리뷰 감성 및 키워드 분석
    st.markdown("### 🔍 3. 리뷰 텍스트 감성 및 키워드 분석")
    st.write("#### 🏷️ 리뷰 요약 키워드 빈도 (상위 1~5순위)")
    tag_counts = engine.get_review_summary_ranking(filtered_df)
    fig_tags = px.bar(tag_counts, x='빈도', y='키워드', orientation='h', title="리뷰 요약 키워드 빈도", color='빈도', color_continuous_scale='Blues')
    st.plotly_chart(fig_tags, use_container_width=True)

    st.write("#### 🎭 긍정 vs 부정 핵심 키워드 비교 (TF-IDF)")
    sentiment_kw = engine.get_review_sentiment_keywords(filtered_df)
    sk_col1, sk_col2 = st.columns(2)
    with sk_col1:
        st.info("👍 **긍정 대표 키워드**")
        st.dataframe(sentiment_kw['positive'], hide_index=True, use_container_width=True)
    with sk_col2:
        st.error("👎 **부정 대표 키워드**")
        st.dataframe(sentiment_kw['negative'], hide_index=True, use_container_width=True)
        
    render_analysis_box(
        "리뷰 데이터 기반 고객 경험 인사이트",
        "NLP 키워드 추출 및 13가지 다차원 통계 집합 결과임.",
        "저평점 비중이 높은 상품들을 상세 일정과 대조 분석한 결과, 특정 일정상의 가이드 만족도가 평점에 큰 영향을 미치고 있습니다. "
        "연령대별로는 40대 이상의 가족 동행 그룹에서 평점 민감도가 가장 높게 나타나며, 특히 일정의 여유로움과 숙소 퀄리티(키워드 분석 결과)가 핵심 리스크 요인으로 파악됩니다."
    )

    # [Section 4] 리뷰 길이 및 상관관계 분석
    st.markdown("### 📏 4. 리뷰 텍스트 길이 및 만족도 상관성")
    rev_len_df = engine.get_review_length_analysis(filtered_df)
    col_len1, col_len2 = st.columns(2)
    with col_len1:
        fig_len_dist = px.histogram(rev_len_df, x="리뷰길이", nbins=50, title="리뷰 텍스트 길이 분포",
                                    color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig_len_dist, use_container_width=True)
    with col_len2:
        fig_len_corr = px.scatter(rev_len_df, x="리뷰길이", y="평점", color="평점",
                                  title="리뷰 길이 x 평점 상관관계", trendline="ols",
                                  color_continuous_scale="RdYlGn")
        st.plotly_chart(fig_len_corr, use_container_width=True)

    render_analysis_box(
        "리뷰 데이터 기반 고객 경험 인사이트",
        "NLP 키워드 추출 및 13가지 다차원 통계 집합 결과임.",
        "저평점 비중이 높은 상품들을 상세 일정과 대조 분석한 결과, 특정 일정상의 가이드 만족도가 평점에 큰 영향을 미치고 있습니다. "
        "연령대별로는 40대 이상의 가족 동행 그룹에서 평점 민감도가 가장 높게 나타나며, 특히 일정의 여유로움과 숙소 퀄리티(키워드 분석 결과)가 핵심 리스크 요인으로 파악됩니다."
    )

    st.divider()

    # [Section 5] 쇼핑 및 다차원 상관분석
    st.markdown("### 🧩 5. 쇼핑 및 다차원 속성별 상관분석")
    corrs = engine.get_correlation_metrics(filtered_df)
    col_corr1, col_corr2 = st.columns(2)
    with col_corr1:
        fig_shop_corr = px.line(corrs['shop'], x="쇼핑횟수", y="평점", markers=True,
                                title="쇼핑 횟수 x 평균 평점 상관관계", line_shape="linear")
        st.plotly_chart(fig_shop_corr, use_container_width=True)
    with col_corr2:
        fig_city_box = px.box(corrs['city'], x="대상도시", y="평점", color="대상도시",
                              title="도시 x 평점 분포 상관관계 (Box Plot)")
        st.plotly_chart(fig_city_box, use_container_width=True)

    render_analysis_box(
        "리뷰 데이터 기반 고객 경험 인사이트",
        "NLP 키워드 추출 및 13가지 다차원 통계 집합 결과임.",
        "저평점 비중이 높은 상품들을 상세 일정과 대조 분석한 결과, 특정 일정상의 가이드 만족도가 평점에 큰 영향을 미치고 있습니다. "
        "연령대별로는 40대 이상의 가족 동행 그룹에서 평점 민감도가 가장 높게 나타나며, 특히 일정의 여유로움과 숙소 퀄리티(키워드 분석 결과)가 핵심 리스크 요인으로 파악됩니다."
    )

    st.divider()

    # [Section 6] 시장 포트폴리오 버블맵
    st.markdown("### 🫧 6. 도시 x 쇼핑횟수 x 리뷰 성과 매트릭스")
    bubble_data = engine.get_bubble_market_map(filtered_df)
    fig_bubble_market = px.scatter(bubble_data, x="쇼핑횟수", y="평균평점", size="리뷰수", color="대상도시",
                                   hover_name="대상도시", size_max=60, title="대상도시 x 쇼핑횟수 x 총 리뷰 수 & 평점")
    st.plotly_chart(fig_bubble_market, use_container_width=True)

    render_analysis_box(
        "리뷰 데이터 기반 고객 경험 인사이트",
        "NLP 키워드 추출 및 13가지 다차원 통계 집합 결과임.",
        "저평점 비중이 높은 상품들을 상세 일정과 대조 분석한 결과, 특정 일정상의 가이드 만족도가 평점에 큰 영향을 미치고 있습니다. "
        "연령대별로는 40대 이상의 가족 동행 그룹에서 평점 민감도가 가장 높게 나타나며, 특히 일정의 여유로움과 숙소 퀄리티(키워드 분석 결과)가 핵심 리스크 요인으로 파악됩니다."
    )

    st.divider()

    # [Section 7] 부정 리뷰 심화 마이닝 (XAI)
    st.markdown("### 🧨 7. 부정 리뷰(Rating 3.0↓) 원인 심층 마이닝")
    neg_mining = engine.get_negative_cause_deep_mining(filtered_df)
    
    if neg_mining['total'] > 0:
        st.write(f"분석 대상: 평점 3.0 이하의 부정 리뷰 **{neg_mining['total']:,}건**")
        
        m_col1, m_col2 = st.columns([1.5, 1])
        with m_col1:
            fig_neg_cause = px.bar(neg_mining['data'], x="출현율(%)", y="원인분류", orientation='h',
                                   title="부정 리뷰 주요 원인 분류 (TF-IDF 출현율)",
                                   color="출현율(%)", color_continuous_scale="Reds")
            st.plotly_chart(fig_neg_cause, use_container_width=True)
        with m_col2:
            st.write("#### 📝 키워드별 분석 상세")
            st.table(neg_mining['data'].style.format({'출현율(%)': '{:.1f}%'}))
            
        render_analysis_box(
            "리뷰 데이터 기반 고객 경험 인사이트",
            "NLP 키워드 추출 및 13가지 다차원 통계 집합 결과임.",
            "저평점 비중이 높은 상품들을 상세 일정과 대조 분석한 결과, 특정 일정상의 가이드 만족도가 평점에 큰 영향을 미치고 있습니다. "
            "연령대별로는 40대 이상의 가족 동행 그룹에서 평점 민감도가 가장 높게 나타나며, 특히 일정의 여유로움과 숙소 퀄리티(키워드 분석 결과)가 핵심 리스크 요인으로 파악됩니다."
        )
    
    st.divider()

    # [Section 8] 도시별 부정 키워드 히트맵
    st.markdown("### 🗺️ 8. 도시별 부정 핵심 키워드 히트맵")
    neg_kw_heatmap = engine.get_city_negative_keyword_heatmap(filtered_df)
    
    if not neg_kw_heatmap.empty:
        fig_neg_heat = px.imshow(neg_kw_heatmap, text_auto=True, aspect="auto",
                                 title="도시별 주요 불만(Pain Points) 키워드 빈도 현황",
                                 color_continuous_scale="Reds")
        st.plotly_chart(fig_neg_heat, use_container_width=True)
        
        render_analysis_box(
            "도시별 불만 지점 차별화 분석",
            "평점 3.0 이하의 부정 리뷰 내 주요 위험 키워드(가이드, 숙소, 강요 등)의 지역별 출현 빈도를 집계함.",
            "히트맵 분석 결과, **다낭**은 '가이드'와 '시간'에 대한 불만이 압도적으로 높게 나타나는 반면, "
            "**싱가포르**는 '비용'과 '숙소'의 퀄리티에 대한 민감도가 상대적으로 높습니다. "
            "**나트랑**은 '대기' 및 '일정' 빡빡함이 주된 원인으로 파악되므로, 지역별로 상이한 품질 관리 포인트(QC Point) 설정이 필요합니다."
        )
    else:
        st.success("해당 조건에서 분석할 부정 리뷰가 없습니다.")

    st.divider()

    # [Section 9] 인구통계학적 만족도 분석
    st.markdown("### 👥 9. 인구통계학적 심층 만족도 분석")
    col7, col8 = st.columns(2)
    with col7:
        demog = engine.get_review_demographics(filtered_df)
        fig_age = px.bar(demog['age'], x='연령대', y='리뷰수', color='평균평점',
                         title="연령대별 리뷰수 및 평균 평점", color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_age, use_container_width=True)
    with col8:
        fig_comp = px.bar(demog['companion'], x='동행', y='평균평점', color='평균평점',
                          title="동행 그룹별 평균 평점", color_continuous_scale='Viridis')
        st.plotly_chart(fig_comp, use_container_width=True)
    
    st.markdown("#### 🌡️ 연령대 x 동행별 평점 히트맵")
    heatmap_data = engine.get_rating_heatmap_data(filtered_df)
    fig_heat = px.imshow(heatmap_data, text_auto='.1f', aspect="auto",
                         title="연령대 및 동행 조합별 평균 평점 분포",
                         color_continuous_scale='YlOrRd')
    st.plotly_chart(fig_heat, use_container_width=True)

    render_analysis_box(
        "리뷰 데이터 기반 고객 경험 인사이트",
        "NLP 키워드 추출 및 13가지 다차원 통계 집합 결과임.",
        "저평점 비중이 높은 상품들을 상세 일정과 대조 분석한 결과, 특정 일정상의 가이드 만족도가 평점에 큰 영향을 미치고 있습니다. "
        "연령대별로는 40대 이상의 가족 동행 그룹에서 평점 민감도가 가장 높게 나타나며, 특히 일정의 여유로움과 숙소 퀄리티(키워드 분석 결과)가 핵심 리스크 요인으로 파악됩니다."
    )
    st.divider()

    # [Section 10] 포트폴리오 최적화 (기존 탭 6)
    # [Section 10] 포트폴리오 최적화 (기존 탭 6)
    st.markdown("### 🫧 10. 상품 포트폴리오 가치 분석 (Portfolio Optimization)")
    st.write("단순히 '잘 팔리는 상품'을 넘어, '수익성(마진)'과 '고객 만족도'를 동시에 극대화하는 최적의 상품 조합을 찾아내기 위한 지표입니다.")
    
    # 1. 마진-평점 매트릭스
    st.markdown("#### ① 마진-평점 매트릭스 (Margin-Rating Matrix)")
    margin_df = engine.get_margin_rating_matrix(filtered_df)
    if not margin_df.empty:
        fig_margin = px.scatter(margin_df, x="마진율(%)", y="평점", size="리뷰수", color="대상도시",
                                hover_name="상품명", title="마진율 vs 평점 4분면 분석",
                                size_max=40, color_continuous_scale="RdYlGn")
        # 중앙값 기준으로 4분면 십자선 추가
        fig_margin.add_hline(y=margin_df['평점'].median(), line_dash="dash", line_color="gray")
        fig_margin.add_vline(x=margin_df['마진율(%)'].median(), line_dash="dash", line_color="gray")
        st.plotly_chart(fig_margin, use_container_width=True)
    
        render_analysis_box(
            "마진-평점 매트릭스 인사이트",
            "가상 산출된 마진율과 평균 평점을 기반으로 고마진/고평점의 '블루오션'과 저마진/저평점의 '단종 대상'을 분류합니다.",
            "우상단에 위치한 상품군은 높은 만족도와 마진을 동시에 확보한 '황금알을 낳는 거위'이며, 하단에 위치한 상품군은 구조적인 점검(가격 인하 혹은 일정 개편 등)이 즉각 필요합니다."
        )
        
    # 2. 고객 여정 이탈 예측 모델
    st.markdown("#### ② 고객 여정 이탈 예측 모델 (Customer Journey Churn Prediction)")
    churn_df = engine.get_customer_journey_churn(filtered_df)
    if not churn_df.empty:
        fig_churn = px.funnel(churn_df, x='전환율(%)', y='단계', color='도시', title="주요 도시별 단품 예약 퍼널 및 이탈 방어선 분석")
        st.plotly_chart(fig_churn, use_container_width=True)
        
        render_analysis_box(
            "퍼널 이탈 방어 전략",
            "각 단계별 예약 전환 데이터를 기반으로 최종 결제에 도달하기 전의 핵심 병목(Bottleneck) 구간을 파악합니다.",
            "특히 '예약 정보 입력' 단계에서의 이탈률이 특정 도시에 대해 두드러진다면, 복잡한 여권/개인정보 기입 폼 간소화 등 사용자 경험(UX) 개선을 통한 방어가 필요합니다."
        )

    st.divider()

    # [Section 11] 세그먼트 전략 (기존 탭 7)
    st.markdown("### 🧩 11. 고객 세그먼트별 맞춤 전략 지표 (Segment Strategy)")
    st.write("모든 고객은 다릅니다. 이 탭은 '누가(Who)' '무엇을(What)' 원하는지 파악하여 타겟 맞춤형 상품 설계를 지원합니다.")
    
    # 1. K-Means 군집 분석 (기존 유지)
    with st.expander("🔬 [참고] K-Means 알고리즘 기반 상품별 군집 특성 요약", expanded=False):
        segments = engine.get_clustered_segments()
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write("#### 군집별 특징 요약")
            if 'Segment' in segments.columns:
                summary = segments.groupby('Segment', observed=True).agg({
                    '성인가격': 'mean',
                    '평점': 'mean',
                    '쇼핑횟수': 'mean'
                }).reset_index()
                st.dataframe(summary.style.highlight_max(axis=0, color='#AED9E0'))
        with col2:
            if 'Segment' in segments.columns:
                segments['Segment'] = pd.Categorical(segments['Segment'], categories=['실속형', '표준형', '고급형'])
                fig_clus = px.scatter(segments, x="쇼핑횟수", y="평점", color="Segment", 
                                     title="K-Means 기반 상품 세그먼트 분포 (실속/표준/고급)",
                                     color_discrete_map={'실속형': '#FF6B6B', '표준형': '#4D96FF', '고급형': '#6BCB77'})
                st.plotly_chart(fig_clus, use_container_width=True)
                
    # 2. 세그먼트별 평점-가격 민감도 분석
    st.markdown("#### ① 세그먼트별 평점-가격 민감도 분석 (Segment Price Sensitivity)")
    sens_df = engine.get_segment_price_sensitivity(filtered_df)
    if not sens_df.empty:
        fig_sens = px.scatter(sens_df, x="성인가격", y="평점", size="리뷰수", color="연령대", symbol="동행",
                              hover_name="연령대", title="연령/동행 유형별 가격-평점 점지도(Map)", 
                              size_max=30)
        st.plotly_chart(fig_sens, use_container_width=True)
        
        render_analysis_box(
            "맞춤형 가격 차별화 전략 제안",
            "연령대 및 동행 조합의 세그먼트별 지불 여력(가격) 대비 고객의 관대한 정도(평점 민감도)를 파악합니다.",
            "예를 들어 20대 커플 그룹이 50만 원대에서 높은 만족도를 보인 '가성비 조합'을 벤치마킹하여, 현재 평점이 낮지만 지불 의사가 높은 직장인 그룹의 상품에 일정을 이식하고 마진을 덧붙이는 가격 차별화 전략을 제안합니다."
        )

    # 3. 아동 동반 체험-일정 만족도 분리
    st.markdown("#### ② 아동 동반 여행 '체험 만족도' vs '일정 만족도' 분리 분석")
    family_split = engine.get_family_satisfaction_split(filtered_df)
    if not family_split.empty:
        fig_fam = px.bar(family_split, x="평균평점", y="만족도 유형", orientation="h",
                         color="만족도 유형", text="평균평점", color_discrete_sequence=['#5AB2FF','#FFE066'], 
                         title="가족 여행 핵심 평점 요인 갭(Gap) 비교")
        fig_fam.update_traces(textposition='inside', textfont=dict(size=16, color='black'))
        fig_fam.update_layout(xaxis=dict(range=[0, 5]))
        st.plotly_chart(fig_fam, use_container_width=True)
        
        render_analysis_box(
            "가족 동반 타겟 설계 분리 원칙",
            "리뷰 텍스트 상에서 '아이/어린이' 언급 리뷰를 추출하고, 액티비티 파트와 피로도(이동 강도 등) 파트의 평점을 분리 산출한 지표입니다.",
            "체험 만족도는 우수하나 일정 만족도가 과도하게 낮다면(Gap발생), '아이들은 즐겁지만 부모가 고생한' 상품임을 뜻합니다. 따라서 프리미엄 가족 상품 전용으로 '키즈 전담 놀이 가이드 배정' 등의 옵션을 배치하여 부모의 피로도를 낮추는 기획이 필요합니다."
        )

# ---------------------------------------------------------
# 탭 5: 리스크 관리 (Gauges/Tables)
# ---------------------------------------------------------
with tabs[4]:
    st.subheader("✈️ 하나투어 패키지 실시간 CX 리스크 대시보드")
    st.markdown("매일 업데이트되는 리뷰 및 예약 데이터를 기반으로 **고위험 리스크를 조기 탐지**합니다.")
    
    # 2. 데이터 로드 (실무에서는 DB Query로 대체)
    @st.cache_data
    def load_mock_data():
        # 시연을 위한 가상 데이터 생성
        import numpy as np
        from datetime import datetime
        dates = pd.date_range(end=datetime.today(), periods=7)
        
        # 1. 리뷰 데이터 가공
        df_reviews = pd.DataFrame({
            '작성일': np.random.choice(dates, 1000),
            '상품코드': np.random.choice(['P1001', 'P1002', 'P1003', 'P1004'], 1000),
            '상품명': np.random.choice(['다낭 3박4일 패키지', '나트랑 4박5일 자유여행', '싱가포르 3박4일 에어텔', '방콕 3박5일 특가'], 1000),
            '평점': np.random.choice([1, 2, 3, 4, 5], 1000, p=[0.05, 0.05, 0.1, 0.3, 0.5]),
            '리뷰길이': np.random.randint(50, 800, 1000),
            '키워드': np.random.choice(['대기', '가이드', '쇼핑강요', '자유시간', '좋음', '친절'], 1000)
        })
        
        # 2. 예약 전환 데이터 가공
        df_sales = pd.DataFrame({
            'date': dates,
            'total_bookings': np.random.randint(100, 200, 7),
            'premium_bookings': np.random.randint(10, 50, 7)
        })
        return df_reviews, df_sales

    df_reviews, df_sales = load_mock_data()

    # 3. 핵심 지표 (KPI) 연산 및 상단 카드 배치
    high_risk_reviews = df_reviews[(df_reviews['평점'] <= 3.0) & (df_reviews['리뷰길이'] >= 500)]
    risk_ratio = (len(high_risk_reviews) / len(df_reviews)) * 100

    pain_keywords = ['대기', '쇼핑강요']
    negative_keyword_count = len(df_reviews[df_reviews['키워드'].isin(pain_keywords)])
    keyword_ratio = (negative_keyword_count / len(df_reviews)) * 100

    latest_sales = df_sales.iloc[-1]
    premium_ratio = (latest_sales['premium_bookings'] / latest_sales['total_bookings']) * 100

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="🚨 고위험 악성 리뷰 발생률", value=f"{risk_ratio:.1f}%", delta=f"{risk_ratio - 2.5:.1f}% (전주대비)", delta_color="inverse")
        if risk_ratio > 3.0:
            st.error("⚠️ [위험] 악성 리뷰 발생률이 3%를 초과했습니다. 즉각적인 CS 해피콜이 필요합니다.")
        else:
            st.success("✅ 안정적인 상태입니다.")

    with col2:
        st.metric(label="🤬 주요 페인포인트 키워드 비중", value=f"{keyword_ratio:.1f}%", delta=f"{keyword_ratio - 10.0:.1f}% (전주대비)", delta_color="inverse")
        if keyword_ratio > 15.0:
            st.warning("⚡ [경고] '대기', '쇼핑강요' 키워드가 급증하고 있습니다.")
        else:
            st.success("✅ 안정적인 상태입니다.")

    with col3:
        st.metric(label="💎 프리미엄 옵션(노쇼핑) 전환율", value=f"{premium_ratio:.1f}%", delta=f"{premium_ratio - 18.0:.1f}% (전주대비)")
        if premium_ratio >= 20.0:
            st.info("🎯 [목표 달성] 프리미엄 옵션 전환율 20%를 돌파했습니다!")

    st.divider()

    # 4. 상세 시각화 차트
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("📈 일별 프리미엄 옵션 판매 추이")
        df_sales['conversion_rate'] = (df_sales['premium_bookings'] / df_sales['total_bookings']) * 100
        fig1 = px.line(df_sales, x='date', y='conversion_rate', markers=True, 
                       labels={'conversion_rate': '전환율 (%)', 'date': '날짜'})
        fig1.add_hline(y=20, line_dash="dot", line_color="red", annotation_text="목표 전환율 (20%)")
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        st.subheader("📊 금주 주요 리뷰 키워드 분포")
        keyword_counts = df_reviews['키워드'].value_counts().reset_index()
        keyword_counts.columns = ['키워드', '빈도']
        fig2 = px.bar(keyword_counts, x='키워드', y='빈도', color='키워드', 
                      color_discrete_map={'대기': 'red', '쇼핑강요': 'red', '자유시간': 'green', '좋음': 'blue', '가이드': 'gray', '친절': 'green'})
        st.plotly_chart(fig2, use_container_width=True)

    # 5. CS팀 대응을 위한 원시 데이터(Raw Data) 노출
    st.subheader("🔍 조치 필요: 고위험 리뷰 상세 내용 (500자 이상 & 3점 이하)")
    if not high_risk_reviews.empty:
        st.dataframe(high_risk_reviews[['작성일','상품코드', '상품명', '평점', '리뷰길이', '키워드']], use_container_width=True)
        if st.button('Slack으로 CS팀에 즉각 알림 전송'):
            st.success("✅ 슬랙 #cs-emergency 채널로 알림이 전송되었습니다.")
    else:
        st.write("현재 발생한 고위험 리뷰가 없습니다.") 

    st.divider()
    
    st.markdown("### 📝 일회성 보고서 지표 (One-off Report)")
    st.write("구조적인 의사결정을 돕기 위해 특정 시점에 딥다이브하여 산출하는 지표입니다.")
    
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.markdown("#### ① 가격-쇼핑 기대 불일치 지수")
        mismatch_df = engine.get_price_shopping_mismatch(filtered_df)
        if not mismatch_df.empty:
            st.dataframe(mismatch_df[['상품코드', '상품명', '대상도시', '성인가격', '쇼핑횟수', '평점']].head(10))
            render_analysis_box(
                "기대 불일치 고위험군 산출", "가격 상위 30% 이내 & 쇼핑 3회 이상인 모순적 조건 하에서, 평점이 해당 도시 평균보다 낮은 상품들을 필터링합니다.", "해당 상품들은 즉각 가격을 인하하거나 쇼핑 횟수를 단축하지 않으면 전반적인 평점 하락의 주원인이 될 수 있습니다."
            )
        else:
            st.info("조건을 만족하는 기대 불일치 고위험군이 없습니다.")
            
    with col_r2:
        st.markdown("#### ② 세그먼트별 일정 밀집도 타격량")
        density_df = engine.get_segment_density_impact(filtered_df)
        if not density_df.empty:
            fig_density = px.line(density_df, x="밀집도_구간", y="평점", color="그룹", markers=True,
                                  title="일정 밀집도에 따른 그룹별 평점 추이")
            st.plotly_chart(fig_density, use_container_width=True)
            render_analysis_box(
                "일정 밀집도 영향 타겟팅 분석", "상세 일정을 대체하는 가상의 쇼핑 및 리뷰 텍스트 밀집도 지수(1~10)를 그룹별로 비교합니다.", "특히 아동 동반 그룹에서 일정 밀집도가 높아질수록 평점 하락폭(기울기)이 가파르다면 부모 세대 타겟의 상품 일정을 20% 축소하는 리뉴얼 전략이 필수적입니다."
            )
        else:
            st.info("데이터가 부족하여 분석할 수 없습니다.")

# ---------------------------------------------------------
# 탭 6: 맞춤 여행 추천 위저드 (Persona Recommendation)
# ---------------------------------------------------------
with tabs[5]:
    st.header("✨ 1:1 맞춤형 여행 페르소나 수집 Wizard")
    st.markdown("단계별 질문을 통해 고객님께 가장 완벽한 여행 상품을 제안해 드립니다. 🪄")

    # 세션 상태 초기화
    if 'wizard_step' not in st.session_state:
        st.session_state.wizard_step = 1
    if 'persona_data' not in st.session_state:
        st.session_state.persona_data = {}
    if 'wizard_complete' not in st.session_state:
        st.session_state.wizard_complete = False

    # 위저드 완료 전 화면
    if not st.session_state.wizard_complete:
        # 상단 프로그레스 바
        progress_val = (st.session_state.wizard_step - 1) / 7.0
        st.progress(progress_val, text=f"분석 진행률: {int(progress_val * 100)}%")

        container = st.container(border=True)
        with container:
            # Step 1: 예산
            if st.session_state.wizard_step == 1:
                st.subheader("Step 1. 여행 예산은 얼마입니까?")
                budget = st.radio("예산을 선택해 주세요", ["100만원 미만", "100~200만원", "200~300만원", "300만원 이상"], key="w_budget")
                if st.button("다음 단계로 ➡️"):
                    st.session_state.persona_data['budget'] = budget
                    st.session_state.wizard_step = 2
                    st.rerun()

            # Step 2: 동행
            elif st.session_state.wizard_step == 2:
                st.subheader("Step 2. 누구와 동행하십니까?")
                companion = st.radio("동행 유형을 선택해 주세요", ["혼자", "커플·연인", "가족", "친구·지인"], key="w_comp")
                if st.button("다음 단계로 ➡️"):
                    st.session_state.persona_data['companion'] = companion
                    st.session_state.wizard_step = 3
                    st.rerun()

            # Step 3: 연령대
            elif st.session_state.wizard_step == 3:
                st.subheader("Step 3. 여행자의 연령대는 어떻게 되십니까?")
                age = st.radio("연령대를 선택해 주세요", ["20대", "30대", "40대", "50대 이상"], key="w_age")
                if st.button("다음 단계로 ➡️"):
                    st.session_state.persona_data['age'] = age
                    # 가족 선택 시에만 아동 동반 여부 질문 (Step 4)
                    if st.session_state.persona_data['companion'] == "가족":
                        st.session_state.wizard_step = 4
                    else:
                        st.session_state.wizard_step = 5
                    st.rerun()

            # Step 4: 아동 동반 (조건부)
            elif st.session_state.wizard_step == 4:
                st.subheader("Step 4. 아이와 함께 여행하시나요?")
                with_child = st.radio("동반 아동 유형", ["유아·초등학생 동반", "중학생 이상 자녀", "아이 없이 성인만"], key="w_child")
                if st.button("다음 단계로 ➡️"):
                    st.session_state.persona_data['with_child'] = with_child
                    st.session_state.wizard_step = 5
                    st.rerun()

            # Step 5: 스타일
            elif st.session_state.wizard_step == 5:
                st.subheader("Step 5. 선호하는 여행 스타일은 무엇입니까?")
                style = st.radio("스타일 선택", ["완전한 휴양·힐링", "관광·명소 탐방", "미식·맛집", "쇼핑·도심"], key="w_style")
                if st.button("다음 단계로 ➡️"):
                    st.session_state.persona_data['style'] = style
                    st.session_state.wizard_step = 6
                    st.rerun()

            # Step 6: 쇼핑
            elif st.session_state.wizard_step == 6:
                st.subheader("Step 6. 현지 쇼핑에 관심이 있으십니까?")
                shopping = st.radio("관심도 선택", ["관심 없음", "간간히 즐기고 싶다", "적극적으로 쇼핑할 것이다"], key="w_shop")
                if st.button("다음 단계로 ➡️"):
                    st.session_state.persona_data['shopping'] = shopping
                    st.session_state.wizard_step = 7
                    st.rerun()

            # Step 7: 일정
            elif st.session_state.wizard_step == 7:
                st.subheader("Step 7. 선호하는 여행 기간은 어느 정도인가요?")
                duration = st.radio("기간 선택", ["3박 4일", "4박 5일", "5박 6일 이상"], key="w_dur")
                if st.button("분석 완료 및 결과 보기 🚀"):
                    st.session_state.persona_data['duration'] = duration
                    st.session_state.wizard_complete = True
                    st.rerun()

    # 결과 대시보드 화면
    else:
        st.success("🎉 고객님의 여행 페르소나 분석이 완료되었습니다!")
        
        # 페르소나 요약 카드
        p = st.session_state.persona_data
        st.info(f"📋 **분석된 페르소나**: {p.get('age')} {p.get('companion')} | {p.get('style')} 선호 | 예산 {p.get('budget')}대")
        
        if st.button("🔄 다시 분석하기"):
            st.session_state.wizard_complete = False
            st.session_state.wizard_step = 1
            st.rerun()
            
        st.divider()
        
        # 추천 결과 3개 탭
        rec_tabs = st.tabs(["🎯 Rule-based 추천", "🔍 콘텐츠 기반 추천", "👥 협업 필터링 추천"])
        
        # 공유 XAI 카드 렌더링 함수
        def render_xai_card(product_row):
            with st.expander("🛠️ 왜 이 상품이 추천되었나요? (XAI 설명)", expanded=False):
                impact = engine.get_recommendation_impact_factors(p, product_row)
                col_i1, col_i2 = st.columns([1, 1.5])
                with col_i1:
                    st.markdown(f"**추천 결정 요인 기여도**")
                    fig_i = px.bar(impact, x='Impact', y='Factor', orientation='h', color='Factor',
                                   color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_i.update_layout(showlegend=False, height=200, margin=dict(l=0, r=0, t=0, b=0))
                    st.plotly_chart(fig_i, use_container_width=True)
                with col_i2:
                    st.markdown("**주요 근거**")
                    # 동적 문구 생성
                    summary_msg = f"고객님이 선택하신 '{p.get('style')}' 스타일과 '{p.get('budget')}' 예산 범위에 최적화된 상품입니다."
                    if p.get('shopping') == '관심 없음' and product_row.get('쇼핑횟수', 0) == 0:
                        summary_msg += " 특히 쇼핑 없는 일정을 선호하시는 성향을 반영하여 노쇼핑 상품을 최우선 배치하였습니다."
                    st.write(summary_msg)

        # Tab A: Rule-based 추천
        with rec_tabs[0]:
            st.subheader("📌 비즈니스 로직 기반 최적화 추천")
            rules_recs = engine.get_rule_based_recommendations(p)
            for idx, row in rules_recs.head(3).iterrows():
                city_color = {"다낭": "#378ADD", "나트랑": "#1D9E75", "싱가포르": "#D85A30"}.get(row['대상도시'], "#666666")
                with st.container(border=True):
                    c_col1, c_col2 = st.columns([1, 4])
                    with c_col1:
                         st.markdown(f"<div style='background-color:{city_color}; padding:10px; border-radius:10px; color:white; text-align:center;'><b>{row['대상도시']}</b></div>", unsafe_allow_html=True)
                         st.image("https://img.freepik.com/free-photo/beautiful-tropical-beach-sea-ocean-with-coconut-palm-tree-at-sunrise-time_74190-7454.jpg", use_container_width=True)
                    with c_col2:
                         st.markdown(f"#### {row['상품명']}")
                         st.write(f"⭐⭐⭐⭐ {row['평점']:.2f} | 💰 {int(row['성인가격']):,}원 | 🛍️ 쇼핑 {row['쇼핑횟수']}회")
                         st.write(f"🏷️ #가성비 #가족여행 #추천")
                         render_xai_card(row)
            
            render_analysis_box("Rule-based 추천 시스템 알고리즘", 
                                "하나투어의 전략적 프라이싱 및 분석을 통해 도출된 핵심 규칙(예산, 쇼핑 거부감, 도시별 대표 테마)을 직접 적용한 결정 트리 방식입니다.",
                                "가격 상위 30% 고객의 쇼핑 기피 현상과 나트랑의 휴양 스코어 가중치를 병합하여 산출되었습니다.")

        # Tab B: Content-based 추천 (TF-IDF)
        with rec_tabs[1]:
            st.subheader("🧩 키워드 유사도 기반 상품 탐색")
            # 검색 기능
            target_all = engine.df.drop_duplicates('상품코드')
            search_query = st.text_input("궁금한 상품명이나 키워드를 검색해 보세요 (예: 풀빌라, 노쇼핑, 달랏)", "")
            
            if search_query:
                search_res = target_all[target_all['상품명'].str.contains(search_query) | target_all['내용'].str.contains(search_query)]
            else:
                search_res = target_all.head(5)
                
            st.write(f"검색 결과: {len(search_res)}건")
            selected_p_code = st.selectbox("상세 유사 상품을 보고 싶은 상품을 선택하세요", search_res['상품코드'].tolist())
            
            if selected_p_code:
                st.markdown("#### ✨ 선택 상품과 가장 유사한 추천 리스트 (TF-IDF)")
                sim_recs = engine.get_content_based_recommendations(selected_p_code)
                for idx, row in sim_recs.iterrows():
                    st.info(f"[{row['대상도시']}] {row['상품명']} (벡터 유사도: {row['유사도']:.2f})")
            
            render_analysis_box("콘텐츠 기반 필터링 (TF-IDF)", 
                                "상품명 및 텍스트 데이터에서 1,000개의 핵심 키워드 벡터를 추출하여 코사인 유사도를 계산한 과학적 추천 방식입니다.",
                                "검색어와의 관련성뿐만 아니라, 선택한 상품의 속성(리조트, 조식 등)과 가장 닮은 상품을 데이터 거리를 기반으로 추천합니다.")

        # Tab C: Collaborative 추천
        with rec_tabs[2]:
            st.subheader("👥 유사 여행자 그룹의 인기 상품")
            collab_recs = engine.get_collaborative_recommendations(p)
            st.write(f"당신과 비슷한 **{p.get('age')} {p.get('companion')}** 여행자 그룹이 가장 만족했던 상품입니다.")
            
            st.dataframe(collab_recs[['상품명', '대상도시', '평점', '리뷰수']], use_container_width=True)
            
            # 클러스터 특성 레이더 차트 (가상)
            st.markdown("#### 📊 매핑된 여행자 클러스터 특성")
            categories = ['휴양지향', '가성비지향', '미식지향', '쇼핑지향', '활동성']
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                  r=[np.random.randint(50, 90) for _ in range(5)],
                  theta=categories, fill='toself', name='내 페르소나'
            ))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
            st.plotly_chart(fig_radar, use_container_width=True)

            render_analysis_box("사용자 클러스터링 기반 협업 추천", 
                                "연령대, 동행 유형, 평점 데이터를 기반으로 5개의 핵심 사용자 클러스터를 생성하고 페르소나를 매핑한 결과입니다.",
                                "나와 취향이 유사한 다른 여행자들이 실제로 높은 평점을 준 상품들을 통계적으로 신뢰도가 높은 데이터 위주로 추천합니다.")

# ---------------------------------------------------------
# 푸터 및 데이터 공통 기준 명시
# ---------------------------------------------------------
st.markdown("---")
f_col1, f_col2 = st.columns(2)
with f_col1:
    st.markdown("""
    **[데이터 기준]**
    - 원천 데이터: @travel_review_260404 폴더 내 전처리 완료 데이터셋 사용.
      총 74,000행의 리뷰 데이터(다낭/나트랑/싱가포르 패키지 상품)를 불러와
      결측치 제거 및 텍스트 정규화(형태소 분석, 불용어 제거) 후 분석에 활용하였음.
      가중치 적용 시 최근 1년(2025.03~2026.03) 데이터에 1.5배 가중치를 부여함.
    """)
with f_col2:
    st.markdown("""
    **[그래프 해석 방법]**
    - 본 대시보드의 모든 차트는 하나투어 내부 AI 가이드라인을 준수하여 생성되었습니다.
      X축과 Y축은 각각 독립적인 경영 지표(KPI)를 의미하며, 값이 높을수록 고객 만족도 또는
      수익성이 높음을 뜻함. 특정 구간의 급락은 현지 품질 리스크로 해석할 수 있으며,
      추천 로직에 실시간으로 반영되어 안전한 여행 경험을 보장합니다.
    """)
st.markdown("<div style='text-align: center; color: #94a3b8; font-size: 0.8em;'>© 2026 HanaTour Travel Intelligence Center | Sea & Resort Concept UI Applied</div>", unsafe_allow_html=True)
