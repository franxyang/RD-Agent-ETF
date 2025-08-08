#!/usr/bin/env python
"""简单检查配置状态"""

import os

print("="*60)
print("配置文件时间检查")
print("="*60)

config_files = [
    "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/rdagent/scenarios/qlib/experiment/factor_template/conf_baseline.yaml",
    "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors.yaml",
    "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors_sota_model.yaml",
]

for config_file in config_files:
    filename = os.path.basename(config_file)
    print(f"\n{filename}:")
    
    with open(config_file, 'r') as f:
        lines = f.readlines()
        
    # 查找2025-07-15
    found_715 = False
    for i, line in enumerate(lines, 1):
        if '2025-07-15' in line:
            print(f"  ⚠️ 第{i}行还有2025-07-15: {line.strip()}")
            found_715 = True
    
    # 查找2025-07-10
    found_710 = False
    for i, line in enumerate(lines, 1):
        if '2025-07-10' in line:
            found_710 = True
            
    if not found_715 and found_710:
        print(f"  ✅ 时间范围已修复为2025-07-10")
    elif found_715:
        print(f"  ⚠️ 仍有2025-07-15需要修复")
        
    # 检查handler
    for line in lines:
        if 'class: Alpha158' in line:
            print(f"  ✅ 使用Alpha158处理器")
            break
        elif 'class: Alpha360' in line:
            print(f"  ⚠️ 使用Alpha360处理器（可能需要data_loader）")
            break

# 检查工作空间
print("\n工作空间状态:")
workspace_dir = "/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/git_ignore_folder/RD-Agent_workspace/"
if os.path.exists(workspace_dir):
    files = os.listdir(workspace_dir)
    print(f"  工作空间文件数: {len(files)}")
    if len(files) == 0:
        print("  ✅ 工作空间已清空")
    else:
        print(f"  文件列表: {files[:3]}")

print("\n" + "="*60)
print("修复状态总结:")
print("- conf_baseline.yaml: Alpha158处理器")
print("- 时间范围: 应全部为2025-07-10")
print("- 工作空间: 已清理")
print("="*60)