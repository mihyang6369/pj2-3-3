"""
하나투어 데이터 로딩 및 전처리 모듈 (Data Loader)

이 모듈은 원본 CSV 파일들을 읽어오고, 데이터 분석에 적합한 형태로 
정제 및 병합하는 파이프라인을 제공합니다. 

주요 단계:
1. 로컬 경로에서 다수의 CSV 파일 로드
2. 상품 마스터(Master) 데이터 생성 및 통합
3. 리뷰 데이터와 상품 상세 정보의 병합(Merge)
4. 항공 실적 데이터와의 결합 및 최종 수치형 데이터 정형화
"""

import pandas as pd # 데이터 분석의 기본이 되는 라이브러리
import os # 파일 경로 조작을 위한 라이브러리
import numpy as np # 수치 연산을 위한 라이브러리
from typing import Tuple, Dict # 타입 힌팅을 위한 모듈

# 데이터 디렉토리 경로 설정: 현재 파일의 상위 디렉토리 내 'data' 폴더를 지칭합니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def load_all_data() -> Dict[str, pd.DataFrame]:
    """
    모든 원본 CSV 파일들을 딕셔너리 형태로 로드합니다.
    
    Returns:
        Dict[str, pd.DataFrame]: 파일명을 키로, 데이터프레임을 값으로 하는 딕셔너리
    """
    data = {}
    
    # 1. 핵심 분석 대상 데이터 로드
    # utf-8-sig 인코딩을 사용하여 한글 깨짐 현상을 방지합니다.
    data['reviews'] = pd.read_csv(os.path.join(DATA_DIR, 'hanatour_reviews.csv'), encoding='utf-8-sig')
    data['aviation'] = pd.read_csv(os.path.join(DATA_DIR, 'processed_aviation_performance.csv'), encoding='utf-8-sig')
    data['itineraries'] = pd.read_csv(os.path.join(DATA_DIR, 'hanatour_all_itineraries.csv'), encoding='utf-8-sig')
    
    # 1.1 해외 관광객 목적지별 통계 데이터 로드 추가
    dest_path = os.path.join(DATA_DIR, 'merged_overseas_destination.csv')
    if os.path.exists(dest_path):
        data['destinations'] = pd.read_csv(dest_path, encoding='utf-8-sig')
    else:
        data['destinations'] = pd.DataFrame(columns=['연도', '국가', '지역', '관광객수'])
    
    # 2. 도시별/상품 유형별로 분산된 통합 데이터들을 반복문을 통해 로드합니다.
    cities = ['danang', 'nhatrang', 'singapore'] # 분석 대상 3대 도시
    types = {'': '패키지', '_airtel': '에어텔', '_tour_ticket': '투어/티켓'} # 상품 유형 매핑
    
    for city in cities:
        for t_suffix, t_label in types.items():
            key = f"{city}{t_suffix}" # 딕셔너리에 저장할 고유 키값 생성
            filename = f"hanatour_{city}{t_suffix}_integrated.csv" # 실제 파일명 조합
            try:
                # 파일이 존재하는 경우 로드하고 '상품군' 정보를 새 컬럼으로 추가합니다.
                df = pd.read_csv(os.path.join(DATA_DIR, filename), encoding='utf-8-sig')
                df['상품군'] = t_label
                data[key] = df
            except FileNotFoundError:
                # 특정 파일이 없을 경우 경고 메시지를 출력하고 다음 파일로 넘어갑니다.
                print(f"Warning: {filename} 파일을 찾을 수 없습니다.")
                
    return data

def preprocess_and_merge(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    로드된 여러 데이터프레임들을 하나의 통합 분석용 데이터셋으로 병합합니다.
    초보 분석가들을 위해 결측치 처리 및 데이터 타입 변환 과정을 상세히 기술합니다.
    """
    # 1. 리뷰 데이터 기본 전처리
    reviews = data['reviews'].copy() # 원본 보존을 위해 복사본 생성
    
    # [방어 로직] 데이터 무결성을 위해 '상품군' 컬럼이 없는 경우 기본값을 미리 채워둡니다.
    if '상품군' not in reviews.columns:
        reviews['상품군'] = '정보없음'
        
    # '작성일'을 시계열 데이터 형식으로 변환합니다. (연도, 월 추출을 위함)
    reviews['작성일'] = pd.to_datetime(reviews['작성일'], errors='coerce')
    reviews['연도'] = reviews['작성일'].dt.year # 연도 추출
    reviews['월'] = reviews['작성일'].dt.month # 월 추출
    
    # 2. 상품별 상세 정보(쇼핑횟수, 가격 등) 마스터 데이터 생성
    target_cols = ['대표상품코드', '쇼핑횟수', '가이드동행', '상품군', '성인가격']
    city_infos = [] # 각 도시/유형별 상품 정보를 담을 리스트
    
    cities = ['danang', 'nhatrang', 'singapore']
    types = ['', '_airtel', '_tour_ticket']
    
    for city in cities:
        for suffix in types:
            key = f"{city}{suffix}"
            if key in data:
                df_city = data[key].copy()
                # 컬럼명 앞뒤에 있을 수 있는 불필요한 공백을 제거합니다.
                df_city.columns = df_city.columns.str.strip()
                
                # '성인가격' 컬럼이 없고 '정상가격'만 있는 경우 이름을 통일해줍니다.
                if '성인가격' not in df_city.columns and '정상가격' in df_city.columns:
                    df_city.rename(columns={'정상가격': '성인가격'}, inplace=True)
                
                # 분석에 필요한 컬럼들만 선별하여 리스트에 추가합니다.
                existing_cols = [c for c in target_cols if c in df_city.columns]
                if existing_cols:
                    # 중복된 상품 코드는 제거하여 마스터 데이터의 유일성을 확보합니다.
                    city_infos.append(df_city[existing_cols].drop_duplicates('대표상품코드'))
    
    # 수집된 상품 정보들을 하나로 합칩니다 (Concatenate).
    if city_infos:
        product_master = pd.concat(city_infos, axis=0).drop_duplicates('대표상품코드')
    else:
        # 정보가 아예 없는 경우를 대비한 빈 뼈대 생성
        product_master = pd.DataFrame(columns=target_cols)
    
    # 3. 리뷰 데이터와 상품 마스터 데이터 병합 (Merge)
    # 상품 정보를 병합하기 전, 리뷰의 상품군 정보가 부정확할 수 있으므로 삭제 후 마스터 정보를 따릅니다.
    if '상품군' in reviews.columns and '상품군' in product_master.columns:
        reviews_temp = reviews.drop(columns=['상품군'])
    else:
        reviews_temp = reviews
        
    # '상품코드'와 '대표상품코드'를 기준으로 왼쪽(리뷰) 데이터를 중심으로 결합합니다.
    df = pd.merge(reviews_temp, product_master, left_on='상품코드', right_on='대표상품코드', how='left')
    
    # 병합 후 '상품군'이 비어있는 경우 다시 '정보없음'으로 채워 결측치를 방어합니다.
    if '상품군' in df.columns:
        df['상품군'] = df['상품군'].fillna('정보없음')
    else:
        df['상품군'] = '정보없음'
    
    # 4. 항공 실적 데이터와의 결합
    aviation = data['aviation'].copy()
    # 도시명을 국제항공운송협회(IATA) 코드와 매핑합니다. (나중에 조인하기 위함)
    city_to_iata = {'다낭': 'DAD', '나트랑': 'CXR', '싱가포르': 'SIN'}
    df['IATA'] = df['대상도시'].map(city_to_iata)
    aviation.columns = aviation.columns.str.strip()
    
    # 항공 데이터에서 도시별, 월별 평균 유임승객 수를 구하여 시장 규모 지표로 사용합니다.
    aviation_monthly = aviation.groupby(['IATA', '월'])['유임승객(명)'].mean().reset_index()
    aviation_monthly.rename(columns={'유임승객(명)': '평균항공객수'}, inplace=True)
    
    # 최종적으로 시장 데이터(항공객수)를 분석 셋에 붙입니다.
    df = pd.merge(df, aviation_monthly, on=['IATA', '월'], how='left')
    
    # 5. 최종 데이터 정형화 및 수치 타입 변환
    # 평점 점수(1.0, 2.0 등)를 '1점대', '2점대'와 같은 범주형 문자열로 변환합니다.
    df['평점대'] = df['평점'].apply(lambda x: f"{int(x)}점대" if pd.notnull(x) else "정보없음")
    
    # 성인가격과 쇼핑횟수는 시각화 시 수치 계산 오류를 막기 위해 숫자로 명확히 변환합니다.
    df['성인가격'] = pd.to_numeric(df['성인가격'], errors='coerce').fillna(0).astype(int)
    
    if '쇼핑횟수' in df.columns:
        # 문자열로 된 쇼핑 횟수를 정수형으로 변환 (Plotly 추세선 계산 시 필수)
        df['쇼핑횟수'] = pd.to_numeric(df['쇼핑횟수'], errors='coerce').fillna(0).astype(int)
    else:
        df['쇼핑횟수'] = 0
        
    return df

if __name__ == "__main__":
    # 이 스크립트를 직접 실행했을 때만 동작하는 테스트 코드입니다.
    print("--- 데이터 전처리 파이프라인 테스트 시작 ---")
    raw_data = load_all_data()
    print(f"로드된 원본 테이블 개수: {len(raw_data)}")
    
    final_df = preprocess_and_merge(raw_data)
    print(f"최종 병합 데이터 셋 크기: {final_df.shape[0]}행, {final_df.shape[1]}열")
    print("데이터 샘플 확인 (상위 3건):")
    print(final_df.head(3))
    print("--- 테스트 완료 ---")
