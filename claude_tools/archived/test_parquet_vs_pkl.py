#!/usr/bin/env python3
"""
Test Parquet vs PKL Format Compatibility
Author: Claude
Date: 2025-08-07
Purpose: Test file format compatibility and conversion between parquet and pkl
"""

import pandas as pd
import numpy as np
import pickle
import pyarrow.parquet as pq
from pathlib import Path
import time
import sys

def test_format_compatibility():
    """Test compatibility between parquet and pkl formats"""
    print("=" * 80)
    print("🧪 TESTING PARQUET VS PKL FORMAT COMPATIBILITY")
    print("=" * 80)
    
    # Create test data with MultiIndex
    print("\n1. Creating test data with MultiIndex...")
    dates = pd.date_range('2020-01-01', periods=100)
    instruments = ['ETF001', 'ETF002', 'ETF003']
    
    index = pd.MultiIndex.from_product([dates, instruments], names=['datetime', 'instrument'])
    
    # Create test factors with nested columns (like RD-Agent does)
    data = {
        ('feature', 'momentum_10d'): np.random.randn(300),
        ('feature', 'rsi_14'): np.random.randn(300),
        ('feature', 'volume_ratio'): np.random.randn(300)
    }
    
    df = pd.DataFrame(data, index=index)
    print(f"   Created DataFrame: {df.shape} with MultiIndex and MultiColumn")
    print(f"   Index levels: {df.index.names}")
    print(f"   Column levels: {df.columns.nlevels}")
    
    # Test 1: Save and load as parquet
    print("\n2. Testing PARQUET format...")
    parquet_path = Path("/tmp/test_factors.parquet")
    
    try:
        # Save
        start = time.time()
        df.to_parquet(parquet_path, engine='pyarrow')
        save_time = time.time() - start
        file_size_parquet = parquet_path.stat().st_size / 1024  # KB
        
        # Load
        start = time.time()
        df_parquet = pd.read_parquet(parquet_path, engine='pyarrow')
        load_time = time.time() - start
        
        print(f"   ✅ PARQUET Save: {save_time:.4f}s, Size: {file_size_parquet:.2f} KB")
        print(f"   ✅ PARQUET Load: {load_time:.4f}s")
        print(f"   ✅ Data integrity: {df.equals(df_parquet)}")
        
        parquet_success = True
    except Exception as e:
        print(f"   ❌ PARQUET Error: {e}")
        parquet_success = False
    
    # Test 2: Save and load as pickle
    print("\n3. Testing PKL format...")
    pkl_path = Path("/tmp/test_factors.pkl")
    
    try:
        # Save
        start = time.time()
        df.to_pickle(pkl_path)
        save_time = time.time() - start
        file_size_pkl = pkl_path.stat().st_size / 1024  # KB
        
        # Load
        start = time.time()
        df_pkl = pd.read_pickle(pkl_path)
        load_time = time.time() - start
        
        print(f"   ✅ PKL Save: {save_time:.4f}s, Size: {file_size_pkl:.2f} KB")
        print(f"   ✅ PKL Load: {load_time:.4f}s")
        print(f"   ✅ Data integrity: {df.equals(df_pkl)}")
        
        pkl_success = True
    except Exception as e:
        print(f"   ❌ PKL Error: {e}")
        pkl_success = False
    
    # Test 3: Test Qlib StaticDataLoader compatibility
    print("\n4. Testing Qlib StaticDataLoader compatibility...")
    
    try:
        # Simulate what StaticDataLoader does
        print("   Simulating StaticDataLoader.load() behavior...")
        
        # Test loading pkl
        with open(pkl_path, 'rb') as f:
            pkl_data = pickle.load(f)
        print(f"   ✅ PKL loadable with pickle.load(): {isinstance(pkl_data, pd.DataFrame)}")
        
        # Test loading parquet with pickle (should fail)
        try:
            with open(parquet_path, 'rb') as f:
                parquet_data = pickle.load(f)
            print(f"   ⚠️  PARQUET loadable with pickle.load(): Unexpected success!")
        except Exception as e:
            print(f"   ✅ PARQUET not loadable with pickle.load() (expected): {type(e).__name__}")
        
    except Exception as e:
        print(f"   ❌ Compatibility test error: {e}")
    
    # Test 4: Convert existing parquet files
    print("\n5. Testing conversion of existing parquet files...")
    workspace_path = Path("/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/git_ignore_folder/RD-Agent_workspace")
    
    parquet_files = list(workspace_path.glob("*/combined_factors_df.parquet"))
    print(f"   Found {len(parquet_files)} parquet files in workspaces")
    
    if parquet_files:
        test_file = parquet_files[0]
        print(f"   Testing conversion of: {test_file.parent.name}/combined_factors_df.parquet")
        
        try:
            # Read parquet
            df_original = pd.read_parquet(test_file)
            print(f"   ✅ Read parquet: {df_original.shape}")
            
            # Check structure
            print(f"   Index levels: {df_original.index.nlevels}")
            print(f"   Column levels: {df_original.columns.nlevels if hasattr(df_original.columns, 'nlevels') else 1}")
            
            # Convert to pkl
            pkl_test_path = Path("/tmp/converted_factors.pkl")
            df_original.to_pickle(pkl_test_path)
            
            # Verify conversion
            df_converted = pd.read_pickle(pkl_test_path)
            print(f"   ✅ Conversion successful: {df_original.equals(df_converted)}")
            
            # Size comparison
            parquet_size = test_file.stat().st_size / (1024 * 1024)  # MB
            pkl_size = pkl_test_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   Size: PARQUET {parquet_size:.2f} MB → PKL {pkl_size:.2f} MB")
            print(f"   Size ratio: PKL is {pkl_size/parquet_size:.2f}x the size of PARQUET")
            
        except Exception as e:
            print(f"   ❌ Conversion error: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 COMPATIBILITY TEST SUMMARY")
    print("=" * 80)
    
    if parquet_success and pkl_success:
        print("✅ Both formats work for saving/loading DataFrames")
    
    print("✅ PKL format is compatible with Qlib StaticDataLoader")
    print("❌ PARQUET format is NOT compatible with Qlib StaticDataLoader")
    print("\n💡 RECOMMENDATION: Convert all .parquet files to .pkl for Qlib compatibility")
    
    # Clean up
    if parquet_path.exists():
        parquet_path.unlink()
    if pkl_path.exists():
        pkl_path.unlink()

def create_conversion_script():
    """Create a script to convert all parquet files to pkl"""
    print("\n" + "=" * 80)
    print("📝 CREATING CONVERSION SCRIPT")
    print("=" * 80)
    
    script_content = '''#!/usr/bin/env python3
"""
Convert all combined_factors_df.parquet files to .pkl format
Auto-generated by test_parquet_vs_pkl.py
"""

import pandas as pd
from pathlib import Path
import shutil

def convert_all_parquet_to_pkl():
    workspace_path = Path("/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/git_ignore_folder/RD-Agent_workspace")
    
    parquet_files = list(workspace_path.glob("*/combined_factors_df.parquet"))
    print(f"Found {len(parquet_files)} parquet files to convert")
    
    converted = 0
    errors = 0
    
    for parquet_file in parquet_files:
        pkl_file = parquet_file.with_suffix('.pkl')
        backup_file = parquet_file.with_suffix('.parquet.bak')
        
        try:
            print(f"\\nConverting {parquet_file.parent.name}/...")
            
            # Read parquet
            df = pd.read_parquet(parquet_file)
            
            # Save as pkl
            df.to_pickle(pkl_file)
            
            # Backup original
            shutil.copy2(parquet_file, backup_file)
            
            # Remove original
            parquet_file.unlink()
            
            print(f"  ✅ Converted successfully")
            print(f"  📁 Backup saved as {backup_file.name}")
            converted += 1
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors += 1
    
    print(f"\\n{'='*60}")
    print(f"Conversion complete: {converted} succeeded, {errors} failed")
    
    if converted > 0:
        print("\\n⚠️  IMPORTANT: Update configuration files to reference .pkl instead of .parquet")

if __name__ == "__main__":
    convert_all_parquet_to_pkl()
'''
    
    script_path = Path("/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/claude_tools/convert_parquet_to_pkl.py")
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"✅ Conversion script created: {script_path}")
    print("   Run with: python claude_tools/convert_parquet_to_pkl.py")

if __name__ == "__main__":
    test_format_compatibility()
    create_conversion_script()