"""
测试StaticDataLoader加载combined_factors_df.parquet文件
"""
import sys
import pandas as pd
from pathlib import Path

# 添加qlib路径
sys.path.append('/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages')

from qlib.data.dataset.loader import StaticDataLoader

# 测试加载parquet文件
parquet_path = "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/git_ignore_folder/RD-Agent_workspace/6d2a12147c604c5e85232c907e76ac30/combined_factors_df.parquet"

if Path(parquet_path).exists():
    print("=== 测试StaticDataLoader ===")
    
    # 方式1: 直接传递文件路径
    loader1 = StaticDataLoader(parquet_path)
    data1 = loader1.load()
    print(f"方式1 - 直接路径加载:")
    print(f"  Shape: {data1.shape}")
    print(f"  Columns: {list(data1.columns[:3])}")
    
    # 方式2: 传递DataFrame
    df = pd.read_parquet(parquet_path)
    loader2 = StaticDataLoader(df)
    data2 = loader2.load()
    print(f"\n方式2 - DataFrame加载:")
    print(f"  Shape: {data2.shape}")
    
    # 方式3: 传递dict配置
    loader3 = StaticDataLoader({"feature": parquet_path})
    data3 = loader3.load()
    print(f"\n方式3 - Dict配置加载:")
    print(f"  Shape: {data3.shape}")
    print(f"  Columns structure: {data3.columns.nlevels} levels")
    
else:
    print(f"文件不存在: {parquet_path}")
