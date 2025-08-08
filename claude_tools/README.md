# Claude Tools for RD-Agent

This directory contains essential tools for RD-Agent ETF factor mining project.

## Core Tools

### 1. analyze_factor_loading.py
**Purpose**: Comprehensive analysis of custom factor loading issues
**Usage**: 
```bash
python claude_tools/core_tools/analyze_factor_loading.py
```
**Output**: JSON report with IC values, file formats, and configuration analysis

### 2. test_parquet_vs_pkl.py
**Purpose**: Test compatibility between .parquet and .pkl formats with Qlib
**Usage**:
```bash
python claude_tools/core_tools/test_parquet_vs_pkl.py
```
**Output**: Compatibility test results and conversion script generation

### 3. convert_parquet_to_pkl.py
**Purpose**: Convert all .parquet files to .pkl format for Qlib compatibility
**Usage**:
```bash
python claude_tools/core_tools/convert_parquet_to_pkl.py
```
**Output**: Converts workspace files from .parquet to .pkl

### 4. verify_fix_complete.py
**Purpose**: Verify all fixes have been applied correctly
**Usage**:
```bash
python claude_tools/core_tools/verify_fix_complete.py
```
**Output**: Verification summary of code fixes, config files, and workspace files

## Archived Tools
The `archived/` directory contains scripts created during debugging and testing. These are kept for reference but are not essential for normal operation.

## Important Notes
- All tools assume RD-Agent is installed in the conda environment `rdagent`
- Data paths are configured for macOS environment
- Tools are designed for RD-Agent v0.7.0 with Qlib 0.9.6