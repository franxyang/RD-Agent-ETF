#!/usr/bin/env python
"""测试qlib数据是否可以正常访问"""

import qlib
from qlib.data import D

print("测试qlib数据访问...")

# 初始化qlib
provider_uri = "/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_final"
print(f"数据路径: {provider_uri}")

qlib.init(provider_uri=provider_uri, region="cn")

# 列出可用的股票
instruments = D.list_instruments({
    "market": "all",
    "filter_pipe": [],
})

print(f"\n找到 {len(instruments)} 个股票/指数")
print(f"前5个: {list(instruments)[:5]}")

# 测试读取数据
print("\n测试读取000852.csi (中证1000) 数据...")
try:
    data = D.features(
        instruments=["000852.csi"],
        fields=["$open", "$high", "$low", "$close", "$volume"],
        start_time="2015-01-05",
        end_time="2015-01-10",
        freq="day"
    )
    print(f"数据形状: {data.shape}")
    print(f"数据示例:\n{data.head()}")
    print("\n✅ 数据访问成功！")
except Exception as e:
    print(f"\n❌ 数据访问失败: {e}")

print("\n测试完成")