#!/usr/bin/env python3
"""
验证方案A的实施效果
Author: Claude
Date: 2025-08-07
"""

import os
import sys
from pathlib import Path
import pandas as pd
import pickle

def main():
    print("=" * 80)
    print("🔍 方案A实施效果验证")
    print("=" * 80)
    
    results = {}
    
    # 1. 检查代码修复
    print("\n1️⃣ 代码修复检查:")
    
    factor_runner = Path("/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/developer/factor_runner.py")
    with open(factor_runner, 'r') as f:
        content = f.read()
    if "to_pickle" in content and "combined_factors_df.pkl" in content:
        print("   ✅ factor_runner.py: 已修复为pkl格式")
        results["factor_runner"] = True
    else:
        print("   ❌ factor_runner.py: 未修复")
        results["factor_runner"] = False
    
    model_runner = Path("/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/developer/model_runner.py")
    with open(model_runner, 'r') as f:
        content = f.read()
    if "to_pickle" in content and "combined_factors_df.pkl" in content:
        print("   ✅ model_runner.py: 已修复为pkl格式")
        results["model_runner"] = True
    else:
        print("   ❌ model_runner.py: 未修复")
        results["model_runner"] = False
    
    # 2. 检查文件转换
    print("\n2️⃣ 文件格式转换检查:")
    
    workspace_path = Path("/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/git_ignore_folder/RD-Agent_workspace")
    pkl_files = list(workspace_path.glob("*/combined_factors_df.pkl"))
    parquet_files = list(workspace_path.glob("*/combined_factors_df.parquet"))
    
    print(f"   ✅ PKL文件数量: {len(pkl_files)}")
    print(f"   {'✅' if len(parquet_files) == 0 else '❌'} Parquet文件清理: {len(parquet_files)}个剩余")
    
    results["pkl_files"] = len(pkl_files) > 0
    results["parquet_cleaned"] = len(parquet_files) == 0
    
    # 测试pkl文件可读性
    if pkl_files:
        try:
            test_file = pkl_files[0]
            with open(test_file, 'rb') as f:
                df = pickle.load(f)
            print(f"   ✅ PKL文件可读: {df.shape}")
            results["pkl_readable"] = True
        except Exception as e:
            print(f"   ❌ PKL文件读取失败: {e}")
            results["pkl_readable"] = False
    
    # 3. 检查配置文件
    print("\n3️⃣ 配置文件更新检查:")
    
    config_files = {
        "model_template": "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/model_template/conf_sota_factors_model.yaml",
        "combined_factors": "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors.yaml",
        "combined_sota": "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors_sota_model.yaml"
    }
    
    for name, path in config_files.items():
        with open(path, 'r') as f:
            content = f.read()
        
        if name == "model_template":
            if "combined_factors_df.pkl" in content:
                print(f"   ✅ {name}: 引用pkl格式")
                results[name] = True
            else:
                print(f"   ❌ {name}: 仍引用parquet")
                results[name] = False
        else:
            # 检查是否使用DataHandlerLP
            if "DataHandlerLP" in content and "NestedDataLoader" in content:
                print(f"   ✅ {name}: 使用DataHandlerLP + NestedDataLoader")
                results[name] = True
            else:
                print(f"   ❌ {name}: 未正确配置DataHandlerLP")
                results[name] = False
    
    # 4. 检查IC值
    print("\n4️⃣ IC值一致性检查:")
    
    ic_values = []
    for mlrun_dir in workspace_path.glob("*/mlruns/*/*/metrics/IC"):
        try:
            with open(mlrun_dir, 'r') as f:
                line = f.readline().strip()
                if line:
                    parts = line.split()
                    if len(parts) >= 2:
                        ic_value = float(parts[1])
                        ic_values.append(ic_value)
        except:
            pass
    
    if ic_values:
        unique_values = set(ic_values)
        if len(unique_values) == 1:
            print(f"   ⚠️  所有IC值相同: {list(unique_values)[0]} (需要新的实验验证)")
            results["ic_variance"] = False
        else:
            print(f"   ✅ IC值有差异: {len(unique_values)}个不同值")
            results["ic_variance"] = True
    else:
        print("   ℹ️  无历史IC值数据")
    
    # 5. 总结
    print("\n" + "=" * 80)
    print("📊 方案A实施总结")
    print("=" * 80)
    
    critical_checks = [
        results.get("factor_runner", False),
        results.get("model_runner", False),
        results.get("pkl_files", False),
        results.get("parquet_cleaned", False),
        results.get("model_template", False),
        results.get("combined_factors", False),
        results.get("combined_sota", False)
    ]
    
    if all(critical_checks):
        print("✅ 方案A已成功实施！")
        print("\n下一步建议:")
        print("1. 运行: rdagent fin_factor --loop_n 1 --step_n 1")
        print("2. 验证新的IC值与之前不同")
        print("3. 检查feature数量 > 158")
        return 0
    else:
        print("❌ 方案A实施不完整")
        print("\n需要修复的项目:")
        for key, value in results.items():
            if not value and key != "ic_variance":
                print(f"   - {key}")
        return 1

if __name__ == "__main__":
    sys.exit(main())