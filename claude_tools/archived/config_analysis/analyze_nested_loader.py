"""
分析NestedDataLoader如何组合Alpha158和自定义因子
"""
import yaml
from pathlib import Path

# 读取包含NestedDataLoader的配置文件
config_path = "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/model_template/conf_sota_factors_model.yaml"

with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

print("=== 分析NestedDataLoader配置 ===\n")

# 提取data_loader配置
data_loader_config = config['data_handler_config']['data_loader']

print(f"DataLoader类: {data_loader_config['class']}")
print(f"DataLoader参数:")

# 分析dataloader_l列表
dataloaders = data_loader_config['kwargs']['dataloader_l']
print(f"\n包含 {len(dataloaders)} 个子DataLoader:")

for i, loader in enumerate(dataloaders, 1):
    print(f"\n{i}. {loader['class']}")
    if 'Alpha158DL' in loader['class']:
        feature_config = loader['kwargs']['config']['feature']
        print(f"   - 特征数量: {len(feature_config[0])} 个表达式")
        print(f"   - 特征名称: {feature_config[1][:5]}... 等{len(feature_config[1])}个")
    elif 'StaticDataLoader' in loader['class']:
        print(f"   - 配置: {loader['kwargs']['config']}")
        print(f"   - 说明: 加载预计算的自定义因子文件")

print("\n=== 关键发现 ===")
print("1. NestedDataLoader组合了两个数据源:")
print("   - Alpha158DL: 提供20个预定义的技术指标特征")
print("   - StaticDataLoader: 加载combined_factors_df.parquet中的自定义因子")
print("2. 这两组特征会被合并成一个DataFrame供模型训练使用")
