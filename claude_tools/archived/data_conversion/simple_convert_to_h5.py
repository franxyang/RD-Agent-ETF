#!/usr/bin/env python
"""
简单的转换脚本：从qlib .bin文件读取数据并转换为HDF5格式
避免qlib版本兼容性问题，直接使用低级API
"""

import pandas as pd
import numpy as np
from pathlib import Path
import struct
from datetime import datetime

def read_bin_file(file_path):
    """读取qlib的.bin文件"""
    with open(file_path, 'rb') as f:
        data = f.read()
    # qlib的.bin文件是float32数组
    values = struct.unpack(f'{len(data)//4}f', data)
    return np.array(values, dtype=np.float32)

def load_calendars(calendar_path):
    """加载交易日历"""
    with open(calendar_path, 'r') as f:
        dates = [line.strip() for line in f if line.strip()]
    return pd.to_datetime(dates)

def load_instruments(instruments_path):
    """加载股票列表"""
    instruments = []
    with open(instruments_path, 'r') as f:
        for line in f:
            if line.strip():
                parts = line.strip().split('\t')
                if len(parts) >= 1:
                    instruments.append(parts[0])
    return instruments

# 路径设置
data_dir = Path("/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_final")
output_dir = Path("/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_h5")
output_dir.mkdir(parents=True, exist_ok=True)

# 加载日历和股票列表
print("加载交易日历...")
dates = load_calendars(data_dir / "calendars" / "day.txt")
print(f"交易日期数量: {len(dates)}")

print("加载股票列表...")
instruments = load_instruments(data_dir / "instruments" / "all.txt")
print(f"股票数量: {len(instruments)}")

# 定义要读取的字段
fields = ["open", "high", "low", "close", "volume"]

# 创建一个大的DataFrame来存储所有数据
all_data = []

print("开始读取数据...")
for i, instrument in enumerate(instruments):
    if i % 50 == 0:
        print(f"进度: {i}/{len(instruments)}")
    
    instrument_data = {}
    inst_dir = data_dir / "features" / instrument
    
    # 检查目录是否存在
    if not inst_dir.exists():
        print(f"警告: {instrument} 的数据目录不存在，跳过")
        continue
    
    # 先获取一个字段的长度来确定这个股票的数据长度
    first_field = None
    data_length = None
    
    for field in fields:
        bin_file = inst_dir / f"{field}.day.bin"
        if bin_file.exists():
            values = read_bin_file(bin_file)
            if first_field is None:
                first_field = field
                data_length = len(values)
                break
    
    if data_length is None:
        print(f"警告: {instrument} 没有找到任何数据文件，跳过")
        continue
    
    # 读取每个字段
    for field in fields:
        bin_file = inst_dir / f"{field}.day.bin"
        if bin_file.exists():
            values = read_bin_file(bin_file)
            # 确保所有字段长度一致
            if len(values) == data_length:
                instrument_data[field] = values
            else:
                print(f"警告: {instrument} 的 {field} 数据长度({len(values)})与预期({data_length})不一致")
    
    # 如果有数据，创建DataFrame
    if instrument_data:
        # 使用实际数据长度创建日期索引
        # 从日历的最后N个交易日
        if data_length <= len(dates):
            actual_dates = dates[-data_length:]
        else:
            # 如果数据长度超过日历长度，可能是基准指数包含更多历史数据
            # 我们只取日历范围内的数据
            for field in instrument_data:
                instrument_data[field] = instrument_data[field][-len(dates):]
            data_length = len(dates)
            actual_dates = dates
        
        df = pd.DataFrame(instrument_data, index=actual_dates)
        df['instrument'] = instrument
        all_data.append(df)

print("合并所有数据...")
# 合并所有数据
if all_data:
    combined_df = pd.concat(all_data, ignore_index=False)
    
    # 重置索引，创建MultiIndex
    combined_df = combined_df.reset_index()
    combined_df = combined_df.rename(columns={'index': 'datetime'})
    
    # 设置MultiIndex (datetime, instrument)
    combined_df = combined_df.set_index(['datetime', 'instrument'])
    combined_df = combined_df.sort_index()
    
    # 保存为HDF5
    output_file = output_dir / "daily_pv.h5"
    print(f"保存数据到 {output_file}...")
    combined_df.to_hdf(output_file, key="data", mode="w", complib='blosc', complevel=5)
    
    print(f"\n转换完成！")
    print(f"数据形状: {combined_df.shape}")
    print(f"时间范围: {combined_df.index.get_level_values('datetime').min()} 到 {combined_df.index.get_level_values('datetime').max()}")
    print(f"股票数量: {len(combined_df.index.get_level_values('instrument').unique())}")
    
    # 创建README
    readme_content = f"""# ETF数据说明

此目录包含从qlib标准.bin格式转换而来的ETF市场数据。

## 数据信息
- 数据源: /Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_final
- 时间范围: {combined_df.index.get_level_values('datetime').min().strftime('%Y-%m-%d')} 至 {combined_df.index.get_level_values('datetime').max().strftime('%Y-%m-%d')}
- 基准指数: 000852.csi (中证1000)
- 股票数量: {len(combined_df.index.get_level_values('instrument').unique())}
- 数据字段: {', '.join(combined_df.columns.tolist())}

## 文件格式
- daily_pv.h5: HDF5格式的日频价量数据
- MultiIndex结构: (datetime, instrument)
- 数据类型: float32

## 使用方法
```python
import pandas as pd
data = pd.read_hdf('daily_pv.h5', key='data')
```
"""
    
    readme_file = output_dir / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"README文件已创建: {readme_file}")
else:
    print("错误：没有成功读取任何数据")