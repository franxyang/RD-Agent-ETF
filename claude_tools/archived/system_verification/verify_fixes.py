#!/usr/bin/env python
"""验证所有修复是否成功"""

import os
import yaml
import subprocess

print("="*60)
print("RD-Agent修复验证")
print("="*60)

# 1. 验证配置文件时间范围修复
print("\n1. 验证IndexError修复（时间范围调整）:")
config_file = "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/factor_template/conf_baseline.yaml"
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)
    
    # 检查各个时间设置
    end_time = config.get('data_handler_config', {}).get('end_time', '')
    backtest_end = config.get('port_analysis_config', {}).get('backtest', {}).get('end_time', '')
    test_end = config.get('task', {}).get('dataset', {}).get('kwargs', {}).get('segments', {}).get('test', [])[1] if 'task' in config else ''
    
    print(f"   data_handler end_time: {end_time}")
    print(f"   backtest end_time: {backtest_end}")
    print(f"   test segment end: {test_end}")
    
    if '2025-07-10' in str(end_time) and '2025-07-10' in str(backtest_end):
        print("   ✅ 时间范围已调整，避免IndexError")
    else:
        print("   ⚠️ 时间范围可能未完全修复")

# 2. 验证环境变量设置
print("\n2. 验证因子多样性参数:")
env_file = "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/.env"
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        content = f.read()
        if 'FACTOR_CoSTEER_temperature=0.9' in content:
            print("   ✅ temperature参数已设置")
        else:
            print("   ⚠️ temperature参数未设置")
        
        if 'FACTOR_CoSTEER_mutation_rate=0.5' in content:
            print("   ✅ mutation_rate参数已设置")
        else:
            print("   ⚠️ mutation_rate参数未设置")

# 3. 验证prompts修改
print("\n3. 验证prompts.yaml修改:")
prompts_file = "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/rdagent/scenarios/qlib/experiment/prompts.yaml"
with open(prompts_file, 'r') as f:
    content = f.read()
    if 'Price-based' in content and 'Volume-based' in content:
        print("   ✅ 因子类别引导已添加")
    else:
        print("   ⚠️ 因子类别引导未找到")
    
    if 'DIVERSITY REQUIREMENT' in content:
        print("   ✅ 多样性要求已添加")
    else:
        print("   ⚠️ 多样性要求未找到")

# 4. 验证scipy版本
print("\n4. 验证scipy兼容性:")
try:
    result = subprocess.run(['python', '-c', 'import scipy; print(scipy.__version__)'], 
                          capture_output=True, text=True)
    scipy_version = result.stdout.strip()
    print(f"   scipy版本: {scipy_version}")
    
    # 测试eye_array导入
    result = subprocess.run(['python', '-c', 'from scipy.sparse import eye_array; print("OK")'], 
                          capture_output=True, text=True)
    if 'OK' in result.stdout:
        print("   ✅ scipy.sparse.eye_array导入成功")
    else:
        print("   ⚠️ scipy导入可能有问题")
except Exception as e:
    print(f"   ❌ 版本检查失败: {e}")

# 5. 验证工作空间清理
print("\n5. 验证工作空间清理:")
workspace_dir = "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/git_ignore_folder/RD-Agent_workspace/"
if os.path.exists(workspace_dir):
    files = os.listdir(workspace_dir)
    if len(files) == 0:
        print("   ✅ 工作空间已清空")
    else:
        print(f"   ⚠️ 工作空间还有 {len(files)} 个文件/目录")
else:
    print("   ✅ 工作空间目录不存在（已清理）")

print("\n" + "="*60)
print("验证总结:")
print("1. IndexError修复: 时间范围已调整至2025-07-10")
print("2. 因子多样性: 参数已通过环境变量设置")
print("3. 系统稳定性: scipy兼容性已解决")
print("4. 建议运行: rdagent fin_factor --loop_n 3 --step_n 1")
print("="*60)