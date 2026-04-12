import pandas as pd
import os

def get_data_info():
    base_path = r'c:\Users\Administrator\Desktop\fcicb6\pj2\pj2-3-3\data'
    
    # 1. Reviews
    reviews_path = os.path.join(base_path, 'hanatour_reviews.csv')
    df_reviews = pd.read_csv(reviews_path)
    print(f"Reviews: {df_reviews.shape}")
    print(f"Reviews Date Range: {df_reviews['작성일'].min()} to {df_reviews['작성일'].max()}")
    
    # 2. Aviation
    aviation_path = os.path.join(base_path, 'merged_aviation_performance.csv')
    df_aviation = pd.read_csv(aviation_path)
    print(f"Aviation: {df_aviation.shape}")
    
    # 3. Integrated (Danang as sample)
    integrated_path = os.path.join(base_path, 'hanatour_danang_integrated.csv')
    df_danang = pd.read_csv(integrated_path)
    print(f"Integrated (Danang): {df_danang.shape}")

if __name__ == "__main__":
    get_data_info()
