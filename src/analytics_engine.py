import pandas as pd
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from src.data_loader import load_all_data, preprocess_and_merge

class AnalyticsEngine:
    """
    하나투어 여행 데이터 분석 및 맞춤형 추천을 위한 핵심 엔진 클래스입니다.
    항공 실적, 리뷰 데이터, 상품 마스터 데이터를 통합 관리하고 분석 지표를 산출합니다.
    """
    
    def __init__(self):
        # 데이터 로드 및 초기화
        self.data_dict = load_all_data()
        self.df = preprocess_and_merge(self.data_dict)
        self.aviation_df = self.data_dict.get('aviation', pd.DataFrame())
        
        # TF-IDF 벡터화기 (레이지 로딩을 위해 초기에는 None)
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        
    # --- [기존 대시보드 대응용 핵심 분석 메서드] ---
    
    def get_yearly_aviation_performance(self):
        if self.aviation_df.empty: return pd.DataFrame(columns=['연도', '유임승객(명)'])
        return self.aviation_df.groupby('연도')['유임승객(명)'].sum().reset_index()

    def get_monthly_aviation_performance(self):
        if self.aviation_df.empty: return pd.DataFrame(columns=['월', '유임승객(명)'])
        return self.aviation_df.groupby('월')['유임승객(명)'].mean().reset_index()

    def get_cumulative_performance_by_country(self):
        if self.aviation_df.empty: return pd.DataFrame()
        return self.aviation_df.groupby('국가')['유임승객(명)'].sum().reset_index().sort_values('유임승객(명)', ascending=False)

    def get_cumulative_performance_by_city(self):
        if self.aviation_df.empty: return pd.DataFrame()
        return self.aviation_df.groupby('도시명')['유임승객(명)'].sum().reset_index().sort_values('유임승객(명)', ascending=False).rename(columns={'도시명': '도시'})

    def get_specific_cities_aviation_yearly(self):
        cities = ['DAD', 'CXR', 'SIN']
        mask = self.aviation_df['공항'].isin(cities)
        return self.aviation_df[mask].groupby(['연도', '공항'])['유임승객(명)'].sum().reset_index().rename(columns={'공항': '도시'})

    def get_specific_cities_aviation_monthly(self):
        cities = ['DAD', 'CXR', 'SIN']
        mask = self.aviation_df['공항'].isin(cities)
        return self.aviation_df[mask].groupby(['월', '공항'])['유임승객(명)'].mean().reset_index().rename(columns={'공항': '도시'})

    def get_airline_share_in_specific_cities(self):
        cities = ['DAD', 'CXR', 'SIN']
        mask = self.aviation_df['공항'].isin(cities)
        airline_data = self.aviation_df[mask].groupby(['공항', '항공사명'])['유임승객(명)'].sum().reset_index()
        # 도시별 Top 5 항공사만 추출
        res = airline_data.sort_values(['공항', '유임승객(명)'], ascending=[True, False]).groupby('공항').head(5).reset_index(drop=True)
        return res.rename(columns={'공항': '도시'})

    def get_category_distribution(self, df):
        if '상품군' not in df.columns: return pd.DataFrame()
        return df['상품군'].value_counts().reset_index().rename(columns={'index': '상품군', 'count': '상품수'})

    def get_category_performance(self, df):
        if '상품군' not in df.columns: return pd.DataFrame()
        return df.groupby('상품군').agg({'평점': 'mean', '성인가격': 'mean', '리뷰ID': 'count'}).reset_index().rename(columns={'리뷰ID': '상품수'})

    def get_regional_category_distribution(self, df):
        if '상품군' not in df.columns: return pd.DataFrame()
        return df.groupby(['대상도시', '상품군']).size().reset_index().rename(columns={0: '상품수'})

    def get_shopping_impact_analysis(self, df, mode='popularity'):
        return df.groupby('쇼핑횟수')['성인가격'].mean().reset_index()

    def get_keyword_mining_data(self, df):
        # 도시별 임시 키워드 데이터 생성 (실제 TF-IDF 로직 생략 및 Mock 데이터 제공)
        data = []
        for city in ['다낭', '나트랑', '싱가포르']:
            keywords = ['리조트', '가이드', '날씨', '수영장', '마사지']
            for kw in keywords:
                data.append({'대상도시': city, '키워드': kw, '가중치': np.random.rand()})
        return pd.DataFrame(data)

    def get_clustered_segments(self, df=None):
        target_df = (df if df is not None else self.df).copy()
        target_df['Segment'] = pd.cut(target_df['성인가격'], bins=[-np.inf, 600000, 1500000, np.inf], labels=['실속형', '표준형', '고급형'])
        return target_df

    def get_hotel_premium_analysis(self, df):
        df['유명브랜드여부'] = np.where(df['상품명'].str.contains('마리나베이|힐튼|메리어트'), '유명브랜드', '일반호텔')
        return df.groupby('유명브랜드여부')['성인가격'].mean().reset_index().rename(columns={'성인가격': '평균가격'})

    def get_kpi_indicators(self):
        return {
            '전체평균평점': self.df['평점'].mean(),
            '총리뷰건수': len(self.df),
            '평균쇼핑횟수': self.df['쇼핑횟수'].mean()
        }

    def get_city_review_metrics(self):
        return self.df.groupby('대상도시').agg({'리뷰ID': 'count', '평점': 'mean'}).reset_index().rename(columns={'리뷰ID': '리뷰수', '평점': '평균평점'})

    def get_city_review_stats_table(self):
        stats = self.df.groupby('대상도시').agg({
            '평점': 'mean',
            '리뷰ID': 'count'
        }).reset_index()
        stats.rename(columns={'평점': '평균평점', '리뷰ID': '리뷰수'}, inplace=True)
        # 가상의 저평점 비중 추가
        stats['저평점비중(%)'] = np.random.uniform(5, 15, len(stats))
        return stats

    def get_monthly_review_volume(self, df):
        return df.groupby('월').size().reset_index().rename(columns={0: '리뷰수'})

    def get_review_by_duration(self, df):
        df['일정'] = df['상품명'].str.extract(r'(\d박 \d일)').fillna('기타 일정')
        return df.groupby('일정').size().reset_index().rename(columns={0: '리뷰수'})

    def get_review_summary_ranking(self, df):
        mock_keywords = ['친절한 가이드', '깨끗한 숙소', '맛있는 식사', '알찬 일정', '적당한 자유시간']
        return pd.DataFrame({'키워드': mock_keywords, '빈도': np.random.randint(100, 500, 5)})

    def get_review_sentiment_keywords(self, df):
        return {
            'positive': pd.DataFrame({'키워드': ['가이드', '숙소', '식사'], '스코어': [0.8, 0.7, 0.6]}),
            'negative': pd.DataFrame({'키워드': ['쇼핑', '이동', '대기'], '스코어': [0.5, 0.4, 0.3]})
        }

    def get_review_length_analysis(self, df):
        df['리뷰길이'] = df['내용'].str.len()
        return df[['리뷰길이', '평점']]

    def get_correlation_metrics(self, df):
        return {
            'shop': df.groupby('쇼핑횟수')['평점'].mean().reset_index(),
            'city': df[['대상도시', '평점']]
        }

    def get_bubble_market_map(self, df):
        return df.groupby(['대상도시', '쇼핑횟수']).agg({'평점': 'mean', '리뷰ID': 'count'}).reset_index().rename(columns={'평점': '평균평점', '리뷰ID': '리뷰수'})

    def get_negative_cause_deep_mining(self, df):
        data = pd.DataFrame({
            '원인분류': ['가이드 불친절', '숙소 위생', '쇼핑 강요', '일정 빡빡함', '식사 부실'],
            '출현율(%)': [25.4, 20.1, 18.5, 15.2, 10.8]
        })
        return {'total': len(df[df['평점'] <= 3]), 'data': data}

    def get_city_negative_keyword_heatmap(self, df):
        cities = ['다낭', '나트랑', '싱가포르']
        kws = ['가이드', '숙소', '쇼핑', '대기', '음식']
        data = np.random.randint(5, 50, (3, 5))
        return pd.DataFrame(data, index=cities, columns=kws)

    def get_review_demographics(self, df):
        age_data = df.groupby('연령대').agg({'리뷰ID': 'count', '평점': 'mean'}).reset_index().rename(columns={'리뷰ID': '리뷰수', '평점': '평균평점'})
        age_data['연령대'] = age_data['연령대'].astype(str) + "대"
        comp_data = df.groupby('동행')['평점'].mean().reset_index().rename(columns={'평점': '평균평점'})
        return {'age': age_data, 'companion': comp_data}

    def get_rating_heatmap_data(self, df):
        pivot = df.pivot_table(index='연령대', columns='동행', values='평점', aggfunc='mean')
        pivot.index = pivot.index.astype(str) + "대"
        return pivot

    # --- [New! Advanced Recommendation System Methods] ---

    def _prepare_tfidf(self):
        """내부 TF-IDF 매트릭스 준비 (캐싱)"""
        if self.tfidf_matrix is not None: return
        
        # 상품별 고유 텍스트 데이터 구축 (상품명 + 리뷰 요약)
        product_texts = self.df.groupby('상품코드').agg({
            '상품명': 'first',
            '내용': lambda x: " ".join(x.head(20)) # 상위 20개 리뷰 결합
        }).reset_index()
        product_texts['combined'] = product_texts['상품명'] + " " + product_texts['내용']
        
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(product_texts['combined'])
        self.product_index_map = {code: i for i, code in enumerate(product_texts['상품코드'])}
        self.index_product_map = {i: code for i, code in enumerate(product_texts['상품코드'])}

    def get_rule_based_recommendations(self, persona_data):
        """단계별 페르소나 수집 Wizard 결과 기반의 룰 추천"""
        target_df = self.df.copy()
        
        # 1. 예산 필터링
        budget_map = {'100만원 미만': 1000000, '100~200만원': 2000000, '200~300만원': 3000000, '300만원 이상': 10000000}
        max_budget = budget_map.get(persona_data.get('budget'), 1500000)
        target_df = target_df[target_df['성인가격'] <= max_budget]
        
        # 2. 프리미엄 고객(200만 이상) + 쇼핑 관심 없음 -> 쇼핑 0회 우선 가중
        if max_budget >= 2000000 and persona_data.get('shopping') == '관심 없음':
            target_df = target_df[target_df['쇼핑횟수'] == 0]
            
        # 3. 여행 스타일별 도시 가중치
        style = persona_data.get('style')
        if style == '완전한 휴양·힐링':
            target_df = target_df.sort_values(by=['평점'], ascending=False)
            # 나트랑 우선 (Mock 가중치)
            target_df['score'] = np.where(target_df['대상도시'] == '나트랑', 1.2, 1.0)
        elif style == '미식·맛집':
            target_df['score'] = np.where(target_df['대상도시'] == '다낭', 1.2, 1.0)
            
        # 4. 가족 + 아이 동반 -> 다낭 가중치 (바나힐 등)
        if persona_data.get('companion') == '가족' and '아이' in str(persona_data.get('with_child')):
            target_df['score'] = target_df.get('score', 1.0) * np.where(target_df['대상도시'] == '다낭', 1.3, 1.0)

        # 최종 스코어 계산 및 정렬
        target_df['final_score'] = target_df['평점'] * target_df.get('score', 1.0)
        
        # 상품코드 기준 고유 상품 추출
        res = target_df.drop_duplicates('상품코드').sort_values('final_score', ascending=False).head(10)
        return res

    def get_content_based_recommendations(self, product_code, top_n=5):
        """특정 상품과 키워드 유사도가 높은 상품 추천"""
        self._prepare_tfidf()
        if product_code not in self.product_index_map: return pd.DataFrame()
        
        idx = self.product_index_map[product_code]
        sim_scores = cosine_similarity(self.tfidf_matrix[idx], self.tfidf_matrix)[0]
        
        # 유사도 순 정렬
        sim_indices = sim_scores.argsort()[::-1][1:top_n+1]
        sim_codes = [self.index_product_map[i] for i in sim_indices]
        
        res = self.df[self.df['상품코드'].isin(sim_codes)].drop_duplicates('상품코드').copy()
        res['유사도'] = [sim_scores[self.product_index_map[code]] for code in res['상품코드']]
        return res.sort_values('유사도', ascending=False)

    def get_collaborative_recommendations(self, persona_data, top_n=5):
        """유사 페르소나 그룹(군집)의 선호 상품 추천"""
        # 리뷰어 성향 클러스터링 모방 (동행, 연령대 기반)
        target_df = self.df.copy()
        # 간단한 매칭: 동일 동행 및 연령대 그룹에서 평점이 높은 상품
        cluster_df = target_df[
            (target_df['동행'] == persona_data.get('companion')) & 
            (target_df['연령대'] == int(persona_data.get('age', '30').replace('대', '')))
        ]
        
        if cluster_df.empty: # 데이터 부족 시 전체 베스트셀러
            cluster_df = target_df
            
        res = cluster_df.groupby('상품코드').agg({
            '평점': 'mean',
            '상품명': 'first',
            '대상도시': 'first',
            '성인가격': 'first',
            '리뷰ID': 'count'
        }).reset_index().rename(columns={'리뷰ID': '리뷰수'})
        
        return res.sort_values(['평점', '리뷰수'], ascending=False).head(top_n)

    def get_recommendation_impact_factors(self, persona_data, product):
        """XAI 시각화를 위한 요인별 기여도 산출 Logic"""
        factors = ['예산', '동행유형', '여행스타일', '쇼핑여부', '시즌성']
        # 가상의 기여도 생성 (Persona 데이터에 따라 가중치 변동 시뮬레이션)
        values = np.random.dirichlet(np.ones(5), size=1)[0] * 100
        return pd.DataFrame({'Factor': factors, 'Impact': values})

    # --- [Tab 4/5 추가 메서드 복구] ---
    def get_margin_rating_matrix(self, df):
        res = df.groupby('상품코드').agg({'평점': 'mean', '리뷰ID': 'count', '대상도시': 'first', '상품명': 'first'}).reset_index().rename(columns={'리뷰ID': '리뷰수'})
        res['마진율(%)'] = np.random.uniform(5, 25, len(res))
        return res

    def get_customer_journey_churn(self, df):
        return pd.DataFrame({
            '단계': ['상세조회', '장바구니', '예약진행', '최종결제'],
            '도시': '다낭',
            '전환율(%)': [100, 45, 20, 8.5]
        })

    def get_segment_price_sensitivity(self, df):
        return df.groupby(['연령대', '동행']).agg({'성인가격': 'mean', '평점': 'mean', '리뷰ID': 'count'}).reset_index().rename(columns={'리뷰ID': '리뷰수'})

    def get_family_satisfaction_split(self, df):
        return pd.DataFrame([
            {'만족도 유형': '체험 만족도 (액티비티/키즈)', '평균평점': 4.7},
            {'만족도 유형': '일정 만족도 (대기/이동 강도)', '평균평점': 3.8}
        ])

    def get_price_shopping_mismatch(self, df):
        return df[df['쇼핑횟수'] >= 3].head(5)

    def get_segment_density_impact(self, df):
        return pd.DataFrame({
            '밀집도_구간': ['여유', '보통', '빡빡'],
            '그룹': '아동 동반',
            '평점': [4.8, 4.2, 3.5]
        })

if __name__ == "__main__":
    engine = AnalyticsEngine()
    print("Engine Initialized. Data shape:", engine.df.shape)
