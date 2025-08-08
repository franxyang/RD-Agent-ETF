#!/usr/bin/env python
"""
将qlib的.bin格式数据转换为RD-Agent需要的HDF5格式
使用qlib标准方法从qlib_etf_data_final读取数据并生成daily_pv.h5
"""

import qlib
from qlib.data import D
import pandas as pd
from pathlib import Path

# 初始化qlib，指向我们的ETF数据，禁用并行处理
import os
os.environ['QLIB_DISABLE_PARALLEL'] = '1'  # 禁用并行处理避免兼容性问题

qlib.init(provider_uri="/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_final", region="cn")

# 获取所有可用的股票列表
instruments = D.list_instruments({
    "market": "all", 
    "filter_pipe": [],
})

print(f"找到 {len(instruments)} 个可用的ETF/指数")

# 定义要提取的字段 - 注意momentum_20d是我们自定义的字段
fields = ["$open", "$high", "$low", "$close", "$volume", "$factor"]

# 尝试分批处理以避免内存问题
print("正在提取数据...")
try:
    # 先尝试读取一小部分数据测试
    test_instruments = list(instruments)[:5]
    test_data = D.features(
        instruments=test_instruments,
        fields=fields,
        start_time="2015-01-01",
        end_time="2015-01-10",
        freq="day"
    )
    print(f"测试数据读取成功，形状: {test_data.shape}")
    
    # 如果测试成功，读取全部数据
    data = D.features(
        instruments=instruments,
        fields=fields,
        start_time="2015-01-01",
        end_time="2025-07-15",
        freq="day"
    )
except Exception as e:
    print(f"读取数据时出错: {e}")
    print("尝试使用基础字段...")
    # 如果失败，只使用基础字段
    fields = ["$open", "$high", "$low", "$close", "$volume"]
    data = D.features(
        instruments=instruments,
        fields=fields,
        start_time="2015-01-01", 
        end_time="2025-07-15",
        freq="day"
    )

# 调整数据格式：交换层级并排序
# RD-Agent期望的格式是(datetime, instrument)的MultiIndex
data = data.swaplevel().sort_index()

# 保存为HDF5格式
output_dir = Path("/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_h5")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "daily_pv.h5"
print(f"正在保存数据到 {output_file}...")
data.to_hdf(output_file, key="data", mode="w")

# 验证数据
print(f"\n数据保存成功！")
print(f"数据形状: {data.shape}")
print(f"时间范围: {data.index.get_level_values('datetime').min()} 到 {data.index.get_level_values('datetime').max()}")
print(f"股票数量: {len(data.index.get_level_values('instrument').unique())}")

# 创建README文件
readme_content = f"""# ETF数据说明

此目录包含从qlib标准.bin格式转换而来的ETF市场数据。

## 数据信息
- 数据源: /Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_final
- 时间范围: 2015-01-01 至 2025-07-15
- 基准指数: 000852.csi (中证1000)
- 股票数量: {len(data.index.get_level_values('instrument').unique())}
- 数据字段: open, high, low, close, volume, factor

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

print(f"\nREADME文件已创建: {readme_file}")