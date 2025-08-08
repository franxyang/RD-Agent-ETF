#!/usr/bin/env python3
"""
Comprehensive Analysis of Custom Factor Loading Issue in RD-Agent
Author: Claude
Date: 2025-08-07
Purpose: Analyze why custom factors are not being loaded in qlib backtesting
"""

import os
import sys
import yaml
import pandas as pd
import numpy as np
from pathlib import Path
import pickle
import pyarrow.parquet as pq
from datetime import datetime
import json

class FactorLoadingAnalyzer:
    def __init__(self):
        self.base_path = Path("/Users/handsomedoge/Documents/CITIC_quant/RD-Agent")
        self.workspace_path = self.base_path / "git_ignore_folder/RD-Agent_workspace"
        self.log_path = self.base_path / "log"
        self.config_path = Path("/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/factor_template")
        
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "issues_found": [],
            "workspaces_analyzed": 0,
            "ic_values": [],
            "file_formats": {},
            "config_analysis": {},
            "recommendations": []
        }
    
    def analyze_workspaces(self):
        """Analyze all workspaces for factor files"""
        print("=" * 80)
        print("📁 ANALYZING WORKSPACES")
        print("=" * 80)
        
        workspace_dirs = list(self.workspace_path.glob("*"))
        self.analysis_results["workspaces_analyzed"] = len(workspace_dirs)
        
        for workspace in workspace_dirs:
            if workspace.is_dir():
                self._analyze_single_workspace(workspace)
        
        print(f"\n✅ Analyzed {len(workspace_dirs)} workspaces")
        return self.analysis_results["file_formats"]
    
    def _analyze_single_workspace(self, workspace: Path):
        """Analyze a single workspace"""
        workspace_id = workspace.name
        
        # Check for combined_factors files
        parquet_file = workspace / "combined_factors_df.parquet"
        pkl_file = workspace / "combined_factors_df.pkl"
        
        if parquet_file.exists():
            size = parquet_file.stat().st_size / (1024 * 1024)  # MB
            mtime = datetime.fromtimestamp(parquet_file.stat().st_mtime)
            
            # Try to read the parquet file
            try:
                df = pd.read_parquet(parquet_file)
                num_factors = len(df.columns) if hasattr(df, 'columns') else 0
                num_rows = len(df)
                
                self.analysis_results["file_formats"][workspace_id] = {
                    "format": "parquet",
                    "size_mb": round(size, 2),
                    "modified": mtime.isoformat(),
                    "num_factors": num_factors,
                    "num_rows": num_rows,
                    "factor_names": list(df.columns) if hasattr(df, 'columns') else []
                }
                
                print(f"  📊 {workspace_id[:8]}... : PARQUET ({num_factors} factors, {num_rows:,} rows)")
            except Exception as e:
                self.analysis_results["file_formats"][workspace_id] = {
                    "format": "parquet",
                    "error": str(e)
                }
                print(f"  ❌ {workspace_id[:8]}... : PARQUET (Error reading: {e})")
        
        elif pkl_file.exists():
            size = pkl_file.stat().st_size / (1024 * 1024)  # MB
            mtime = datetime.fromtimestamp(pkl_file.stat().st_mtime)
            
            try:
                with open(pkl_file, 'rb') as f:
                    df = pickle.load(f)
                num_factors = len(df.columns) if hasattr(df, 'columns') else 0
                num_rows = len(df)
                
                self.analysis_results["file_formats"][workspace_id] = {
                    "format": "pkl",
                    "size_mb": round(size, 2),
                    "modified": mtime.isoformat(),
                    "num_factors": num_factors,
                    "num_rows": num_rows
                }
                
                print(f"  📊 {workspace_id[:8]}... : PKL ({num_factors} factors, {num_rows:,} rows)")
            except Exception as e:
                self.analysis_results["file_formats"][workspace_id] = {
                    "format": "pkl",
                    "error": str(e)
                }
                print(f"  ❌ {workspace_id[:8]}... : PKL (Error reading: {e})")
        else:
            print(f"  ⚠️  {workspace_id[:8]}... : No combined_factors file found")
    
    def analyze_ic_values(self):
        """Analyze IC values from mlruns"""
        print("\n" + "=" * 80)
        print("📈 ANALYZING IC VALUES")
        print("=" * 80)
        
        ic_values = []
        
        # Find all IC metric files
        for mlrun_dir in self.workspace_path.glob("*/mlruns/*/*/metrics/IC"):
            try:
                with open(mlrun_dir, 'r') as f:
                    line = f.readline().strip()
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            ic_value = float(parts[1])
                            ic_values.append({
                                "workspace": mlrun_dir.parts[-6],
                                "value": ic_value,
                                "timestamp": int(parts[0]) if parts[0].isdigit() else None
                            })
            except Exception as e:
                print(f"  ⚠️  Error reading IC from {mlrun_dir}: {e}")
        
        self.analysis_results["ic_values"] = ic_values
        
        if ic_values:
            unique_values = set(ic["value"] for ic in ic_values)
            print(f"\n  📊 Found {len(ic_values)} IC values")
            print(f"  📊 Unique IC values: {len(unique_values)}")
            
            if len(unique_values) == 1:
                print(f"  ❌ ALL IC VALUES ARE IDENTICAL: {list(unique_values)[0]}")
                self.analysis_results["issues_found"].append({
                    "type": "IDENTICAL_IC_VALUES",
                    "severity": "CRITICAL",
                    "description": f"All {len(ic_values)} IC values are identical: {list(unique_values)[0]}",
                    "impact": "Custom factors are not being used in model training"
                })
            else:
                print(f"  ✅ IC values vary: min={min(unique_values)}, max={max(unique_values)}")
        
        return ic_values
    
    def analyze_configs(self):
        """Analyze configuration files"""
        print("\n" + "=" * 80)
        print("⚙️  ANALYZING CONFIGURATION FILES")
        print("=" * 80)
        
        config_files = [
            "conf_baseline.yaml",
            "conf_combined_factors.yaml", 
            "conf_combined_factors_sota_model.yaml"
        ]
        
        for config_name in config_files:
            config_file = self.config_path / config_name
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                handler_config = config.get("task", {}).get("dataset", {}).get("kwargs", {}).get("handler", {})
                handler_class = handler_config.get("class", "Unknown")
                
                # Check for data_loader
                has_data_loader = "data_loader" in handler_config.get("kwargs", {})
                
                # Check for StaticDataLoader
                static_loader_config = None
                if has_data_loader:
                    data_loader = handler_config["kwargs"]["data_loader"]
                    if isinstance(data_loader, dict):
                        dataloaders = data_loader.get("kwargs", {}).get("dataloader_l", [])
                        for loader in dataloaders:
                            if "StaticDataLoader" in loader.get("class", ""):
                                static_loader_config = loader.get("kwargs", {}).get("config", "")
                
                self.analysis_results["config_analysis"][config_name] = {
                    "handler_class": handler_class,
                    "has_data_loader": has_data_loader,
                    "static_loader_config": static_loader_config,
                    "expected_format": "pkl" if ".pkl" in str(static_loader_config) else "parquet" if ".parquet" in str(static_loader_config) else "unknown"
                }
                
                print(f"\n  📄 {config_name}:")
                print(f"     Handler: {handler_class}")
                print(f"     Has data_loader: {has_data_loader}")
                if static_loader_config:
                    print(f"     Static loader expects: {static_loader_config}")
                
                # Check for issues
                if handler_class == "Alpha158" and not has_data_loader:
                    self.analysis_results["issues_found"].append({
                        "type": "CONFIG_ISSUE",
                        "severity": "HIGH",
                        "file": config_name,
                        "description": "Alpha158 handler without data_loader - will only use 158 predefined features",
                        "impact": "Custom factors will be ignored"
                    })
    
    def check_code_files(self):
        """Check factor_runner.py and model_runner.py"""
        print("\n" + "=" * 80)
        print("🔧 CHECKING CODE FILES")
        print("=" * 80)
        
        code_files = {
            "factor_runner.py": "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/developer/factor_runner.py",
            "model_runner.py": "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/developer/model_runner.py"
        }
        
        for name, path in code_files.items():
            if os.path.exists(path):
                with open(path, 'r') as f:
                    content = f.read()
                
                has_to_pickle = "to_pickle" in content
                has_to_parquet = "to_parquet" in content
                
                print(f"\n  📝 {name}:")
                print(f"     Uses to_pickle(): {has_to_pickle}")
                print(f"     Uses to_parquet(): {has_to_parquet}")
                
                if has_to_parquet and not has_to_pickle:
                    self.analysis_results["issues_found"].append({
                        "type": "CODE_ISSUE",
                        "severity": "HIGH",
                        "file": name,
                        "description": f"{name} still uses to_parquet() instead of to_pickle()",
                        "impact": "Generated files incompatible with config expectations"
                    })
    
    def generate_recommendations(self):
        """Generate recommendations based on analysis"""
        print("\n" + "=" * 80)
        print("💡 RECOMMENDATIONS")
        print("=" * 80)
        
        # Check for format mismatch
        has_parquet = any(f.get("format") == "parquet" for f in self.analysis_results["file_formats"].values())
        has_pkl = any(f.get("format") == "pkl" for f in self.analysis_results["file_formats"].values())
        
        if has_parquet and not has_pkl:
            self.analysis_results["recommendations"].append({
                "priority": "HIGH",
                "action": "Convert all .parquet files to .pkl format",
                "reason": "Qlib 0.9.6 StaticDataLoader doesn't support .parquet format"
            })
            
            self.analysis_results["recommendations"].append({
                "priority": "HIGH", 
                "action": "Fix model_runner.py to use to_pickle() instead of to_parquet()",
                "reason": "model_runner.py is still generating .parquet files"
            })
        
        # Check for Alpha158 without data_loader
        alpha158_issues = [i for i in self.analysis_results["issues_found"] if "Alpha158" in i.get("description", "")]
        if alpha158_issues:
            self.analysis_results["recommendations"].append({
                "priority": "CRITICAL",
                "action": "Add DataHandlerLP with NestedDataLoader to combine Alpha158 and custom factors",
                "reason": "Alpha158 alone only uses 158 predefined features"
            })
        
        # Check for identical IC values
        ic_issues = [i for i in self.analysis_results["issues_found"] if i.get("type") == "IDENTICAL_IC_VALUES"]
        if ic_issues:
            self.analysis_results["recommendations"].append({
                "priority": "CRITICAL",
                "action": "Verify custom factors are being loaded and used in model training",
                "reason": "Identical IC values indicate custom factors are not being used"
            })
        
        for i, rec in enumerate(self.analysis_results["recommendations"], 1):
            print(f"\n  {i}. [{rec['priority']}] {rec['action']}")
            print(f"     Reason: {rec['reason']}")
    
    def save_report(self):
        """Save analysis report"""
        report_path = self.base_path / "claude_tools/factor_loading_analysis.json"
        with open(report_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        print(f"\n📊 Full report saved to: {report_path}")
        return report_path
    
    def run_full_analysis(self):
        """Run complete analysis"""
        print("\n" + "=" * 80)
        print("🔍 RD-AGENT CUSTOM FACTOR LOADING ANALYSIS")
        print("=" * 80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all analyses
        self.analyze_workspaces()
        self.analyze_ic_values()
        self.analyze_configs()
        self.check_code_files()
        self.generate_recommendations()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 80)
        print(f"  Workspaces analyzed: {self.analysis_results['workspaces_analyzed']}")
        print(f"  Issues found: {len(self.analysis_results['issues_found'])}")
        print(f"  Recommendations: {len(self.analysis_results['recommendations'])}")
        
        if self.analysis_results["issues_found"]:
            print("\n  🚨 CRITICAL ISSUES:")
            for issue in self.analysis_results["issues_found"]:
                if issue["severity"] == "CRITICAL":
                    print(f"     - {issue['description']}")
        
        # Save report
        report_path = self.save_report()
        
        return self.analysis_results

if __name__ == "__main__":
    analyzer = FactorLoadingAnalyzer()
    results = analyzer.run_full_analysis()
    
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)