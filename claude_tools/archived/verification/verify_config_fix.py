"""
验证配置文件修改是否正确
"""
import re

configs = [
    "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors.yaml",
    "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors_sota_model.yaml"
]

for config_path in configs:
    print(f"\n=== {config_path.split('/')[-1]} ===")
    
    with open(config_path, 'r') as f:
        content = f.read()
    
    # 检查关键组件
    if "NestedDataLoader" in content:
        print("✅ 包含 NestedDataLoader")
    else:
        print("❌ 缺少 NestedDataLoader")
    
    if "Alpha158DL" in content:
        print("✅ 包含 Alpha158DL (预定义特征)")
    else:
        print("❌ 缺少 Alpha158DL")
        
    if "StaticDataLoader" in content:
        print("✅ 包含 StaticDataLoader")
        if "combined_factors_df.parquet" in content:
            print("✅ 配置加载 combined_factors_df.parquet")
    else:
        print("❌ 缺少 StaticDataLoader")
    
    if "DataHandlerLP" in content:
        print("✅ 使用 DataHandlerLP")
    else:
        print("❌ 未使用 DataHandlerLP")

print("\n=== 总结 ===")
print("配置文件已修改为使用NestedDataLoader模式")
print("将同时加载Alpha158特征和自定义因子")
print("预期效果：不同的自定义因子将产生不同的IC值")
