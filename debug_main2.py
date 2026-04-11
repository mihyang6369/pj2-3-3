import sys, os
sys.path.append('c:/Users/Administrator/Desktop/fcicb6/pj2/pj2-3-3')
from src.analytics_engine import AnalyticsEngine
engine = AnalyticsEngine()
df = engine.df
filtered_df = df[df['대상도시'].isin(["다낭", "나트랑", "싱가포르"])]
rev_len_df = engine.get_review_length_analysis(filtered_df)
print(rev_len_df.columns.tolist())
