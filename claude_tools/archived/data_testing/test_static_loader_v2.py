"""
测试StaticDataLoader加载parquet文件 - 修正版
"""
import sys
import pandas as pd
from pathlib import Path

sys.path.append('/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages')

# 测试直接使用pandas读取parquet
parquet_path = "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/git_ignore_folder/RD-Agent_workspace/6d2a12147c604c5e85232c907e76ac30/combined_factors_df.parquet"

if Path(parquet_path).exists():
    print("=== 分析combined_factors_df.parquet ===")
    
    # 读取parquet文件
    df = pd.read_parquet(parquet_path)
    
    print(f"Shape: {df.shape}")
    print(f"Index levels: {df.index.names}")
    print(f"Columns: {list(df.columns)}")
    print(f"Column structure: {df.columns.nlevels} levels")
    
    # 显示前几行
    print("\n前5行数据:")
    print(df.head())
    
    # 检查数据类型
    print("\n数据类型:")
    print(df.dtypes)
    
    # 检查是否有MultiIndex列
    if df.columns.nlevels > 1:
        print("\n列的层级结构:")
        for col in df.columns[:3]:
            print(f"  {col}")
    
    # 统计信息
    print("\n基本统计:")
    print(f"非空值数量: {df.notna().sum().sum()}")
    print(f"空值数量: {df.isna().sum().sum()}")
    
else:
    print(f"文件不存在: {parquet_path}")
