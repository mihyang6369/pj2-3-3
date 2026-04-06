import pandas as pd
import os
import streamlit as st

@st.cache_data
def load_all_data():
    """
    분석에 필요한 5가지 주요 CSV 파일을 통합 로드합니다.
    """
    base_path = "c:/Users/Administrator/Desktop/fcicb6/pj2/pj2-3-3/data"
    
    files = {
        'reviews': 'hanatour_reviews.csv',
        'aviation': 'filtered_aviation_performance.csv',
        'danang': 'hanatour_danang_integrated.csv',
        'nhatrang': 'hanatour_nhatrang_integrated.csv',
        'singapore': 'hanatour_singapore_integrated.csv'
    }
    
    data = {}
    for key, filename in files.items():
        path = os.path.join(base_path, filename)
        if os.path.exists(path):
            data[key] = pd.read_csv(path, encoding='utf-8-sig')
        else:
            data[key] = pd.DataFrame()
            
    return data

def preprocess_and_merge(data):
    """
    리뷰 데이터와 도시별 마스터 정보를 병합하여 분석용 통합 데이터프레임을 생성합니다.
    """
    reviews = data.get('reviews', pd.DataFrame())
    if reviews.empty:
        return pd.DataFrame()
        
    # 기본 전처리
    reviews['작성일'] = pd.to_datetime(reviews['작성일'], errors='coerce')
    reviews['월'] = reviews['작성일'].dt.month
    reviews['평점'] = reviews['평점'].astype(float)
    
    # 도시별 마스터 데이터(쇼핑횟수, 성인가격 등) 통합
    masters = []
    for city in ['danang', 'nhatrang', 'singapore']:
        m = data.get(city, pd.DataFrame())
        if not m.empty:
            # 병합에 필요한 핵심 컬럼만 추출
            m = m[['대표상품코드', '성인가격', '쇼핑횟수']].drop_duplicates()
            masters.append(m)
            
    if masters:
        master_df = pd.concat(masters, axis=0).drop_duplicates('대표상품코드')
        # 리뷰의 '상품코드'와 마스터의 '대표상품코드'를 기준으로 병합
        combined_df = pd.merge(reviews, master_df, left_on='상품코드', right_on='대표상품코드', how='left')
    else:
        combined_df = reviews
        
    return combined_df
