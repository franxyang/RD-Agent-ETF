#!/usr/bin/env python3
"""
Verify that all fixes have been applied correctly
Author: Claude
Date: 2025-08-07
"""

import os
import sys
from pathlib import Path
import pandas as pd
import pickle
import yaml

def check_code_fixes():
    """Check if code files have been fixed"""
    print("=" * 80)
    print("🔧 CHECKING CODE FIXES")
    print("=" * 80)
    
    fixes_status = {}
    
    # Check factor_runner.py
    factor_runner = Path("/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/developer/factor_runner.py")
    with open(factor_runner, 'r') as f:
        content = f.read()
    
    if "to_pickle" in content and "combined_factors_df.pkl" in content:
        print("✅ factor_runner.py: Uses to_pickle() and .pkl format")
        fixes_status["factor_runner"] = True
    else:
        print("❌ factor_runner.py: Still using parquet")
        fixes_status["factor_runner"] = False
    
    # Check model_runner.py
    model_runner = Path("/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/developer/model_runner.py")
    with open(model_runner, 'r') as f:
        content = f.read()
    
    if "to_pickle" in content and "combined_factors_df.pkl" in content:
        print("✅ model_runner.py: Uses to_pickle() and .pkl format")
        fixes_status["model_runner"] = True
    else:
        print("❌ model_runner.py: Still using parquet")
        fixes_status["model_runner"] = False
    
    return all(fixes_status.values())

def check_config_files():
    """Check if configuration files reference .pkl"""
    print("\n" + "=" * 80)
    print("⚙️  CHECKING CONFIGURATION FILES")
    print("=" * 80)
    
    config_status = {}
    
    # Check model template config
    model_config = Path("/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/model_template/conf_sota_factors_model.yaml")
    with open(model_config, 'r') as f:
        content = f.read()
    
    if "combined_factors_df.pkl" in content:
        print("✅ conf_sota_factors_model.yaml: References .pkl format")
        config_status["model_template"] = True
    else:
        print("❌ conf_sota_factors_model.yaml: Still references .parquet")
        config_status["model_template"] = False
    
    return all(config_status.values())

def check_workspace_files():
    """Check if workspace files have been converted"""
    print("\n" + "=" * 80)
    print("📁 CHECKING WORKSPACE FILES")
    print("=" * 80)
    
    workspace_path = Path("/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/git_ignore_folder/RD-Agent_workspace")
    
    pkl_files = list(workspace_path.glob("*/combined_factors_df.pkl"))
    parquet_files = list(workspace_path.glob("*/combined_factors_df.parquet"))
    backup_files = list(workspace_path.glob("*/combined_factors_df.parquet.bak"))
    
    print(f"✅ PKL files found: {len(pkl_files)}")
    print(f"✅ Backup files created: {len(backup_files)}")
    print(f"{'✅' if len(parquet_files) == 0 else '❌'} Original parquet files removed: {len(parquet_files)} remaining")
    
    # Test loading a pkl file
    if pkl_files:
        test_file = pkl_files[0]
        try:
            df = pd.read_pickle(test_file)
            print(f"\n✅ Test loading pkl file: Success")
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {len(df.columns)} features")
            
            # Check if it's loadable with pickle.load (like qlib does)
            with open(test_file, 'rb') as f:
                df_pickle = pickle.load(f)
            print(f"✅ Compatible with pickle.load(): Yes")
            
        except Exception as e:
            print(f"❌ Error loading pkl file: {e}")
            return False
    
    return len(pkl_files) > 0 and len(parquet_files) == 0

def check_alpha158_config():
    """Check if Alpha158 configs need updating"""
    print("\n" + "=" * 80)
    print("🔍 CHECKING ALPHA158 CONFIGURATION")
    print("=" * 80)
    
    config_path = Path("/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/factor_template")
    
    configs_to_check = [
        "conf_combined_factors.yaml",
        "conf_combined_factors_sota_model.yaml"
    ]
    
    recommendations = []
    
    for config_name in configs_to_check:
        config_file = config_path / config_name
        if config_file.exists():
            with open(config_file, 'r') as f:
                try:
                    config = yaml.safe_load(f)
                    handler = config.get("task", {}).get("dataset", {}).get("kwargs", {}).get("handler", {})
                    handler_class = handler.get("class", "")
                    
                    if handler_class == "Alpha158":
                        print(f"⚠️  {config_name}: Uses Alpha158 without data_loader")
                        recommendations.append(f"Update {config_name} to use DataHandlerLP with NestedDataLoader")
                    else:
                        print(f"✅ {config_name}: {handler_class}")
                except:
                    print(f"⚠️  {config_name}: Could not parse YAML")
    
    if recommendations:
        print("\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   - {rec}")
    
    return len(recommendations) == 0

def main():
    print("\n" + "=" * 80)
    print("🔍 RD-AGENT FIX VERIFICATION")
    print("=" * 80)
    print("Checking if all fixes have been applied correctly...\n")
    
    results = {
        "code_fixes": check_code_fixes(),
        "config_files": check_config_files(),
        "workspace_files": check_workspace_files(),
        "alpha158_config": check_alpha158_config()
    }
    
    print("\n" + "=" * 80)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 80)
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check.replace('_', ' ').title()}")
    
    if all_passed:
        print("\n" + "=" * 80)
        print("🎉 ALL FIXES VERIFIED SUCCESSFULLY!")
        print("=" * 80)
        print("\n✅ The system is now ready for testing.")
        print("   Next step: Run 'rdagent fin_factor --loop_n 1' to test")
    else:
        print("\n" + "=" * 80)
        print("⚠️  SOME FIXES ARE INCOMPLETE")
        print("=" * 80)
        print("\n❌ Please review the failed checks above.")
        
        if not results["alpha158_config"]:
            print("\n⚠️  IMPORTANT: Alpha158 configuration issue remains.")
            print("   Custom factors won't load until DataHandlerLP is configured.")
            print("   See recommendations above for required changes.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())