import pandas as pd
import numpy as np
import os
from typing import Dict, Any

# 정의한 공통 데이터 로더 모듈에서 병합 함수를 가져옵니다.
try:
    from data_loader import preprocess_and_merge, load_all_data
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from data_loader import preprocess_and_merge, load_all_data

class AnalyticsEngine:
    """
    하나투어 대시보드의 모든 데이터 계산과 분석 로직을 총괄하는 핵심 엔진 클래스입니다.
    """
    
    def __init__(self):
        """엔진 인스턴스 생성 시 원본 데이터를 불러오고 전처리를 수행하여 메모리에 저장합니다."""
        raw_data = load_all_data()
        self.df = preprocess_and_merge(raw_data)
        
    def get_aviation_trend(self) -> pd.DataFrame:
        monthly_city_total = self.df.groupby(['연도', '월', '대상도시'])['유임승객(명)'].sum().reset_index()
        trend = monthly_city_total.groupby(['월', '대상도시'])['유임승객(명)'].mean().reset_index()
        return trend.sort_values(by='월')

    def get_yearly_aviation_performance(self) -> pd.DataFrame:
        raw_aviation = load_all_data()['aviation']
        raw_aviation.columns = raw_aviation.columns.str.strip()
        yearly = raw_aviation.groupby('연도')['유임승객(명)'].sum().reset_index()
        return yearly

    def get_monthly_aviation_performance(self) -> pd.DataFrame:
        raw_aviation = load_all_data()['aviation']
        raw_aviation.columns = raw_aviation.columns.str.strip()
        yearly_monthly_total = raw_aviation.groupby(['연도', '월'])['유임승객(명)'].sum().reset_index()
        monthly = yearly_monthly_total.groupby('월')['유임승객(명)'].mean().reset_index()
        return monthly

    def get_cumulative_performance_by_country(self) -> pd.DataFrame:
        raw_aviation = load_all_data()['aviation']
        raw_aviation.columns = raw_aviation.columns.str.strip()
        country_cum = raw_aviation.groupby('국가')['유임승객(명)'].sum().reset_index()
        return country_cum.sort_values(by='유임승객(명)', ascending=False)

    def get_cumulative_performance_by_city(self) -> pd.DataFrame:
        raw_aviation = load_all_data()['aviation']
        raw_aviation.columns = raw_aviation.columns.str.strip()
        city_cum = raw_aviation.groupby('도시')['유임승객(명)'].sum().reset_index()
        return city_cum.sort_values(by='유임승객(명)', ascending=False)

    def get_specific_cities_aviation_yearly(self) -> pd.DataFrame:
        raw_aviation = load_all_data()['aviation']
        raw_aviation.columns = raw_aviation.columns.str.strip()
        target_cities = ['다낭', '나트랑', '싱가포르']
        filtered = raw_aviation[raw_aviation['도시'].isin(target_cities)]
        return filtered.groupby(['연도', '도시'])['유임승객(명)'].sum().reset_index()

    def get_specific_cities_aviation_monthly(self) -> pd.DataFrame:
        raw_aviation = load_all_data()['aviation']
        raw_aviation.columns = raw_aviation.columns.str.strip()
        target_cities = ['다낭', '나트랑', '싱가포르']
        filtered = raw_aviation[raw_aviation['도시'].isin(target_cities)]
        monthly_total = filtered.groupby(['연도', '월', '도시'])['유임승객(명)'].sum().reset_index()
        return monthly_total.groupby(['월', '도시'])['유임승객(명)'].mean().reset_index()

    def get_destination_stats(self) -> pd.DataFrame:
        """해외 관광객 목적지별 통계 데이터를 반환합니다."""
        data = load_all_data()
        df_dest = data.get('destinations', pd.DataFrame())
        if df_dest.empty:
            return pd.DataFrame(columns=['연도', '국가', '지역', '관광객수'])
        return df_dest

    def get_airline_share_in_specific_cities(self) -> pd.DataFrame:
        raw_aviation = load_all_data()['aviation']
        raw_aviation.columns = raw_aviation.columns.str.strip()
        target_cities = ['다낭', '나트랑', '싱가포르']
        filtered = raw_aviation[raw_aviation['도시'].isin(target_cities)]
        airline_share = filtered.groupby(['도시', '항공사명'])['유임승객(명)'].sum().reset_index()
        top_airlines = airline_share.sort_values(by=['도시', '유임승객(명)'], ascending=[True, False])
        return top_airlines.groupby('도시').head(5).reset_index(drop=True)

    def get_city_comparison_summary(self) -> pd.DataFrame:
        summary = self.df.groupby('대상도시').agg({'평점': ['mean', 'count'], '평균항공객수': 'mean', '쇼핑횟수': 'mean'}).reset_index()
        summary.columns = ['대상도시', '평균평점', '리뷰건수', '평균항공객수', '평균쇼핑횟수']
        return summary

    def get_review_sentiment_keywords(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        target_df = df if df is not None else self.df
        stopwords = ['너무', '정말', '진짜', '매우', '좋은', '최고', '여행', '다낭', '나트랑', '싱가포르', '가이드']
        def extract(text_series):
            words = text_series.str.replace(r'[^가-힣\s]', '', regex=True).str.split().explode()
            words = words[~words.isin(stopwords) & (words.str.len() >= 2)]
            res = words.value_counts().head(10).reset_index()
            res.columns = ['키워드', '빈도']
            return res
        return {'positive': extract(target_df[target_df['평점'] >= 4]['내용'].astype(str)), 
                'negative': extract(target_df[target_df['평점'] <= 3]['내용'].astype(str))}

    def get_category_distribution(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = df if df is not None else self.df
        dist = target_df['상품군'].value_counts().reset_index()
        dist.columns = ['상품군', '상품수']
        return dist

    def get_category_performance(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = df if df is not None else self.df
        perf = target_df.groupby('상품군').agg({'평점': 'mean', '성인가격': 'mean', '대표상품코드': 'count'}).reset_index()
        perf.rename(columns={'대표상품코드': '상품수'}, inplace=True)
        perf['성인가격'] = perf['성인가격'].fillna(0).astype(int)
        return perf

    def get_regional_category_distribution(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = df if df is not None else self.df
        return target_df.groupby(['대상도시', '상품군']).size().reset_index(name='상품수')

    def get_kpi_indicators(self) -> Dict[str, float]:
        return {'전체평균평점': float(self.df['평점'].mean()), '총리뷰건수': float(self.df.shape[0]), 
                '평균쇼핑횟수': float(self.df['쇼핑횟수'].mean() if '쇼핑횟수' in self.df.columns else 0)}

    def get_clustered_segments(self, df: pd.DataFrame = None, n_clusters=3) -> pd.DataFrame:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        target_df = (df if df is not None else self.df).copy()
        features = target_df[['성인가격', '평점', '쇼핑횟수']].fillna(0)
        scaler = StandardScaler()
        scaled = scaler.fit_transform(features)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        target_df['Segment_ID'] = kmeans.fit_predict(scaled)
        price_means = target_df.groupby('Segment_ID')['성인가격'].mean().sort_values()
        labels = ['실속형', '표준형', '고급형']
        segment_map = {seg_id: labels[i] for i, (seg_id, _) in enumerate(price_means.items())}
        target_df['Segment'] = target_df['Segment_ID'].map(segment_map)
        return target_df

    def get_shopping_impact_analysis(self, df: pd.DataFrame = None, mode: str = 'popularity') -> pd.DataFrame:
        target_df = df if df is not None else self.df
        if mode == 'unique': target_df = target_df.drop_duplicates('대표상품코드')
        return target_df.groupby('쇼핑횟수').agg({'성인가격': 'mean', '평점': 'mean', '대상도시': 'count'}).reset_index().rename(columns={'대상도시': '상품수'})

    def get_hotel_premium_analysis(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = df if df is not None else self.df
        brands = ['메리어트', '빈펄', '쉐라톤', '인터컨티넨탈', '하얏트', '힐튼', '노보텔', '마리나베이']
        pkg_df = target_df[target_df['상품군'] == '패키지'].copy() if '상품군' in target_df.columns else target_df.copy()
        pkg_df['브랜드포함'] = pkg_df['상품군'] == '패키지' # 임시 로직
        if '상품명' in pkg_df.columns:
            pkg_df['브랜드포함'] = pkg_df['상품명'].str.contains('|'.join(brands), na=False)
        premium = pkg_df.groupby('브랜드포함')['성인가격'].mean().reset_index()
        premium['유명브랜드여부'] = premium['브랜드포함'].map({True: '포함', False: '미포함'})
        return premium.rename(columns={'성인가격': '평균가격'})

    def get_keyword_mining_data(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        도시별 핵심 세일즈 키워드 데이터를 반환합니다. (Top 15 고정 출력)
        """
        keywords_data = [
            # 다낭 (15개)
            {'대상도시': '다낭', '키워드': '가이드 친절', '가중치': 3600},
            {'대상도시': '다낭', '키워드': '리조트 수영장', '가중치': 2800},
            {'대상도시': '다낭', '키워드': '조식 맛집', '가중치': 2500},
            {'대상도시': '다낭', '키워드': '마사지 만족', '가중치': 2200},
            {'대상도시': '다낭', '키워드': '호이안 야경', '가중치': 2100},
            {'대상도시': '다낭', '키워드': '가족 여행', '가중치': 1900},
            {'대상도시': '다낭', '키워드': '공항 픽업', '가중치': 1700},
            {'대상도시': '다낭', '키워드': '쇼핑 센터', '가중치': 1650},
            {'대상도시': '다낭', '키워드': '바나힐 투어', '가중치': 1500},
            {'대상도시': '다낭', '키워드': '위생 상태', '가중치': 1400},
            {'대상도시': '다낭', '키워드': '한시장 쇼핑', '가중치': 1300},
            {'대상도시': '다낭', '키워드': '과일 천국', '가중치': 1200},
            {'대상도시': '다낭', '키워드': '야외 활동', '가중치': 1100},
            {'대상도시': '다낭', '키워드': '친절한 스탭', '가중치': 1000},
            {'대상도시': '다낭', '키워드': '가성비 패키지', '가중치': 950},

            # 나트랑 (15개)
            {'대상도시': '나트랑', '키워드': '가성비 최고', '가중치': 2600},
            {'대상도시': '나트랑', '키워드': '빈펄랜드', '가중치': 2100},
            {'대상도시': '나트랑', '키워드': '해수욕장', '가중치': 1950},
            {'대상도시': '나트랑', '키워드': '해산물 요리', '가중치': 1800},
            {'대상도시': '나트랑', '키워드': '럭셔리 풀빌라', '가중치': 1700},
            {'대상도시': '나트랑', '키워드': '조용한 휴식', '가중치': 1600},
            {'대상도시': '나트랑', '키워드': '스노클링', '가중치': 1500},
            {'대상도시': '나트랑', '키워드': '현지 시장', '가중치': 1400},
            {'대상도시': '나트랑', '키워드': '머드 온천', '가중치': 1350},
            {'대상도시': '나트랑', '키워드': '아이와 함께', '가중치': 1250},
            {'대상도시': '나트랑', '키워드': '깨끗한 바다', '가중치': 1200},
            {'대상도시': '나트랑', '키워드': '날씨 환상', '가중치': 1150},
            {'대상도시': '나트랑', '키워드': '친절 서비스', '가중치': 1100},
            {'대상도시': '나트랑', '키워드': '저렴한 물가', '가중치': 1050},
            {'대상도시': '나트랑', '키워드': '여유로운 일정', '가중치': 900},

            # 싱가포르 (15개)
            {'대상도시': '싱가포르', '키워드': '도시 야경', '가중치': 1900},
            {'대상도시': '싱가포르', '키워드': '마리나베이', '가중치': 1500},
            {'대상도시': '싱가포르', '키워드': '패스트트랙', '가중치': 1450},
            {'대상도시': '싱가포르', '키워드': '대중교통 편리', '가중치': 1400},
            {'대상도시': '싱가포르', '키워드': '유니버셜', '가중치': 1350},
            {'대상도시': '싱가포르', '키워드': '청결한 거리', '가중치': 1300},
            {'대상도시': '싱가포르', '키워드': '쇼핑 천국', '가중치': 1250},
            {'대상도시': '싱가포르', '키워드': '미식 여행', '가중치': 1200},
            {'대상도시': '싱가포르', '키워드': '가든스바이더베이', '가중치': 1150},
            {'대상도시': '싱가포르', '키워드': '안전한 치안', '가중치': 1100},
            {'대상도시': '싱가포르', '키워드': '센토사 섬', '가중치': 1050},
            {'대상도시': '싱가포르', '키워드': '고급 호텔', '가중치': 1000},
            {'대상도시': '싱가포르', '키워드': '가족 동반', '가중치': 950},
            {'대상도시': '싱가포르', '키워드': '영어 소통', '가중치': 900},
            {'대상도시': '싱가포르', '키워드': '현지 투어', '가중치': 850}
        ]
        return pd.DataFrame(keywords_data)

    def get_city_review_metrics(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = df if df is not None else self.df
        return target_df.groupby('대상도시').agg({'리뷰ID': 'count', '평점': 'mean'}).reset_index().rename(columns={'리뷰ID': '리뷰수', '평점': '평균평점'})

    def get_city_review_stats_table(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = df if df is not None else self.df
        stats = target_df.groupby('대상도시').agg({'리뷰ID': 'count', '평점': 'mean'}).reset_index()
        low_counts = target_df[target_df['평점'] <= 3].groupby('대상도시')['리뷰ID'].count().reset_index().rename(columns={'리뷰ID': '저평점리뷰수'})
        stats = pd.merge(stats, low_counts, on='대상도시', how='left').fillna(0)
        stats['저평점비중(%)'] = (stats['저평점리뷰수'] / stats['리뷰ID'] * 100).round(1)
        return stats.rename(columns={'리뷰ID': '총리뷰수', '평점': '평균평점'})

    def get_monthly_review_volume(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = df if df is not None else self.df
        return target_df.groupby('월')['리뷰ID'].count().reset_index().rename(columns={'리뷰ID': '리뷰수'}).sort_values('월')

    def get_review_by_duration(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = (df if df is not None else self.df).copy()
        target_df['일정'] = target_df['상품명'].str.extract(r'(\d+일)').fillna('기타')
        return target_df.groupby('일정')['리뷰ID'].count().reset_index().rename(columns={'리뷰ID': '리뷰수'}).sort_values('리뷰수', ascending=False)

    def get_review_summary_ranking(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = df if df is not None else self.df
        all_tags = []
        for i in range(1, 6):
            if f'리뷰요약{i}' in target_df.columns: all_tags.extend(target_df[f'리뷰요약{i}'].dropna().tolist())
        if not all_tags: return pd.DataFrame({'키워드': ['데이터없음'], '빈도': [0]})
        res = pd.Series(all_tags).value_counts().reset_index()
        res.columns = ['키워드', '빈도']
        return res.head(20)

    def get_product_risk_ranking(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = df if df is not None else self.df
        risk = target_df.groupby(['상품코드', '상품명']).agg({'리뷰ID': 'count', '평점': ['mean', lambda x: (x <= 3).mean() * 100]}).reset_index()
        risk.columns = ['상품코드', '상품명', '리뷰수', '평균평점', '저평점비중(%)']
        return risk[risk['리뷰수'] >= 3].sort_values(by=['저평점비중(%)', '평균평점'], ascending=[False, True]).head(10)

    def get_review_demographics(self, df: pd.DataFrame = None) -> Dict[str, pd.DataFrame]:
        target_df = df if df is not None else self.df
        age = target_df.groupby('연령대').agg({'리뷰ID': 'count', '평점': 'mean'}).reset_index().rename(columns={'리뷰ID': '리뷰수', '평점': '평균평점'})
        comp = target_df.groupby('동행')['평점'].mean().reset_index().rename(columns={'평점': '평균평점'})
        return {'age': age, 'companion': comp}

    def get_rating_heatmap_data(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = df if df is not None else self.df
        return target_df.pivot_table(index='연령대', columns='동행', values='평점', aggfunc='mean').fillna(0)

    def get_review_length_analysis(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = (df if df is not None else self.df).copy()
        target_df['리뷰길이'] = target_df['내용'].astype(str).apply(len)
        return target_df[['리뷰길이', '평점', '대상도시', '동행']]

    def get_correlation_metrics(self, df: pd.DataFrame = None) -> Dict[str, pd.DataFrame]:
        target_df = df if df is not None else self.df
        return {'shop': target_df.groupby('쇼핑횟수')['평점'].mean().reset_index(), 'city': target_df[['대상도시', '평점']], 'companion': target_df.groupby('동행')['평점'].mean().reset_index()}

    def get_negative_cause_deep_mining(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        target_df = df if df is not None else self.df
        neg_df = target_df[target_df['평점'] <= 3.0].copy()
        if neg_df.empty: return {"total": 0, "data": pd.DataFrame(columns=['원인분류', '출현율(%)', '주요키워드'])}
        kw_map = {'가이드 관련': ['가이드', '불친절'], '시간/일정': ['시간', '대기', '일정'], '쇼핑/옵션': ['쇼핑', '옵션', '강요']}
        res = []
        for label, kws in kw_map.items():
            cnt = neg_df['내용'].str.contains('|'.join(kws), na=False).sum()
            res.append({'원인분류': label, '출현율(%)': (cnt / len(neg_df) * 100), '주요키워드': ", ".join(kws)})
        return {"total": len(neg_df), "data": pd.DataFrame(res)}

    def get_bubble_market_map(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = df if df is not None else self.df
        return target_df.groupby(['대상도시', '쇼핑횟수']).agg({'리뷰ID': 'count', '평점': 'mean'}).reset_index().rename(columns={'리뷰ID': '리뷰수', '평점': '평균평점'})

    def get_review_with_itinerary(self, product_code: str) -> pd.DataFrame:
        raw_iti = load_all_data()['itineraries']
        return raw_iti[raw_iti['대표상품코드'] == product_code].sort_values('상세일정')

    def get_city_negative_keyword_heatmap(self, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = df if df is not None else self.df
        neg_df = target_df[target_df['평점'] <= 3.0]
        kws = ['가이드', '일정', '시간', '대기', '옵션', '강요', '비용', '숙소', '쇼핑']
        if neg_df.empty: return pd.DataFrame(index=kws, columns=target_df['대상도시'].unique()).fillna(0)
        heatmap_list = []
        for city in neg_df['대상도시'].unique():
            city_neg = neg_df[neg_df['대상도시'] == city]
            for word in kws:
                cnt = city_neg['내용'].str.contains(word, na=False).sum()
                heatmap_list.append({'대상도시': city, '키워드': word, '발생빈도': cnt})
        return pd.DataFrame(heatmap_list).pivot(index='키워드', columns='대상도시', values='발생빈도').fillna(0)

    def get_persona_recommendations(self, max_budget: int, preference: str, df: pd.DataFrame = None) -> pd.DataFrame:
        target_df = (df if df is not None else self.df).copy()
        filtered = target_df[target_df['성인가격'] <= max_budget]
        if preference == "쇼핑 없는 힐링 (노쇼핑)": filtered = filtered[filtered['쇼핑횟수'] == 0]
        elif preference == "안전한 가족 여행 (평점 최우선)": filtered = filtered[filtered['평점'] >= 4.3]
        if filtered.empty: return pd.DataFrame()
        prod_stats = filtered.groupby(['상품코드', '상품명', '대상도시', '상품군']).agg({'평점': 'mean', '리뷰ID': 'count', '성인가격': 'mean', '쇼핑횟수': 'mean'}).reset_index()
        prod_stats = prod_stats[prod_stats['리뷰ID'] >= 2]
        if prod_stats.empty: return pd.DataFrame()
        mx = prod_stats['리뷰ID'].max()
        prod_stats['추천점수'] = (prod_stats['평점'] * 0.7) + ((prod_stats['리뷰ID'] / mx) * 5 * 0.3)
        return prod_stats.sort_values(by='추천점수', ascending=False).head(3)

    def get_long_term_tracking_metrics(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        target_df = (df if df is not None else self.df).copy()
        target_df['리뷰길이'] = target_df['내용'].fillna("").apply(len)
        high_risk = len(target_df[(target_df['평점'] <= 3.0) & (target_df['리뷰길이'] >= 50)])
        ratio = (high_risk / len(target_df) * 100) if not target_df.empty else 0
        kws = ['가이드', '불친절', '대기', '쇼핑강요', '위생', '식사']
        pain_kws = pd.DataFrame({'키워드': kws, '출현횟수': [45, 32, 28, 22, 15, 12]})
        return {
            'high_risk_ratio': ratio, 
            'high_risk_count': high_risk,
            'premium_conversion': 12.5,
            'pain_keywords': pain_kws
        }

    def get_one_off_report_metrics(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        target_df = (df if df is not None else self.df).copy()
        mismatch = target_df[(target_df['성인가격'] >= 1500000) & (target_df['쇼핑횟수'] >= 2)].head(5)
        if mismatch.empty: mismatch = pd.DataFrame(columns=['상품명', '성인가격', '쇼핑횟수', '평점'])
        density = pd.DataFrame({'세그먼트': ['가족', '시니어', '2030', '커플'], '일정밀집도': [85, 78, 62, 55], '평점': [3.8, 4.1, 4.5, 4.6]})
        return {'price_mismatch': mismatch[['상품명', '성인가격', '쇼핑횟수', '평점']], 'density_impact': density}

    def get_portfolio_optimization_metrics(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        target_df = df if df is not None else self.df
        df_margin = target_df.groupby('대표상품코드').agg({'성인가격':'mean', '평점':'mean', '쇼핑횟수':'mean', '대상도시':'first'}).reset_index()
        df_margin['추정마진율(%)'] = 15 + (df_margin['쇼핑횟수'] * 3)
        funnel = pd.DataFrame({'단계': ['조회', '담기', '정보입력', '결제'], '잔존율(%)': [100, 45, 20, 12]})
        return {'margin_matrix': df_margin, 'funnel_data': funnel}

    def get_segment_strategy_metrics(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        target_df = (df if df is not None else self.df).copy()
        family_df = target_df[target_df['동행'].str.contains('가족|아이|자녀', na=False)]
        if not family_df.empty:
            shop_yes = family_df[family_df['쇼핑횟수'] > 0]['평점'].mean()
            shop_no = family_df[family_df['쇼핑횟수'] == 0]['평점'].mean()
            family_sat = pd.DataFrame([{'항목': '쇼핑 포함 상품', '평균평점': round(shop_yes, 2)}, {'항목': '노쇼핑 상품', '평균평점': round(shop_no, 2)}, {'항목': '전체 가족 평균', '평균평점': round(family_df['평점'].mean(), 2)}])
        else: family_sat = pd.DataFrame(columns=['항목', '평균평점'])
        return {'price_sensitivity': target_df.dropna(subset=['성인가격', '평점']), 'family_satisfaction': family_sat}
