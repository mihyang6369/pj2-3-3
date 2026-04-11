import sys, os, json
sys.path.append(r'C:/Users/Administrator/Desktop/fcicb6/pj2/pj2-3-3')
from src.analytics_engine import AnalyticsEngine
engine = AnalyticsEngine()
print(json.dumps(engine.df.columns.tolist(), ensure_ascii=False))
print('동행 in columns?', '동행' in engine.df.columns)
