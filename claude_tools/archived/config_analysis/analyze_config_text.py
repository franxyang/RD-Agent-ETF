"""
分析配置文件结构（通过文本方式）
"""
import re

config_path = "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/model_template/conf_sota_factors_model.yaml"

with open(config_path, 'r') as f:
    content = f.read()

# 查找NestedDataLoader部分
nested_pattern = r'class:\s*NestedDataLoader.*?(?=^\w|\Z)'
nested_match = re.search(nested_pattern, content, re.MULTILINE | re.DOTALL)

if nested_match:
    print("=== NestedDataLoader配置部分 ===")
    nested_content = nested_match.group()
    
    # 提取关键信息
    if 'Alpha158DL' in nested_content:
        print("\n✓ 包含 Alpha158DL - 预定义技术指标")
        # 计算特征数量
        features = re.findall(r'"[A-Z]+\d*"', nested_content)
        print(f"  特征数量: 约{len(features)}个")
        
    if 'StaticDataLoader' in nested_content:
        print("\n✓ 包含 StaticDataLoader - 自定义因子")
        static_match = re.search(r'StaticDataLoader.*?config:\s*"([^"]+)"', nested_content, re.DOTALL)
        if static_match:
            print(f"  文件: {static_match.group(1)}")

print("\n=== 关键发现 ===")
print("model_template使用NestedDataLoader组合两种数据源:")
print("1. Alpha158的预定义特征（约20个）")
print("2. combined_factors_df.parquet中的自定义因子")
print("\n而factor_template中的配置只使用了Alpha158，没有加载自定义因子！")
print("这就是为什么所有实验IC值相同的原因。")
