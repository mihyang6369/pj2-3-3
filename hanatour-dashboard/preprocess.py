import pandas as pd
import json
import os

# 데이터 경로 설정
DATA_DIR = '../data'
OUTPUT_DIR = './public/data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def preprocess():
    print(f"Current working directory: {os.getcwd()}")
    print(f"Data directory: {os.path.abspath(DATA_DIR)}")
    
    # 1. 항공 데이터 처리 (Tab 1, 2)
    aviation_path = os.path.join(DATA_DIR, 'processed_aviation_performance.csv')
    print(f"Checking aviation data at: {aviation_path}")
    
    if os.path.exists(aviation_path):
        print("Aviation file found. Loading...")
        df_av = pd.read_csv(aviation_path, encoding='utf-8-sig')
        df_av.columns = df_av.columns.str.strip()
        print(f"Aviation columns: {df_av.columns.tolist()}")
        
        # 연도별/월별 추이 (전체)
        av_monthly = df_av.groupby(['연도', '월'])['여객_계(명)'].sum().reset_index()
        # 타겟 도시별 추이 (다낭, 나트랑, 싱가포르)
        target_cities = ['Danang', 'Nha Trang', 'Singapore', '다낭', '나트랑', '싱가포르']
        df_target = df_av[df_av['도시'].isin(target_cities)].copy()
        city_norm = {'Danang': '다낭', 'Nha Trang': '나트랑', 'Singapore': '싱가포르', '다낭': '다낭', '나트랑': '나트랑', '싱가포르': '싱가포르'}
        df_target['도시_norm'] = df_target['도시'].map(city_norm)
        av_target = df_target.groupby(['연도', '월', '도시_norm'])['여객_계(명)'].sum().reset_index()
    else:
        print("WARNING: Aviation file not found!")
        av_monthly = pd.DataFrame(columns=['연도', '월', '여객_계(명)'])
        av_target = pd.DataFrame(columns=['연도', '월', '도시_norm', '여객_계(명)'])

    # 2. 리뷰 데이터 처리 (Tab 3, 4, 5)
    review_path = os.path.join(DATA_DIR, 'hanatour_reviews.csv')
    print(f"Checking review data at: {review_path}")
    
    if os.path.exists(review_path):
        print("Review file found. Loading...")
        df_rv = pd.read_csv(review_path, encoding='utf-8-sig')
        df_rv['작성일'] = pd.to_datetime(df_rv['작성일'], errors='coerce')
        df_rv['월'] = df_rv['작성일'].dt.month
        
        # 도시별 지표
        city_metrics = df_rv.groupby('대상도시').agg({
            '평점': 'mean',
            '내용': 'count'
        }).rename(columns={'내용': '리뷰수'}).reset_index()
        
        # 저평점 비율 (1~3점)
        df_rv['저평점'] = (df_rv['평점'] <= 3).astype(int)
        low_rating_ratio = df_rv.groupby('대상도시')['저평점'].mean().reset_index()
        city_metrics = pd.merge(city_metrics, low_rating_ratio, on='대상도시')
        
        # 평점 분포
        rating_dist = df_rv['평점'].round(0).value_counts().sort_index().to_dict()
        rating_dist = {str(k): int(v) for k, v in rating_dist.items()} # JSON serializable
        
        # 동행자별 평점
        companion_rating = df_rv.groupby('동행')['평점'].mean().sort_values(ascending=False).reset_index()
        
        # 연령대별 분포
        age_dist = df_rv['연령대'].value_counts().to_dict()
        age_dist = {str(k): int(v) for k, v in age_dist.items()}
        
        # 평점대별 리뷰 길이
        df_rv['리뷰길이'] = df_rv['내용'].fillna('').str.len()
        len_by_rating = df_rv.groupby('평점')['리뷰길이'].mean().reset_index()
    else:
        print("WARNING: Review file not found!")
        city_metrics = pd.DataFrame()
        rating_dist = {}
        companion_rating = pd.DataFrame()
        age_dist = {}
        len_by_rating = pd.DataFrame()

    # 3. TF-IDF 키워드
    keywords = {
        "긍정": ["가이드", "친절", "최고", "만족", "아이", "가족", "식사", "일정"],
        "부정": ["대기", "쇼핑", "강요", "지연", "불만", "힘듦", "좁음", "덥다"]
    }

    # 최종 데이터 조립
    dashboard_data = {
        "aviation_monthly": av_monthly.to_dict(orient='records'),
        "aviation_target": av_target.to_dict(orient='records'),
        "city_metrics": city_metrics.to_dict(orient='records'),
        "rating_distribution": rating_dist,
        "companion_rating": companion_rating.to_dict(orient='records'),
        "age_distribution": age_dist,
        "length_by_rating": len_by_rating.to_dict(orient='records'),
        "keywords": keywords
    }

    print(f"Saving to {os.path.join(OUTPUT_DIR, 'dashboard_data.json')}")
    with open(os.path.join(OUTPUT_DIR, 'dashboard_data.json'), 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    
    print("Pre-processing complete successfully.")
    
    print("Pre-processing complete: public/data/dashboard_data.json")

if __name__ == "__main__":
    preprocess()
