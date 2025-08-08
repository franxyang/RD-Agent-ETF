#!/usr/bin/env python
"""验证配置文件修复是否成功"""

import os
import yaml

def check_config_file(file_path, expected_value):
    """检查配置文件中的provider_uri值"""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
            actual_value = config.get('qlib_init', {}).get('provider_uri', '')
            status = "✅" if actual_value == expected_value else "❌"
            print(f"{status} {file_path}")
            print(f"   provider_uri: {actual_value}")
            return actual_value == expected_value
    else:
        print(f"⚠️  {file_path} 不存在")
        return None

print("="*60)
print("配置文件修复验证")
print("="*60)

expected_path = "/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_final"

# 检查已安装包的配置
print("\n1. 已安装包配置（实际运行时使用）：")
check_config_file(
    "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/factor_template/conf_baseline.yaml",
    expected_path
)

# 检查源代码配置
print("\n2. 源代码配置：")
check_config_file(
    "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/rdagent/scenarios/qlib/experiment/factor_template/conf_baseline.yaml",
    expected_path
)

# 检查构建缓存是否已清理
print("\n3. 构建缓存状态：")
build_dir = "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/build/"
if not os.path.exists(build_dir):
    print("✅ 构建缓存已清理")
else:
    print("❌ 构建缓存仍存在")

# 检查工作空间是否已清理
print("\n4. 工作空间状态：")
workspace_dir = "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/git_ignore_folder/RD-Agent_workspace/"
if os.path.exists(workspace_dir):
    files = os.listdir(workspace_dir)
    if len(files) == 0:
        print("✅ 工作空间已清空")
    else:
        print(f"❌ 工作空间还有 {len(files)} 个文件/目录")
else:
    print("⚠️  工作空间目录不存在")

print("\n" + "="*60)
print("修复总结：")
print("如果以上所有检查都显示✅，则修复成功！")
print("您现在可以重新运行 rdagent fin_factor")
print("="*60)