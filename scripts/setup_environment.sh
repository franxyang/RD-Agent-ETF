#!/bin/bash

# RD-Agent ETF 环境设置脚本
# 用途：自动配置运行环境，处理操作系统差异

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_info "检测到 macOS 系统"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        log_info "检测到 Linux 系统"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
        log_info "检测到 Windows 系统"
    else
        log_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
}

# 检查Python版本
check_python() {
    log_info "检查Python版本..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        log_info "Python版本: $PYTHON_VERSION"
        
        if [[ "$PYTHON_VERSION" == "3.10" ]] || [[ "$PYTHON_VERSION" == "3.11" ]]; then
            log_success "Python版本符合要求"
        else
            log_warning "推荐使用Python 3.10或3.11，当前版本: $PYTHON_VERSION"
        fi
    else
        log_error "未找到Python3，请先安装Python"
        exit 1
    fi
}

# 检查Conda
check_conda() {
    log_info "检查Conda..."
    
    if command -v conda &> /dev/null; then
        CONDA_VERSION=$(conda --version)
        log_success "Conda已安装: $CONDA_VERSION"
        return 0
    else
        log_warning "Conda未安装，将使用venv"
        return 1
    fi
}

# 创建虚拟环境
create_virtual_env() {
    log_info "创建虚拟环境..."
    
    if check_conda; then
        # 使用Conda
        if conda env list | grep -q "rdagent"; then
            log_warning "rdagent环境已存在，跳过创建"
        else
            log_info "创建conda环境..."
            conda create -n rdagent python=3.10.18 -y
            log_success "Conda环境创建成功"
        fi
        
        # 激活环境
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate rdagent
    else
        # 使用venv
        if [ -d "venv" ]; then
            log_warning "venv已存在，跳过创建"
        else
            log_info "创建venv环境..."
            python3 -m venv venv
            log_success "venv环境创建成功"
        fi
        
        # 激活环境
        if [[ "$OS" == "windows" ]]; then
            source venv/Scripts/activate
        else
            source venv/bin/activate
        fi
    fi
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."
    
    case $OS in
        macos)
            # 检查Homebrew
            if ! command -v brew &> /dev/null; then
                log_warning "Homebrew未安装，某些功能可能受限"
                log_info "建议安装: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            else
                # 安装必要工具
                log_info "安装macOS依赖..."
                
                # 安装coreutils（包含timeout）
                if ! command -v gtimeout &> /dev/null; then
                    brew install coreutils
                    log_success "coreutils安装成功"
                fi
                
                # 检查Xcode命令行工具
                if ! xcode-select -p &> /dev/null; then
                    log_warning "需要安装Xcode命令行工具"
                    log_info "请运行: xcode-select --install"
                fi
            fi
            ;;
            
        linux)
            # 检查包管理器
            if command -v apt-get &> /dev/null; then
                log_info "更新apt包列表..."
                sudo apt-get update
                
                log_info "安装Linux依赖..."
                sudo apt-get install -y build-essential python3-dev
                log_success "Linux依赖安装成功"
                
            elif command -v yum &> /dev/null; then
                log_info "安装Linux依赖..."
                sudo yum install -y gcc gcc-c++ python3-devel
                log_success "Linux依赖安装成功"
            fi
            ;;
            
        windows)
            log_warning "Windows系统建议使用WSL2或Docker Desktop"
            log_info "请参考文档安装WSL2: https://docs.microsoft.com/windows/wsl/install"
            ;;
    esac
}

# 检查Docker
check_docker() {
    log_info "检查Docker..."
    
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        log_info "Docker已安装: $DOCKER_VERSION"
        
        # 测试Docker权限
        if docker run --rm hello-world &> /dev/null; then
            log_success "Docker运行正常"
        else
            log_warning "Docker需要sudo权限或未正确配置"
            
            if [[ "$OS" == "linux" ]]; then
                log_info "尝试将用户添加到docker组..."
                sudo usermod -aG docker $USER
                log_warning "请注销并重新登录以使更改生效"
            fi
        fi
    else
        log_warning "Docker未安装，某些功能可能受限"
        log_info "建议安装Docker: https://docs.docker.com/get-docker/"
    fi
}

# 应用macOS补丁
apply_macos_patches() {
    if [[ "$OS" != "macos" ]]; then
        return
    fi
    
    log_info "应用macOS兼容性补丁..."
    
    # 修复timeout命令问题
    if [ -f "rdagent/utils/env.py" ]; then
        python3 << 'EOF'
import fileinput
import sys
import os

file_path = "rdagent/utils/env.py"
if os.path.exists(file_path):
    content = open(file_path, 'r').read()
    if 'timeout --kill-after' in content and 'command -v timeout' not in content:
        # 需要修复
        for line in fileinput.input(file_path, inplace=True):
            if 'timeout --kill-after=10' in line and 'entry_add_timeout' in line:
                print('        entry_add_timeout = f"/bin/sh -c \'if command -v timeout >/dev/null 2>&1; then timeout --kill-after=10 {self.conf.running_timeout_period} {entry}; else {entry}; fi; entry_exit_code=$?; exit $entry_exit_code\'"')
            else:
                print(line, end='')
        print("  ✅ timeout命令补丁已应用")
    else:
        print("  ⚠️ 文件已包含补丁，跳过")
else:
    print("  ⚠️ 文件不存在，跳过补丁")
EOF
    fi
    
    # 修复文件链接问题
    if [ -f "rdagent/core/experiment.py" ]; then
        python3 << 'EOF'
import os
import platform

file_path = "rdagent/core/experiment.py"
if os.path.exists(file_path):
    content = open(file_path, 'r').read()
    if 'platform.system() == "Darwin"' not in content:
        print("  ⚠️ 需要手动修复文件链接问题")
        print("  请参考部署文档的macOS兼容性章节")
    else:
        print("  ✅ 文件链接补丁已存在")
EOF
    fi
    
    log_success "macOS补丁检查完成"
}

# 创建目录结构
create_directories() {
    log_info "创建必要的目录结构..."
    
    directories=(
        "data"
        "data/qlib_etf_data_final"
        "data/qlib_etf_data_final/calendars"
        "data/qlib_etf_data_final/features"
        "data/qlib_etf_data_final/instruments"
        "data/qlib_etf_data_h5"
        "logs"
        "config"
        "scripts"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_info "创建目录: $dir"
        fi
    done
    
    log_success "目录结构创建完成"
}

# 生成配置模板
generate_config_template() {
    log_info "生成配置模板..."
    
    # 生成.env模板
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# RD-Agent 配置文件
# 请填写您的实际配置

# API配置
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
CHAT_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small

# 数据路径配置
QLIB_DATA_PATH=./data/qlib_etf_data_final
HDF5_DATA_PATH=./data/qlib_etf_data_h5

# 市场配置
MARKET=all
BENCHMARK=000852.csi
START_DATE=2023-01-01
END_DATE=2025-07-10

# 性能配置
MAX_WORKERS=4
CACHE_ENABLED=true
EOF
        log_success ".env模板已生成"
        log_warning "请编辑.env文件，填入您的API密钥"
    else
        log_info ".env文件已存在，跳过生成"
    fi
}

# 主函数
main() {
    echo "========================================="
    echo "   RD-Agent ETF 环境设置工具"
    echo "========================================="
    echo ""
    
    # 1. 检测操作系统
    detect_os
    
    # 2. 检查Python
    check_python
    
    # 3. 安装系统依赖
    install_system_deps
    
    # 4. 创建虚拟环境
    create_virtual_env
    
    # 5. 检查Docker
    check_docker
    
    # 6. 应用系统补丁
    apply_macos_patches
    
    # 7. 创建目录结构
    create_directories
    
    # 8. 生成配置模板
    generate_config_template
    
    echo ""
    echo "========================================="
    log_success "环境设置完成！"
    echo ""
    echo "下一步操作："
    echo "1. 编辑 .env 文件，配置API密钥"
    echo "2. 安装Python依赖: pip install -e ."
    echo "3. 准备数据: python scripts/prepare_data.py"
    echo "4. 运行健康检查: rdagent health_check"
    echo "========================================="
}

# 运行主函数
main