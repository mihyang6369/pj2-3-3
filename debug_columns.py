import sys, os
sys.path.append('c:/Users/Administrator/Desktop/fcicb6/pj2/pj2-3-3')
from src.analytics_engine import AnalyticsEngine
engine = AnalyticsEngine()
print('Columns:', engine.df.columns.tolist())
print('Sample rows:')
print(engine.df.head())
