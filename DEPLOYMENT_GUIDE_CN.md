# RD-Agent ETF因子挖掘系统 - 本地部署完全指南

> 📖 版本：1.0.0 | 更新日期：2025-08-08  
> 💡 本指南针对RD-Agent 0.7.0版本，提供从零开始的完整部署教程

## 🎯 第一部分：系统概述

### 什么是RD-Agent？

RD-Agent是微软开源的**自动化量化研究系统**，通过AI驱动的方式自动进行因子挖掘和模型优化。本项目将其应用于**ETF市场**，实现自动化的Alpha因子发现。

### 核心价值
- 🤖 **自动化因子生成**：AI自动设计和实现新的量化因子
- 📊 **智能回测评估**：自动进行历史回测并计算IC值
- 🔄 **进化优化**：基于反馈持续改进因子质量
- 💰 **成本效益**：不到10美元即可获得2倍于基准的收益率

### 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    用户输入命令                        │
└────────────────┬───────────────────────────────────┘
                 ▼
┌─────────────────────────────────────────────────────┐
│              RD-Agent 核心引擎                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Research │→ │ Develop  │→ │ Evaluate │          │
│  │  Agent   │  │  Agent   │  │  Agent   │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└────────────────┬───────────────────────────────────┘
                 ▼
┌─────────────────────────────────────────────────────┐
│                  数据层                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ ETF数据  │  │ 因子库   │  │ 回测结果 │          │
│  │ (.bin)   │  │ (.pkl)   │  │ (.csv)   │          │
│  └──────────┘  └──────────┘  └──────────┘          │
└─────────────────────────────────────────────────────┘
```

### 工作流程

1. **因子假设生成** → LLM生成因子设计思路
2. **代码实现** → 自动编写factor.py实现代码  
3. **数据处理** → 读取ETF数据计算因子值
4. **回测评估** → Qlib执行回测计算IC值
5. **进化迭代** → 基于结果优化因子

---

## 📋 第二部分：环境准备

### 系统要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| 操作系统 | macOS 12+ / Windows 10+ / Ubuntu 20.04+ | macOS 14+ / Windows 11 |
| CPU | 4核 | 8核+ |
| 内存 | 8GB | 16GB+ |
| 硬盘空间 | 20GB | 50GB+ |
| Python | 3.10.x | 3.10.18 |
| Docker | 20.10+ | 最新版 |

### 前置软件检查

创建检查脚本 `check_environment.sh`：

```bash
#!/bin/bash

echo "========================================="
echo "   RD-Agent 环境检查工具 v1.0"
echo "========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $2 已安装: $(command -v $1)"
        if [ ! -z "$3" ]; then
            version=$($3)
            echo "  版本: $version"
        fi
        return 0
    else
        echo -e "${RED}✗${NC} $2 未安装"
        return 1
    fi
}

echo ""
echo "1. 检查基础环境..."
echo "-----------------"

# Python检查
check_command python3 "Python 3" "python3 --version"
if [ $? -eq 0 ]; then
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ "$python_version" == "3.10" ]] || [[ "$python_version" == "3.11" ]]; then
        echo -e "  ${GREEN}Python版本符合要求${NC}"
    else
        echo -e "  ${YELLOW}警告: 推荐使用Python 3.10或3.11${NC}"
    fi
fi

# Conda检查
check_command conda "Conda" "conda --version"

# Git检查
check_command git "Git" "git --version"

# Docker检查
check_command docker "Docker" "docker --version"
if [ $? -eq 0 ]; then
    if docker run --rm hello-world &> /dev/null; then
        echo -e "  ${GREEN}Docker运行正常${NC}"
    else
        echo -e "  ${YELLOW}警告: Docker需要sudo权限或未正确配置${NC}"
    fi
fi

echo ""
echo "2. 检查磁盘空间..."
echo "-----------------"

# macOS和Linux通用磁盘检查
available_space=$(df -h . | awk 'NR==2 {print $4}')
echo "当前目录可用空间: $available_space"

# 提取数字部分进行比较
space_num=$(echo $available_space | sed 's/[^0-9.]//g')
space_unit=$(echo $available_space | sed 's/[0-9.]//g')

if [[ "$space_unit" == "G" || "$space_unit" == "Gi" ]]; then
    if (( $(echo "$space_num > 20" | bc -l) )); then
        echo -e "${GREEN}磁盘空间充足${NC}"
    else
        echo -e "${YELLOW}警告: 建议至少保留20GB可用空间${NC}"
    fi
elif [[ "$space_unit" == "T" || "$space_unit" == "Ti" ]]; then
    echo -e "${GREEN}磁盘空间充足${NC}"
else
    echo -e "${RED}磁盘空间可能不足${NC}"
fi

echo ""
echo "3. 操作系统特定检查..."
echo "---------------------"

# 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "检测到 macOS 系统"
    
    # 检查Homebrew
    check_command brew "Homebrew" "brew --version"
    
    # 检查Xcode命令行工具
    if xcode-select -p &> /dev/null; then
        echo -e "${GREEN}✓${NC} Xcode命令行工具已安装"
    else
        echo -e "${YELLOW}⚠${NC} 需要安装Xcode命令行工具: xcode-select --install"
    fi
    
    # 检查coreutils（包含gtimeout）
    if command -v gtimeout &> /dev/null; then
        echo -e "${GREEN}✓${NC} GNU coreutils已安装（包含timeout命令）"
    else
        echo -e "${YELLOW}⚠${NC} 建议安装coreutils: brew install coreutils"
    fi
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "检测到 Linux 系统"
    check_command timeout "timeout命令" "timeout --version | head -n1"
    
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "检测到 Windows 系统"
    echo -e "${YELLOW}提示: 建议使用WSL2或Docker Desktop${NC}"
fi

echo ""
echo "========================================="
echo "检查完成！"
echo ""
echo "下一步操作："
echo "1. 修复所有标记为 ✗ 的项目"
echo "2. 考虑安装标记为 ⚠ 的推荐项"
echo "3. 运行 'bash quick_install.sh' 开始安装"
echo "========================================="
```

---

## 🚀 第三部分：快速安装

### 选项1：一键安装脚本（推荐）

创建 `quick_install.sh`：

```bash
#!/bin/bash

set -e  # 遇到错误立即退出

echo "========================================="
echo "   RD-Agent ETF 一键安装脚本"
echo "========================================="

# 1. 克隆项目
echo "📦 步骤1: 克隆RD-Agent项目..."
if [ ! -d "RD-Agent" ]; then
    git clone https://github.com/microsoft/RD-Agent.git
fi
cd RD-Agent

# 2. 创建Python环境
echo "🐍 步骤2: 创建Python环境..."
conda create -n rdagent python=3.10.18 -y
source $(conda info --base)/etc/profile.d/conda.sh
conda activate rdagent

# 3. 安装依赖
echo "📚 步骤3: 安装Python依赖..."
pip install -e .
pip install qlib

# 4. 下载示例数据
echo "📊 步骤4: 准备ETF示例数据..."
mkdir -p data
cd data

# 下载预处理的ETF示例数据（这里需要您提供数据URL）
# wget https://your-data-url/etf_sample_data.tar.gz
# tar -xzf etf_sample_data.tar.gz

echo "示例数据准备完成"
cd ..

# 5. 应用必要的补丁
echo "🔧 步骤5: 应用系统兼容性补丁..."

# macOS兼容性修复
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "检测到macOS，应用兼容性补丁..."
    
    # 修复timeout命令问题
    python << 'EOF'
import fileinput
import sys

file_path = "rdagent/utils/env.py"
for line in fileinput.input(file_path, inplace=True):
    if "timeout --kill-after" in line and "entry_add_timeout" in line:
        print('        entry_add_timeout = f"/bin/sh -c \'if command -v timeout >/dev/null 2>&1; then timeout --kill-after=10 {self.conf.running_timeout_period} {entry}; else {entry}; fi; entry_exit_code=$?; exit $entry_exit_code\'"')
    else:
        print(line, end='')
EOF
    echo "macOS补丁应用完成"
fi

# 6. 配置文件生成
echo "⚙️ 步骤6: 生成配置文件..."
python << 'EOF'
import os
import yaml

# 创建.env文件
env_content = """
# LLM配置
CHAT_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# 数据路径配置
QLIB_DATA_PATH={}/data/qlib_etf_data_final
HDF5_DATA_PATH={}/data/qlib_etf_data_h5
""".format(os.getcwd(), os.getcwd())

with open('.env', 'w') as f:
    f.write(env_content)

print("配置文件已生成")
print("⚠️ 请编辑 .env 文件，填入您的OpenAI API密钥")
EOF

# 7. 验证安装
echo "✅ 步骤7: 验证安装..."
python -c "import rdagent; print('RD-Agent版本:', rdagent.__version__)"
python -c "import qlib; print('Qlib导入成功')"

echo ""
echo "========================================="
echo "🎉 安装完成！"
echo ""
echo "下一步操作："
echo "1. 编辑 .env 文件，配置API密钥"
echo "2. 准备ETF数据（参见数据准备章节）"
echo "3. 运行测试: rdagent health_check"
echo "========================================="
```

### 选项2：Docker安装（最简单）

创建 `Dockerfile`：

```dockerfile
FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 克隆RD-Agent
RUN git clone https://github.com/microsoft/RD-Agent.git .

# 安装Python依赖
RUN pip install --no-cache-dir -e .
RUN pip install --no-cache-dir qlib

# 复制配置文件
COPY config/ ./config/
COPY data/ ./data/

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露端口（用于Web UI）
EXPOSE 19899

# 启动命令
CMD ["bash"]
```

使用Docker：
```bash
# 构建镜像
docker build -t rdagent-etf:latest .

# 运行容器
docker run -it \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/config:/app/config \
    -p 19899:19899 \
    rdagent-etf:latest
```

---

## 📊 第四部分：数据准备

### ETF数据格式要求

您的CSV数据需要包含以下字段：

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| datetime | str | 日期 | 2025-01-01 |
| instrument | str | ETF代码 | 510300.SH |
| open | float | 开盘价 | 4.123 |
| high | float | 最高价 | 4.156 |
| low | float | 最低价 | 4.098 |
| close | float | 收盘价 | 4.145 |
| volume | float | 成交量 | 1234567 |

### 数据转换脚本

创建 `prepare_etf_data.py`：

```python
#!/usr/bin/env python
"""
ETF数据准备工具
将CSV格式的ETF数据转换为RD-Agent所需的格式
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
import subprocess
from tqdm import tqdm

class ETFDataPreparer:
    def __init__(self, input_path, output_dir):
        self.input_path = Path(input_path)
        self.output_dir = Path(output_dir)
        self.qlib_dir = self.output_dir / "qlib_etf_data_final"
        self.h5_dir = self.output_dir / "qlib_etf_data_h5"
        
    def prepare(self):
        """完整的数据准备流程"""
        print("📊 ETF数据准备开始...")
        
        # 1. 读取原始数据
        print("1️⃣ 读取CSV数据...")
        df = self.read_csv_data()
        
        # 2. 数据验证
        print("2️⃣ 验证数据格式...")
        self.validate_data(df)
        
        # 3. 转换为Qlib格式
        print("3️⃣ 转换为Qlib格式...")
        self.convert_to_qlib(df)
        
        # 4. 生成HDF5格式
        print("4️⃣ 生成HDF5格式...")
        self.create_hdf5(df)
        
        # 5. 验证结果
        print("5️⃣ 验证转换结果...")
        self.verify_conversion()
        
        print("✅ 数据准备完成！")
        
    def read_csv_data(self):
        """读取CSV数据"""
        if self.input_path.is_file():
            df = pd.read_csv(self.input_path)
        else:
            # 读取目录下所有CSV文件
            all_dfs = []
            for csv_file in self.input_path.glob("*.csv"):
                df = pd.read_csv(csv_file)
                all_dfs.append(df)
            df = pd.concat(all_dfs, ignore_index=True)
        
        print(f"  读取 {len(df)} 条记录")
        print(f"  时间范围: {df['datetime'].min()} 至 {df['datetime'].max()}")
        print(f"  ETF数量: {df['instrument'].nunique()}")
        
        return df
    
    def validate_data(self, df):
        """验证数据格式"""
        required_columns = ['datetime', 'instrument', 'open', 'high', 'low', 'close', 'volume']
        
        # 检查必需列
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"缺少必需列: {missing_cols}")
        
        # 检查数据类型
        df['datetime'] = pd.to_datetime(df['datetime'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 检查缺失值
        null_counts = df[required_columns].isnull().sum()
        if null_counts.any():
            print(f"  ⚠️ 警告: 发现缺失值")
            print(null_counts[null_counts > 0])
        
        return True
    
    def convert_to_qlib(self, df):
        """转换为Qlib bin格式"""
        # 创建目录结构
        self.qlib_dir.mkdir(parents=True, exist_ok=True)
        calendars_dir = self.qlib_dir / "calendars"
        features_dir = self.qlib_dir / "features"
        instruments_dir = self.qlib_dir / "instruments"
        
        calendars_dir.mkdir(exist_ok=True)
        features_dir.mkdir(exist_ok=True)
        instruments_dir.mkdir(exist_ok=True)
        
        # 1. 生成日历文件
        calendars = sorted(df['datetime'].unique())
        calendars_file = calendars_dir / "day.txt"
        pd.DataFrame(calendars).to_csv(calendars_file, index=False, header=False)
        print(f"  生成日历文件: {len(calendars)} 个交易日")
        
        # 2. 生成股票列表文件
        instruments = []
        for instrument in df['instrument'].unique():
            inst_df = df[df['instrument'] == instrument]
            start_date = inst_df['datetime'].min()
            end_date = inst_df['datetime'].max()
            instruments.append(f"{instrument}\t{start_date}\t{end_date}")
        
        instruments_file = instruments_dir / "all.txt"
        with open(instruments_file, 'w') as f:
            f.write('\n'.join(instruments))
        print(f"  生成股票列表: {len(instruments)} 个ETF")
        
        # 3. 为每个股票生成特征文件
        for instrument in tqdm(df['instrument'].unique(), desc="  转换股票数据"):
            inst_df = df[df['instrument'] == instrument].sort_values('datetime')
            inst_dir = features_dir / instrument.lower()
            inst_dir.mkdir(exist_ok=True)
            
            # 为每个特征生成bin文件
            for feature in ['open', 'high', 'low', 'close', 'volume']:
                self._save_bin_file(
                    inst_df['datetime'].values,
                    inst_df[feature].values,
                    inst_dir / f"{feature}.day.bin",
                    calendars
                )
    
    def _save_bin_file(self, dates, values, output_path, all_calendars):
        """保存为Qlib bin格式"""
        # 创建完整的日期序列
        df = pd.DataFrame({'date': dates, 'value': values})
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        
        # 重索引到完整日历
        full_dates = pd.to_datetime(all_calendars)
        df = df.reindex(full_dates)
        
        # 前向填充缺失值
        df = df.fillna(method='ffill')
        
        # 获取起始索引
        start_index = 0
        
        # 保存为二进制格式
        data = np.hstack([start_index, df['value'].values]).astype('<f')
        data.tofile(str(output_path))
    
    def create_hdf5(self, df):
        """创建HDF5格式文件"""
        self.h5_dir.mkdir(parents=True, exist_ok=True)
        
        # 转换为MultiIndex格式
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.set_index(['datetime', 'instrument'])
        df = df.sort_index()
        
        # 选择需要的列
        df = df[['open', 'high', 'low', 'close', 'volume']]
        
        # 保存为HDF5
        h5_file = self.h5_dir / "daily_pv.h5"
        df.to_hdf(h5_file, key='data', mode='w')
        print(f"  生成HDF5文件: {h5_file}")
        print(f"  数据形状: {df.shape}")
    
    def verify_conversion(self):
        """验证转换结果"""
        # 检查文件是否存在
        checks = {
            "日历文件": self.qlib_dir / "calendars/day.txt",
            "股票列表": self.qlib_dir / "instruments/all.txt",
            "HDF5数据": self.h5_dir / "daily_pv.h5"
        }
        
        all_good = True
        for name, path in checks.items():
            if path.exists():
                print(f"  ✅ {name}: {path}")
            else:
                print(f"  ❌ {name}: 未找到")
                all_good = False
        
        # 检查特征文件数量
        features_dir = self.qlib_dir / "features"
        etf_count = len(list(features_dir.iterdir()))
        print(f"  📁 特征目录: {etf_count} 个ETF")
        
        return all_good

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ETF数据准备工具')
    parser.add_argument('--input', required=True, help='输入CSV文件或目录')
    parser.add_argument('--output', required=True, help='输出目录')
    
    args = parser.parse_args()
    
    preparer = ETFDataPreparer(args.input, args.output)
    preparer.prepare()

if __name__ == "__main__":
    main()
```

使用示例：
```bash
# 单个CSV文件
python prepare_etf_data.py --input etf_data.csv --output ./data

# 多个CSV文件目录
python prepare_etf_data.py --input ./csv_files --output ./data
```

---

## ⚙️ 第五部分：配置修改

### 核心配置文件清单

| 配置文件 | 作用 | 必改项 |
|---------|------|--------|
| `.env` | API密钥和环境变量 | OPENAI_API_KEY |
| `rdagent/components/coder/factor_coder/config.py` | 数据路径配置 | 第11, 15行 |
| `rdagent/scenarios/qlib/experiment/factor_template/*.yaml` | 回测参数 | 第4, 9, 10行 |

### 配置生成器

创建 `config_generator.py`：

```python
#!/usr/bin/env python
"""
RD-Agent配置生成器
交互式生成所有必需的配置文件
"""

import os
import yaml
import json
from pathlib import Path

class ConfigGenerator:
    def __init__(self):
        self.config = {}
        self.project_root = Path.cwd()
        
    def run(self):
        """运行交互式配置生成"""
        print("========================================")
        print("   RD-Agent 配置生成器")
        print("========================================")
        print()
        
        # 1. API配置
        self.configure_api()
        
        # 2. 数据路径配置
        self.configure_data_paths()
        
        # 3. 市场配置
        self.configure_market()
        
        # 4. 生成配置文件
        self.generate_configs()
        
        print("\n✅ 配置生成完成！")
        
    def configure_api(self):
        """配置API密钥"""
        print("1. API配置")
        print("-" * 40)
        
        api_key = input("请输入OpenAI API密钥: ").strip()
        api_base = input("API基础URL [默认: https://api.openai.com/v1]: ").strip()
        
        if not api_base:
            api_base = "https://api.openai.com/v1"
        
        self.config['api'] = {
            'OPENAI_API_KEY': api_key,
            'OPENAI_API_BASE': api_base,
            'CHAT_MODEL': 'gpt-4o',
            'EMBEDDING_MODEL': 'text-embedding-3-small'
        }
        
    def configure_data_paths(self):
        """配置数据路径"""
        print("\n2. 数据路径配置")
        print("-" * 40)
        
        default_qlib = str(self.project_root / "data/qlib_etf_data_final")
        default_h5 = str(self.project_root / "data/qlib_etf_data_h5")
        
        qlib_path = input(f"Qlib数据路径 [{default_qlib}]: ").strip()
        h5_path = input(f"HDF5数据路径 [{default_h5}]: ").strip()
        
        if not qlib_path:
            qlib_path = default_qlib
        if not h5_path:
            h5_path = default_h5
            
        self.config['data'] = {
            'qlib_path': qlib_path,
            'h5_path': h5_path
        }
        
    def configure_market(self):
        """配置市场参数"""
        print("\n3. 市场配置")
        print("-" * 40)
        
        market = input("市场范围 [all]: ").strip() or "all"
        benchmark = input("基准指数 [000852.csi]: ").strip() or "000852.csi"
        
        start_date = input("回测开始日期 [2023-01-01]: ").strip() or "2023-01-01"
        end_date = input("回测结束日期 [2025-07-10]: ").strip() or "2025-07-10"
        
        self.config['market'] = {
            'market': market,
            'benchmark': benchmark,
            'start_date': start_date,
            'end_date': end_date
        }
        
    def generate_configs(self):
        """生成配置文件"""
        print("\n生成配置文件...")
        
        # 1. 生成.env文件
        self._generate_env_file()
        
        # 2. 更新Python配置
        self._update_python_config()
        
        # 3. 更新YAML配置
        self._update_yaml_configs()
        
    def _generate_env_file(self):
        """生成.env文件"""
        env_content = f"""# RD-Agent配置文件
# 自动生成，请勿手动修改

# API配置
OPENAI_API_KEY={self.config['api']['OPENAI_API_KEY']}
OPENAI_API_BASE={self.config['api']['OPENAI_API_BASE']}
CHAT_MODEL={self.config['api']['CHAT_MODEL']}
EMBEDDING_MODEL={self.config['api']['EMBEDDING_MODEL']}

# 数据路径
QLIB_DATA_PATH={self.config['data']['qlib_path']}
HDF5_DATA_PATH={self.config['data']['h5_path']}

# 市场配置
MARKET={self.config['market']['market']}
BENCHMARK={self.config['market']['benchmark']}
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        print("  ✅ 生成 .env")
        
    def _update_python_config(self):
        """更新Python配置文件"""
        config_file = Path("rdagent/components/coder/factor_coder/config.py")
        
        if config_file.exists():
            # 读取文件
            with open(config_file, 'r') as f:
                lines = f.readlines()
            
            # 更新数据路径
            for i, line in enumerate(lines):
                if 'data_folder:' in line and 'git_ignore_folder' in line:
                    lines[i] = f'    data_folder: str = "{self.config["data"]["h5_path"]}"\n'
                elif 'data_folder_debug:' in line and 'git_ignore_folder' in line:
                    lines[i] = f'    data_folder_debug: str = "{self.config["data"]["h5_path"]}"\n'
            
            # 写回文件
            with open(config_file, 'w') as f:
                f.writelines(lines)
            print("  ✅ 更新 config.py")
        
    def _update_yaml_configs(self):
        """更新YAML配置文件"""
        yaml_dir = Path("rdagent/scenarios/qlib/experiment/factor_template")
        
        if yaml_dir.exists():
            for yaml_file in yaml_dir.glob("*.yaml"):
                self._update_single_yaml(yaml_file)
        
    def _update_single_yaml(self, yaml_file):
        """更新单个YAML文件"""
        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # 更新配置
        if 'qlib_init' in config:
            config['qlib_init']['provider_uri'] = self.config['data']['qlib_path']
        
        if 'market' in self.config['market']:
            # 使用YAML锚点引用
            for key in config:
                if isinstance(config[key], str) and 'market' in config[key]:
                    config[key] = self.config['market']['market']
        
        # 写回文件
        with open(yaml_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"  ✅ 更新 {yaml_file.name}")

def main():
    generator = ConfigGenerator()
    generator.run()

if __name__ == "__main__":
    main()
```

---

## 🏃 第六部分：运行验证

### 健康检查

```bash
# 基础健康检查
rdagent health_check

# 详细诊断
python diagnostic_tool.py
```

创建 `diagnostic_tool.py`：

```python
#!/usr/bin/env python
"""
RD-Agent诊断工具
检查系统配置和数据完整性
"""

import os
import sys
from pathlib import Path
import pandas as pd
import yaml

class DiagnosticTool:
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        
    def run(self):
        """运行所有诊断检查"""
        print("========================================")
        print("   RD-Agent 系统诊断")
        print("========================================\n")
        
        # 1. 检查Python环境
        self.check_python_env()
        
        # 2. 检查配置文件
        self.check_configs()
        
        # 3. 检查数据文件
        self.check_data_files()
        
        # 4. 检查依赖包
        self.check_dependencies()
        
        # 5. 运行测试因子
        self.test_factor_generation()
        
        # 总结
        self.print_summary()
        
    def check_python_env(self):
        """检查Python环境"""
        print("1. Python环境检查")
        print("-" * 40)
        
        # Python版本
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self._check("Python版本", python_version, 
                   sys.version_info.major == 3 and sys.version_info.minor == 10)
        
        # 虚拟环境
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        self._check("虚拟环境", "已激活" if in_venv else "未激活", in_venv)
        
        print()
        
    def check_configs(self):
        """检查配置文件"""
        print("2. 配置文件检查")
        print("-" * 40)
        
        # .env文件
        env_exists = Path('.env').exists()
        self._check(".env文件", "存在" if env_exists else "不存在", env_exists)
        
        if env_exists:
            with open('.env', 'r') as f:
                env_content = f.read()
                has_api_key = 'OPENAI_API_KEY=' in env_content and \
                             'your_api_key_here' not in env_content
                self._check("API密钥配置", "已设置" if has_api_key else "未设置", has_api_key)
        
        # 检查关键配置文件
        config_files = [
            "rdagent/components/coder/factor_coder/config.py",
            "rdagent/scenarios/qlib/experiment/factor_template/conf_baseline.yaml"
        ]
        
        for config_file in config_files:
            exists = Path(config_file).exists()
            self._check(f"{Path(config_file).name}", "存在" if exists else "不存在", exists)
        
        print()
        
    def check_data_files(self):
        """检查数据文件"""
        print("3. 数据文件检查")
        print("-" * 40)
        
        # 从.env读取路径
        data_paths = self._get_data_paths()
        
        # 检查Qlib数据
        if data_paths['qlib_path']:
            qlib_path = Path(data_paths['qlib_path'])
            if qlib_path.exists():
                calendars = qlib_path / "calendars/day.txt"
                instruments = qlib_path / "instruments/all.txt"
                features = qlib_path / "features"
                
                self._check("Qlib日历文件", "存在" if calendars.exists() else "不存在", calendars.exists())
                self._check("Qlib股票列表", "存在" if instruments.exists() else "不存在", instruments.exists())
                
                if features.exists():
                    etf_count = len(list(features.iterdir()))
                    self._check("ETF数据", f"{etf_count}个", etf_count > 0)
        
        # 检查HDF5数据
        if data_paths['h5_path']:
            h5_path = Path(data_paths['h5_path'])
            if h5_path.exists():
                h5_file = h5_path / "daily_pv.h5"
                self._check("HDF5数据文件", "存在" if h5_file.exists() else "不存在", h5_file.exists())
                
                if h5_file.exists():
                    try:
                        df = pd.read_hdf(h5_file, key='data')
                        self._check("HDF5数据读取", f"成功 ({df.shape[0]}条记录)", True)
                    except Exception as e:
                        self._check("HDF5数据读取", f"失败: {str(e)}", False)
        
        print()
        
    def check_dependencies(self):
        """检查依赖包"""
        print("4. 依赖包检查")
        print("-" * 40)
        
        packages = ['rdagent', 'qlib', 'pandas', 'numpy', 'pyyaml']
        
        for package in packages:
            try:
                __import__(package)
                self._check(f"{package}", "已安装", True)
            except ImportError:
                self._check(f"{package}", "未安装", False)
        
        print()
        
    def test_factor_generation(self):
        """测试因子生成"""
        print("5. 因子生成测试")
        print("-" * 40)
        
        # 创建测试因子代码
        test_factor = """
import pandas as pd
import numpy as np

# 测试能否读取数据
try:
    data = pd.read_hdf('daily_pv.h5', key='data')
    print(f"数据读取成功: {data.shape}")
    
    # 计算简单因子
    factor = data['close'].pct_change()
    print(f"因子计算成功: {factor.shape}")
    
    success = True
except Exception as e:
    print(f"测试失败: {e}")
    success = False
"""
        
        # 这里只是模拟，实际运行需要在正确的环境中
        self._check("因子生成测试", "跳过（需手动测试）", None)
        
        print()
        
    def _check(self, name, status, passed):
        """执行单个检查"""
        if passed is None:
            symbol = "⚠️"
            color = "\033[93m"  # 黄色
        elif passed:
            symbol = "✅"
            color = "\033[92m"  # 绿色
            self.checks_passed += 1
        else:
            symbol = "❌"
            color = "\033[91m"  # 红色
            self.checks_failed += 1
        
        reset = "\033[0m"
        print(f"  {symbol} {name}: {color}{status}{reset}")
        
    def _get_data_paths(self):
        """从配置获取数据路径"""
        paths = {'qlib_path': None, 'h5_path': None}
        
        if Path('.env').exists():
            with open('.env', 'r') as f:
                for line in f:
                    if 'QLIB_DATA_PATH=' in line:
                        paths['qlib_path'] = line.split('=')[1].strip()
                    elif 'HDF5_DATA_PATH=' in line:
                        paths['h5_path'] = line.split('=')[1].strip()
        
        return paths
        
    def print_summary(self):
        """打印诊断总结"""
        print("========================================")
        print("诊断总结")
        print("========================================")
        
        total = self.checks_passed + self.checks_failed
        if total > 0:
            success_rate = (self.checks_passed / total) * 100
            print(f"✅ 通过: {self.checks_passed}")
            print(f"❌ 失败: {self.checks_failed}")
            print(f"📊 成功率: {success_rate:.1f}%")
            
            if success_rate == 100:
                print("\n🎉 系统状态良好，可以开始使用！")
            elif success_rate >= 80:
                print("\n⚠️ 系统基本就绪，但建议修复失败项")
            else:
                print("\n❌ 系统存在问题，请先修复失败项")
        
        print("\n下一步：")
        if self.checks_failed > 0:
            print("1. 修复所有标记为 ❌ 的项目")
            print("2. 重新运行诊断工具")
        else:
            print("1. 运行: rdagent fin_factor --loop_n 1")
            print("2. 查看结果: rdagent ui --port 19899")

def main():
    tool = DiagnosticTool()
    tool.run()

if __name__ == "__main__":
    main()
```

### 首次测试运行

```bash
# 1. 简单测试（1个因子，1轮迭代）
rdagent fin_factor --loop_n 1 --step_n 1

# 2. 查看运行日志
tail -f log/latest/run.log

# 3. 检查结果
python check_results.py
```

---

## 🔧 第七部分：问题排查

### 常见问题速查表

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| timeout: command not found | macOS缺少GNU工具 | `brew install coreutils` |
| IC值全部相同(0.007418) | 文件格式不兼容 | 将.parquet改为.pkl |
| KeyError: 'label' | 配置文件错误 | 检查YAML配置中的label字段 |
| No module named 'qlib' | Qlib未安装 | `pip install qlib` |
| Docker permission denied | Docker权限问题 | 将用户加入docker组 |
| 内存溢出 | 数据量过大 | 减少batch_size或使用分批处理 |

### 详细解决方案

#### 问题1：macOS timeout命令

```python
# 自动修复脚本 fix_macos_timeout.py
import fileinput
import sys

file_path = "rdagent/utils/env.py"
for line in fileinput.input(file_path, inplace=True):
    if "timeout --kill-after" in line:
        # 替换为兼容版本
        new_line = line.replace(
            "timeout --kill-after=10",
            "if command -v timeout >/dev/null 2>&1; then timeout --kill-after=10"
        )
        print(new_line, end='')
    else:
        print(line, end='')

print("✅ macOS timeout问题已修复")
```

#### 问题2：IC值相同问题

```python
# 修复文件格式 fix_file_format.py
import pandas as pd
from pathlib import Path

def convert_parquet_to_pkl():
    """将所有.parquet文件转换为.pkl"""
    workspace_dir = Path("git_ignore_folder/RD-Agent_workspace")
    
    for parquet_file in workspace_dir.rglob("*.parquet"):
        try:
            # 读取parquet
            df = pd.read_parquet(parquet_file)
            
            # 保存为pkl
            pkl_file = parquet_file.with_suffix('.pkl')
            df.to_pickle(pkl_file)
            
            # 删除原文件
            parquet_file.unlink()
            
            print(f"✅ 转换: {parquet_file.name} → {pkl_file.name}")
        except Exception as e:
            print(f"❌ 失败: {parquet_file.name}: {e}")

if __name__ == "__main__":
    convert_parquet_to_pkl()
```

---

## 📚 附录A：命令速查表

```bash
# 环境管理
conda create -n rdagent python=3.10.18    # 创建环境
conda activate rdagent                    # 激活环境
conda deactivate                          # 退出环境

# 安装相关
pip install -e .                          # 开发模式安装
pip install qlib                          # 安装Qlib

# RD-Agent命令
rdagent health_check                      # 健康检查
rdagent fin_factor --loop_n 5             # 运行5轮因子挖掘
rdagent ui --port 19899                   # 启动Web界面

# 数据准备
python prepare_etf_data.py --input data.csv --output ./data
python scripts/dump_bin.py dump_all --csv_path ./csv --qlib_dir ./qlib_data

# 诊断工具
python check_environment.sh               # 环境检查
python diagnostic_tool.py                 # 系统诊断
python config_generator.py                # 配置生成

# Docker相关
docker build -t rdagent-etf .            # 构建镜像
docker run -it rdagent-etf               # 运行容器
docker ps                                 # 查看运行容器
docker logs <container_id>               # 查看日志
```

---

## 📚 附录B：项目结构说明

```
RD-Agent/
├── rdagent/                    # 核心代码
│   ├── components/             # 组件模块
│   │   └── coder/             
│   │       └── factor_coder/   # 因子生成器
│   │           └── config.py   # ⚙️ 需要修改：数据路径
│   ├── scenarios/              # 场景实现
│   │   └── qlib/              
│   │       ├── experiment/     # 实验配置
│   │       │   └── factor_template/  # ⚙️ 需要修改：YAML配置
│   │       └── developer/      # 开发者工具
│   └── utils/                  
│       └── env.py              # ⚙️ macOS需要修改：timeout命令
├── data/                       # 数据目录（需创建）
│   ├── qlib_etf_data_final/   # Qlib格式数据
│   │   ├── calendars/          # 交易日历
│   │   ├── features/           # 特征数据(.bin文件)
│   │   └── instruments/        # 股票列表
│   └── qlib_etf_data_h5/      # HDF5格式数据
│       └── daily_pv.h5         # 价量数据
├── git_ignore_folder/          # 工作目录（自动生成）
│   └── RD-Agent_workspace/     # 实验工作空间
├── log/                        # 日志目录（自动生成）
├── .env                        # ⚙️ 需要创建：环境变量
└── scripts/                    # 工具脚本
    ├── quick_install.sh        # 一键安装
    ├── prepare_etf_data.py     # 数据准备
    └── diagnostic_tool.py      # 诊断工具
```

---

## 🎓 学习资源

- [RD-Agent官方仓库](https://github.com/microsoft/RD-Agent)
- [Qlib官方文档](https://qlib.readthedocs.io/)
- [论文：R&D-Agent-Quant](https://arxiv.org/abs/2505.15155)
- [视频教程](待创建)

---

## 📞 获取帮助

遇到问题时的解决步骤：

1. 查看本文档的问题排查章节
2. 运行诊断工具：`python diagnostic_tool.py`
3. 查看日志文件：`log/latest/run.log`
4. 搜索GitHub Issues
5. 提交新Issue（包含诊断结果）

---

*文档版本：1.0.0 | 最后更新：2025-08-08*