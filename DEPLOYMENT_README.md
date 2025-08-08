# RD-Agent ETF 因子挖掘系统 - 部署包说明

## 📦 部署包内容

本部署包包含了完整的RD-Agent ETF因子挖掘系统部署所需的所有文档和工具。

### 核心文件清单

| 文件/目录 | 说明 | 用途 |
|-----------|------|------|
| **DEPLOYMENT_GUIDE_CN.md** | 📚 详细部署指南 | 完整的部署教程，从零开始到系统运行 |
| **quick_start.sh** | 🚀 快速启动脚本 | 一键完成所有安装配置 |
| **scripts/** | 🛠️ 工具脚本目录 | 包含所有自动化工具 |
| ├── setup_environment.sh | 环境设置脚本 | 自动配置运行环境 |
| ├── prepare_data.py | 数据准备工具 | CSV转换为Qlib格式 |
| └── config_manager.py | 配置管理器 | 交互式生成配置文件 |

## 🎯 快速开始（5分钟）

### 方式1：一键安装（推荐）

```bash
# 给脚本执行权限
chmod +x quick_start.sh

# 运行快速开始脚本
./quick_start.sh
```

脚本会自动完成：
- ✅ 环境检查
- ✅ 项目克隆
- ✅ Python环境创建
- ✅ 依赖安装
- ✅ 系统补丁
- ✅ 配置生成
- ✅ 数据准备

### 方式2：手动安装

如果自动脚本出现问题，请参考 `DEPLOYMENT_GUIDE_CN.md` 进行手动安装。

## 📋 使用流程

### 1. 环境准备
```bash
# 检查环境
bash scripts/setup_environment.sh

# 输出会显示缺少的组件
```

### 2. 数据准备
```bash
# 准备您的ETF数据（CSV格式）
# 格式要求：datetime, instrument, open, high, low, close, volume

# 转换数据
python scripts/prepare_data.py \
    --input your_etf_data.csv \
    --output ./data
```

### 3. 配置系统
```bash
# 交互式配置
python scripts/config_manager.py

# 或直接编辑.env文件
vim .env
```

### 4. 验证安装
```bash
# 健康检查
rdagent health_check

# 详细诊断
python scripts/diagnostic_tool.py
```

### 5. 运行系统
```bash
# 运行1轮因子挖掘测试
rdagent fin_factor --loop_n 1 --step_n 1

# 查看Web界面
rdagent ui --port 19899
```

## 🔧 工具脚本说明

### setup_environment.sh
**功能**：自动配置运行环境
```bash
bash scripts/setup_environment.sh
```
- 检测操作系统（macOS/Linux/Windows）
- 安装系统依赖
- 应用兼容性补丁
- 创建目录结构

### prepare_data.py
**功能**：ETF数据格式转换
```bash
python scripts/prepare_data.py --help
```
支持功能：
- CSV → Qlib binary (.bin)
- CSV → HDF5 (.h5)
- 批量处理多个文件
- 数据验证和清洗
- 生成数据报告

### config_manager.py
**功能**：配置文件管理
```bash
# 交互式配置
python scripts/config_manager.py

# 导出配置
python scripts/config_manager.py --export config.json

# 导入配置
python scripts/config_manager.py --import config.json
```

## 📊 数据格式要求

### 输入CSV格式
```csv
datetime,instrument,open,high,low,close,volume
2025-01-01,510300.SH,4.123,4.156,4.098,4.145,1234567
2025-01-02,510300.SH,4.145,4.178,4.120,4.165,1345678
```

### 支持的额外指标
如果您的CSV包含额外指标（如momentum_20d, rsi_14等），脚本会自动识别并转换。

## ❓ 常见问题

### Q1: macOS上timeout命令不存在
**解决**：
```bash
brew install coreutils
```
或运行 `setup_environment.sh` 自动修复

### Q2: IC值全部相同（0.007418）
**原因**：文件格式问题（.parquet vs .pkl）
**解决**：参考部署指南第13章

### Q3: 内存不足
**解决**：减少并行线程数
```bash
# 编辑.env
MAX_WORKERS=2
```

### Q4: API调用失败
**检查**：
1. API密钥是否正确
2. 网络是否可访问OpenAI
3. API额度是否充足

## 📁 建议的项目结构

```
RD-Agent/
├── data/                      # 数据目录
│   ├── qlib_etf_data_final/  # Qlib格式数据
│   └── qlib_etf_data_h5/     # HDF5格式数据
├── scripts/                   # 工具脚本
├── logs/                      # 运行日志
├── .env                       # 配置文件
├── DEPLOYMENT_GUIDE_CN.md    # 部署指南
└── quick_start.sh             # 快速开始脚本
```

## 🚀 优化建议

### 1. 使用Docker（最简单）
```bash
docker build -t rdagent-etf .
docker run -it rdagent-etf
```

### 2. 创建Starter仓库
建议创建一个包含以下内容的GitHub仓库：
- 预配置文件
- 示例数据
- 自动化脚本
- 视频教程

### 3. 性能优化
- 使用SSD存储数据
- 增加内存到16GB+
- 使用GPU加速（如果有）

## 📞 获取帮助

1. **查看详细文档**：`DEPLOYMENT_GUIDE_CN.md`
2. **运行诊断工具**：`python scripts/diagnostic_tool.py`
3. **查看日志**：`tail -f log/latest/run.log`
4. **GitHub Issues**：https://github.com/microsoft/RD-Agent/issues

## 🎯 下一步计划

- [ ] 添加更多ETF数据源
- [ ] 集成自定义指标（momentum_20d等）
- [ ] 优化因子生成算法
- [ ] 提升IC值到0.05+

## 📝 版本信息

- **部署包版本**：1.0.0
- **RD-Agent版本**：0.7.0
- **Qlib版本**：0.9.6
- **更新日期**：2025-08-08

---

**作者**：RD-Agent ETF Team  
**许可**：MIT License