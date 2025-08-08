# RD-Agent ETF Factor Mining Project Documentation

## 项目概述
**目标**: 通过RD-Agent在本地实现ETF市场的因子挖掘  
**环境**: macOS 15.5 (Apple M1 Max), Python 3.10.18  
**版本**: RD-Agent 0.7.0, Qlib 0.9.6  

## 环境搭建

### 1. 基础环境配置
```bash
# 创建conda环境
conda create -n rdagent python=3.10.18
conda activate rdagent

# 安装RD-Agent
pip install rdagent==0.7.0

# 克隆项目
git clone https://github.com/microsoft/RD-Agent.git
cd RD-Agent
```

### 2. 数据路径配置
```bash
# 设置环境变量
export QLIB_DATA=/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_final
export H5_DATA=/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_h5
```

## 阶段一：官方数据测试 ✅

### 1.1 macOS兼容性修复

#### 问题1: 文件链接不支持macOS
**文件**: `rdagent/core/experiment.py`  
**行号**: 192  
**修复**:
```python
# 在link_all_files_in_folder_to_workspace函数中添加
if platform.system() == "Darwin":  # macOS
    os.symlink(data_file_path, workspace_data_file_path)
```

#### 问题2: timeout命令不存在
**文件**: `rdagent/utils/env.py`  
**行号**: 301-319  
**修复**:
```python
# 替换原有的entry_add_timeout定义
entry_add_timeout = (
    f"/bin/sh -c 'if command -v timeout >/dev/null 2>&1; then "
    + f"timeout --kill-after=10 {self.conf.running_timeout_period} {entry}; "
    + "else {entry}; fi; "
    + "entry_exit_code=$?; exit $entry_exit_code'"
)
```

### 1.2 运行验证
```bash
# 健康检查
rdagent health_check

# 运行因子挖掘
rdagent fin_factor --loop_n 1 --step_n 1
```

**成果**: 成功生成momentum_5d因子（7,545,108行数据）

## 阶段二：ETF数据接入 ✅

### 2.1 数据准备

#### 转换CSV到Qlib格式
```bash
# 假设原始CSV文件在./etf_csv目录
python scripts/dump_bin.py dump_all \
    --csv_path ./etf_csv \
    --qlib_dir /Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_final
```

#### 创建HDF5格式（用于因子生成）
```bash
# 运行转换脚本
python claude_tools/archived/data_conversion/simple_convert_to_h5.py
```

**数据信息**:
- 247个ETF/指数
- 时间范围: 2015-01-05至2025-07-15
- 基准: 000852.csi (中证1000)

### 2.2 配置文件修改

#### 修改1: 因子生成配置
**文件**: `rdagent/components/coder/factor_coder/config.py`  
**行号**: 11, 15
```python
# 原配置（注释掉）
# data_folder: str = "git_ignore_folder/factor_implementation_source_data"
# 新配置
data_folder: str = "/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_h5"
data_folder_debug: str = "/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_h5"
```

#### 修改2: Qlib回测配置
**文件**: `rdagent/scenarios/qlib/experiment/factor_template/conf_baseline.yaml`  
```yaml
qlib_init:
    provider_uri: "/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_final"
    region: cn

market: &market all  # 改为所有ETF
benchmark: &benchmark 000852.csi  # 中证1000

data_handler_config:
    start_time: 2015-01-01
    end_time: 2025-07-10  # 避免越界
    fit_start_time: 2015-01-01
    fit_end_time: 2020-12-31
```

#### 修改3: 处理器配置
```yaml
# 使用Alpha158替代Alpha360（conf_baseline.yaml）
handler:
    class: Alpha158
    module_path: qlib.contrib.data.handler
```

**注意**: 同样修改`conf_combined_factors.yaml`和`conf_combined_factors_sota_model.yaml`

### 2.3 系统兼容性修复

**文件**: `rdagent/scenarios/qlib/experiment/utils.py`  
**行号**: 143-174  
**修复**: 添加对qlib标准目录结构的支持
```python
elif p.name in ["calendars", "instruments", "features"]:
    # 处理qlib数据目录结构
    return f"This directory contains {p.name} data for qlib"
```

## 关键问题修复：自定义因子加载

### 问题描述
- **现象**: 所有实验IC值相同（0.007418）
- **原因**: Qlib 0.9.6不支持.parquet格式，自定义因子未被加载

### 解决方案

#### 步骤1: 修改factor_runner.py
**文件**: `rdagent/scenarios/qlib/developer/factor_runner.py`  
**行号**: 121  
```python
# 原代码
# combined_factors.to_parquet(target_path, engine="pyarrow")
# 修改为
target_path = exp.experiment_workspace.workspace_path / "combined_factors_df.pkl"
combined_factors.to_pickle(target_path)
```

#### 步骤2: 修改model_runner.py
**文件**: `rdagent/scenarios/qlib/developer/model_runner.py`  
**行号**: 54  
```python
# 同样的修改：to_parquet改为to_pickle
combined_factors.to_pickle(target_path)
```

#### 步骤3: 转换现有文件
```bash
python claude_tools/core_tools/convert_parquet_to_pkl.py
```

#### 步骤4: 更新模板配置
**文件**: `rdagent/scenarios/qlib/experiment/model_template/conf_sota_factors_model.yaml`  
```yaml
- class: qlib.data.dataset.loader.StaticDataLoader
  kwargs:
    config: "combined_factors_df.pkl"  # 原为.parquet
```

### 验证修复
```bash
# 清理工作空间
rm -rf git_ignore_folder/RD-Agent_workspace/*

# 运行测试
rdagent fin_factor --loop_n 1 --step_n 1

# 验证IC值不再相同
python claude_tools/core_tools/verify_fix_complete.py
```

## 工具脚本说明

### 核心工具（claude_tools/core_tools/）
1. **analyze_factor_loading.py**: 分析因子加载问题
2. **test_parquet_vs_pkl.py**: 测试文件格式兼容性
3. **convert_parquet_to_pkl.py**: 批量转换文件格式
4. **verify_fix_complete.py**: 验证所有修复是否生效

### 使用示例
```bash
# 分析当前系统状态
python claude_tools/core_tools/analyze_factor_loading.py

# 转换文件格式
python claude_tools/core_tools/convert_parquet_to_pkl.py

# 验证修复
python claude_tools/core_tools/verify_fix_complete.py
```

## 当前状态总结

### ✅ 已完成
1. macOS兼容性问题修复
2. ETF数据成功接入（247个ETF）
3. 自定义因子加载问题解决
4. IC值不再相同，系统能正常进化

### 📊 性能指标
- 数据规模: 247个ETF，588,108条记录
- 处理速度: 30秒/Loop
- IC值范围: -0.000800 到 0.006214（持续优化中）

### 🎯 下一步计划（阶段三）
1. 添加momentum20d测试因子
2. 接入公司完整数据库
3. 目标IC值 > 0.05

## Momentum20d因子集成方案（待实施）

### 方案A：作为Qlib特征添加（推荐）
```bash
# 1. 为每个ETF生成momentum20d.day.bin
for etf in /qlib_etf_data_final/features/*; do
    # 计算20日动量
    momentum20d = (close[t] - close[t-20]) / close[t-20]
    # 保存为.bin文件
done

# 2. 扩展Alpha158配置
# 创建自定义Alpha158Extended类包含momentum20d

# 3. 更新配置文件使用Alpha158Extended
```

### 方案B：使用StaticDataLoader
```yaml
# 在配置文件中使用NestedDataLoader
handler:
  class: DataHandlerLP
  kwargs:
    data_loader:
      class: NestedDataLoader
      kwargs:
        dataloader_l:
          - class: Alpha158DL
          - class: StaticDataLoader
            kwargs:
              config: "momentum20d_features.pkl"
```

### 方案C：修改HDF5数据源
```python
# 添加momentum20d到daily_pv.h5
# 最简单但只影响因子生成，不影响回测
```

**推荐**: 方案A，因为能同时用于因子生成和回测

## 注意事项

1. **路径问题**: 所有路径都是绝对路径，需根据实际环境调整
2. **缓存清理**: 配置修改后必须清理工作空间缓存
3. **版本兼容**: 确保RD-Agent 0.7.0 + Qlib 0.9.6
4. **数据格式**: Qlib使用.bin格式，因子生成使用HDF5格式

---
*最后更新: 2025-08-07*