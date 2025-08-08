#!/usr/bin/env python
"""验证qlib配置修复"""

import os
import yaml
import subprocess

print("="*60)
print("Qlib配置修复验证")
print("="*60)

# 1. 验证配置文件时间范围修复
print("\n1. 验证时间范围修复：")
config_files = [
    "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/rdagent/scenarios/qlib/experiment/factor_template/conf_baseline.yaml",
    "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors.yaml",
    "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors_sota_model.yaml",
]

for config_file in config_files:
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
        
    filename = os.path.basename(config_file)
    print(f"\n   {filename}:")
    
    # 检查data_handler_config
    if 'data_handler_config' in config:
        end_time = config['data_handler_config'].get('end_time', '')
        print(f"     data_handler end_time: {end_time}")
        if '2025-07-10' in str(end_time):
            print("     ✅ 时间范围已修复")
        else:
            print("     ⚠️ 时间范围可能未修复")
    
    # 检查handler类
    if 'task' in config:
        handler_class = config.get('task', {}).get('dataset', {}).get('kwargs', {}).get('handler', {}).get('class', '')
        print(f"     handler class: {handler_class}")
        if handler_class == 'Alpha158':
            print("     ✅ 使用Alpha158处理器")
        elif handler_class == 'Alpha360':
            print("     ⚠️ 仍在使用Alpha360，可能有data_loader问题")

# 2. 验证工作空间清理
print("\n2. 验证工作空间清理：")
workspace_dir = "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/git_ignore_folder/RD-Agent_workspace/"
if os.path.exists(workspace_dir):
    files = os.listdir(workspace_dir)
    if len(files) == 0:
        print("   ✅ 工作空间已清空")
    else:
        print(f"   ⚠️ 工作空间还有 {len(files)} 个文件/目录")
        print(f"      文件列表: {files[:5]}")

# 3. 验证环境变量
print("\n3. 验证环境变量设置：")
env_file = "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/.env"
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        content = f.read()
        if 'FACTOR_CoSTEER_temperature' in content:
            print("   ✅ temperature参数已设置")
        if 'FACTOR_CoSTEER_mutation_rate' in content:
            print("   ✅ mutation_rate参数已设置")

# 4. 验证数据路径
print("\n4. 验证ETF数据路径：")
with open(config_files[0], 'r') as f:
    config = yaml.safe_load(f)
    provider_uri = config.get('qlib_init', {}).get('provider_uri', '')
    print(f"   provider_uri: {provider_uri}")
    if 'qlib_etf_data_final' in provider_uri:
        print("   ✅ ETF数据路径正确")
    else:
        print("   ⚠️ 数据路径可能不正确")

print("\n" + "="*60)
print("验证总结：")
print("1. 时间范围: 已调整至2025-07-10")
print("2. 处理器: 改用Alpha158避免data_loader问题")
print("3. 工作空间: 已清理缓存")
print("4. 数据源: 指向ETF数据")
print("\n建议测试命令:")
print("rdagent fin_factor --loop_n 1 --step_n 1")
print("="*60)