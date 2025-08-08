#!/usr/bin/env python3
"""
测试label修复是否成功
Author: Claude
Date: 2025-08-07
"""

import yaml
import sys
from pathlib import Path

def check_label_config():
    """检查label配置是否正确"""
    print("=" * 80)
    print("🔍 检查Label配置修复")
    print("=" * 80)
    
    config_files = {
        "conf_combined_factors.yaml": "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors.yaml",
        "conf_combined_factors_sota_model.yaml": "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors_sota_model.yaml"
    }
    
    all_correct = True
    
    for name, path in config_files.items():
        print(f"\n检查 {name}:")
        try:
            with open(path, 'r') as f:
                config = yaml.safe_load(f)
            
            # 导航到handler配置
            handler = config.get("task", {}).get("dataset", {}).get("kwargs", {}).get("handler", {})
            
            # 检查是否使用DataHandlerLP
            if handler.get("class") == "DataHandlerLP":
                print(f"  ✅ 使用DataHandlerLP")
                
                # 检查data_loader配置
                data_loader = handler.get("kwargs", {}).get("data_loader", {})
                if data_loader:
                    dataloader_l = data_loader.get("kwargs", {}).get("dataloader_l", [])
                    
                    # 检查Alpha158DL的label配置
                    alpha158_found = False
                    label_found = False
                    
                    for loader in dataloader_l:
                        if "Alpha158DL" in loader.get("class", ""):
                            alpha158_found = True
                            loader_config = loader.get("kwargs", {}).get("config", {})
                            if "label" in loader_config:
                                label_found = True
                                label_def = loader_config["label"]
                                print(f"  ✅ Alpha158DL找到")
                                print(f"  ✅ Label已定义: {label_def[0][0] if label_def else 'Empty'}")
                            else:
                                print(f"  ❌ Alpha158DL缺少label定义")
                                all_correct = False
                    
                    if not alpha158_found:
                        print(f"  ❌ 未找到Alpha158DL")
                        all_correct = False
                    elif not label_found:
                        print(f"  ❌ Alpha158DL中未找到label")
                        all_correct = False
                        
                    # 检查StaticDataLoader
                    static_found = False
                    for loader in dataloader_l:
                        if "StaticDataLoader" in loader.get("class", ""):
                            static_found = True
                            pkl_config = loader.get("kwargs", {}).get("config", "")
                            if "combined_factors_df.pkl" in pkl_config:
                                print(f"  ✅ StaticDataLoader配置正确: {pkl_config}")
                            else:
                                print(f"  ⚠️  StaticDataLoader配置: {pkl_config}")
                    
                    if not static_found:
                        print(f"  ❌ 未找到StaticDataLoader")
                        all_correct = False
                else:
                    print(f"  ❌ 没有data_loader配置")
                    all_correct = False
            else:
                print(f"  ❌ 未使用DataHandlerLP，当前: {handler.get('class')}")
                all_correct = False
                
        except Exception as e:
            print(f"  ❌ 读取配置失败: {e}")
            all_correct = False
    
    print("\n" + "=" * 80)
    if all_correct:
        print("✅ Label配置修复成功！")
        print("\n建议的下一步:")
        print("1. 运行: rdagent fin_factor --loop_n 1")
        print("2. 观察是否还有KeyError: 'label'错误")
        return 0
    else:
        print("❌ Label配置仍有问题")
        print("\n问题原因:")
        print("Alpha158DL需要在kwargs.config中定义label")
        print("格式如下:")
        print("""
kwargs:
    config:
        label:
            - ["Ref($close, -2) / Ref($close, -1) - 1"]
            - ["LABEL0"]
""")
        return 1

if __name__ == "__main__":
    sys.exit(check_label_config())