# 하나투어 항공 및 여행 실적 통합 대시보드 기획 프롬프트

## 1. 개요 (Overview)
본 대시보드는 하나투어의 해외 여행 상품 데이터와 국토교통부/인천공항공사의 항공 운항 실적을 결합하여, 코로나 이후의 시장 회복 및 타겟 도시(다낭, 나트랑, 싱가포르)의 성과를 다각도로 분석하기 위해 구축되었습니다.

## 2. 주요 분석 목표
- **항공 시장 분석**: 코로나 팬데믹 이후 현재의 여객 수 및 운항 수 측정.
- **타겟 도시 집중 비교**: 전략적 중요도가 높은 3개 도시(다낭, 나트랑, 싱가포르)의 경쟁 우위 및 성장성 대조.
- **예약 상품 및 고객 반응 연계**: 실제 예약 실적과 리뷰 평점을 결합한 제품 경쟁력 평가.
- **데이터 정합성 및 성능**: 2025년 최신 데이터를 포함하며, 대용량 리뷰 데이터 처리 시 메모리 안정성 확보.

## 3. 화면 구성 및 주요 기능 (Tab 구조)

### [Tab 1] 코로나 이후 항공 시장 (Historical Trends)
- **사용 파일**: C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\processed_aviation_performance.csv, C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\merged_overseas_destination.csv
- **목적**: 거시적인 항공 시장 추세 파악.
- **주요 차트**:
  - 연도별 전체 여객 수 트렌드 (2020~2025).
  - 월별 시계열 여객 추이
  - 국가별 여객 누적 실적(10위까지)
  - 도시별 여객 누적 실적(10위까지)

### [Tab 2] 타겟 도시 항공 모니터링 (Target City Analysis)
- **기간**: 2020~2025
- **사용 파일**: C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\processed_aviation_performance.csv C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\merged_overseas_destination.csv
- **목적**: 다낭, 나트랑, 싱가포르의 실적 실시간 모니터링.
- **주요 차트**:
  - 3개 도시 통합 월별 선 그래프.
  - 연도별 누적 막대 차트 (2020~2025).
  - 도시별 상위 항공사 비중 (Top 3).


### [Tab 3] 종합 핵심 지표 (Summary KPIs)
- **사용 파일**: C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_all_itineraries.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_danang_airtel_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_danang_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_danang_tour_ticket_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_nhatrang_airtel_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_nhatrang_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_nhatrang_tour_ticket_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_singapore_airtel_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_singapore_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_singapore_tour_ticket_integrated.csv
- **목적**: 데이터 EDA
- **참고 파일**: C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\doc\comprehensive_eda_report.md
- **처리 로직**: 메모리 오류 방지를 위해 대용량 텍스트 컬럼('내용', '리뷰요약') 제거 후 병합.
- **레이아웃**: 2열
- **주석**: 모든 시각화에 50자 이상의 해석과 인사이트를 추가

### [Tab 4] 상품 및 리스크 현황 (Product & Risk)
- **사용 파일**: C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_all_itineraries.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_danang_airtel_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_danang_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_danang_tour_ticket_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_nhatrang_airtel_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_nhatrang_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_nhatrang_tour_ticket_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_singapore_airtel_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_singapore_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_singapore_tour_ticket_integrated.csv
C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_reviews.csv
- **목적**: 세부 상품별 실적 및 부정적 시나리오 관리.
- 추가 포함 내용
  - 여행일정 선호도
  

### [Tab 5] 일정 및 리뷰 분석 (Review Insights)
- **사용 파일**: C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_reviews.csv
- C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_all_itineraries.csv
- **목적**: 고객 평점 기반 히트맵 및 키워드 분석.
- 포함 내용
  - 요약
    - 도시별 리뷰 수
      - 도시별 리뷰수를 평균 평점과, 1~3점대 저평점 비중 표로 첨부
    - 월별 리뷰량
  - 리뷰 요약
    - C:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data\hanatour_reviews.csv의 리뷰요약1~5 열의 등장 빈도를 순위별로 확인
    - TF-IDF를 활용한 리뷰 요약
      - 긍정 대표 키워드
      - 부정 대표 키워드
        -# 조사, 너무, 많은 등 불용어 배제 
    - 상품코드별 리뷰수와 평균평점, 저평점비중으로 리스크 순위 파악
      - 리뷰 데이터와 일정 데이터 함께 사용하여 어떠한 세부 일정이 있는지도 같이 볼 수 있게 할 것
    - 연령대별 리뷰 분포
    - 도시별 평균 평점
    - 동행별 평균 평점
    - 연령대별 평균 평점
  - 평점 히트맵

## 4. 데이터 파이프라인 (Data Pipeline)
- **Raw Data**: `data/w/` 내 연도별 CSV 파일.
- **Pre-processing**: 
  - `re-merge_aviation.py`: 다중 연도 데이터의 컬럼명 표준화('년도'/'연도' 통합) 및 따옴표 제거 클렌징.
  - `enrich_aviation.py`: IATA 코드를 기반으로 도시(City), 국가(Country), 5대 지역(Region) 정보 보강.
- **Final Storage**: `data/processed_aviation_performance.csv`.

## 5. 기술 스택 (Technology Stack)
- **Frontend**: Streamlit
- **Visualization**: Plotly Express
- **Data Engine**: Pandas
- **Runtime**: Python 3.x (uv 가상환경)
