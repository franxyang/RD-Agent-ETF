#!/bin/bash

# ==========================================
# RD-Agent GitHub上传准备脚本
# 版本: 1.0.0 | 更新日期: 2025-08-08
# ==========================================
# 
# 功能:
# 1. 检查并移除敏感信息
# 2. 创建必要的文档
# 3. 准备标准的GitHub项目结构
# 4. 生成上传指南
#
# ==========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 打印分隔线
print_separator() {
    echo "=========================================="
}

# 检查当前目录
check_directory() {
    print_info "检查当前目录..."
    
    if [ ! -f "pyproject.toml" ] || [ ! -d "rdagent" ]; then
        print_error "请在RD-Agent项目根目录运行此脚本"
        exit 1
    fi
    
    print_success "当前目录确认为RD-Agent项目根目录"
}

# 备份.env文件
backup_env_files() {
    print_info "备份环境配置文件..."
    
    if [ -f ".env" ]; then
        cp .env .env.backup
        print_success "已备份 .env 到 .env.backup"
    fi
    
    # 创建示例.env文件（不包含敏感信息）
    if [ -f ".env.template" ]; then
        print_info "创建示例环境配置文件..."
        cat > .env.example << 'EOF'
# ==========================================
# RD-Agent 环境配置示例
# 请复制此文件为 .env 并填入实际值
# ==========================================

# LLM配置
CHAT_MODEL="o3-mini"
EMBEDDING_MODEL="text-embedding-3-small"
OPENAI_API_BASE="https://api.openai.com/v1"
OPENAI_API_KEY="sk-your-api-key-here"  # 替换为实际API密钥

# 数据配置
FACTOR_CoSTEER_data_folder=/path/to/your/h5/data
FACTOR_CoSTEER_data_folder_debug=/path/to/your/h5/data

# 其他配置请参考.env.template
EOF
        print_success "已创建 .env.example"
    fi
}

# 检查敏感信息
check_sensitive_info() {
    print_info "扫描敏感信息..."
    
    # 定义敏感信息模式
    local sensitive_patterns=(
        "sk-[a-zA-Z0-9]{32,}"  # OpenAI API keys
        "sk-proj-[a-zA-Z0-9]{32,}"  # OpenAI project keys
        "Bearer [a-zA-Z0-9]{32,}"  # Bearer tokens
        "password\s*=\s*['\"][^'\"]{8,}"  # Passwords
        "secret\s*=\s*['\"][^'\"]{8,}"  # Secrets
    )
    
    local found_sensitive=false
    
    # 排除的文件和目录
    local exclude_patterns="-not -path '*/\.*' -not -path '*/git_ignore_folder/*' -not -path '*/pickle_cache/*' -not -path '*/__pycache__/*' -not -name '*.pyc' -not -name '*.db' -not -name '*.pkl' -not -name '*.h5'"
    
    for pattern in "${sensitive_patterns[@]}"; do
        print_info "检查模式: $pattern"
        
        # 使用grep搜索敏感信息（排除二进制文件和指定目录）
        if find . -type f $exclude_patterns -exec grep -l -E "$pattern" {} \; 2>/dev/null | head -n 5; then
            found_sensitive=true
            print_warning "发现可能的敏感信息匹配模式: $pattern"
        fi
    done
    
    if [ "$found_sensitive" = true ]; then
        print_warning "发现潜在敏感信息，请手动检查以上文件"
        echo ""
        read -p "是否继续？(y/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "已取消操作"
            exit 1
        fi
    else
        print_success "未发现明显的敏感信息"
    fi
}

# 确保敏感文件不会被上传
ensure_gitignore() {
    print_info "确保.gitignore配置正确..."
    
    # 确保.gitignore包含必要的排除项
    local gitignore_entries=(
        ".env"
        ".env.*"
        "!.env.example"
        "!.env.template"
        "*.key"
        "*.pem"
        "*.crt"
        "*credentials*"
        "*secret*"
        "api_keys.txt"
        "config.local.json"
    )
    
    for entry in "${gitignore_entries[@]}"; do
        if ! grep -q "^${entry}$" .gitignore 2>/dev/null; then
            echo "$entry" >> .gitignore
        fi
    done
    
    print_success ".gitignore已更新，敏感文件将被排除"
    
    # 提醒用户
    if [ -f ".env" ]; then
        print_warning ".env文件存在但不会被上传（已在.gitignore中）"
    fi
}

# 创建README
create_readme() {
    print_info "更新README文件..."
    
    if [ ! -f "README.md" ]; then
        cat > README.md << 'EOF'
# RD-Agent ETF因子挖掘系统

基于Microsoft RD-Agent的ETF市场因子挖掘实现。

## 快速开始

请参考 [部署指南](DEPLOYMENT_GUIDE_CN.md) 进行本地部署。

## 项目结构

```
RD-Agent/
├── rdagent/              # 核心代码
├── scripts/              # 工具脚本
├── claude_tools/         # 辅助工具
├── DEPLOYMENT_GUIDE_CN.md # 部署指南
├── quick_start.sh        # 快速启动脚本
└── .env.template         # 环境配置模板
```

## 环境要求

- Python 3.10+
- Conda/Miniconda
- 8GB+ RAM
- macOS/Linux/Windows

## 安装

```bash
# 克隆项目
git clone https://github.com/your-username/RD-Agent.git
cd RD-Agent

# 运行快速启动脚本
./quick_start.sh
```

## 配置

1. 复制 `.env.template` 为 `.env`
2. 填入您的API密钥和数据路径
3. 根据需要调整其他配置

## 文档

- [完整部署指南](DEPLOYMENT_GUIDE_CN.md)
- [环境配置说明](.env.template)
- [官方文档](https://github.com/microsoft/RD-Agent)

## 许可证

本项目基于 Microsoft RD-Agent，遵循其原始许可证。

## 贡献

欢迎提交Issue和Pull Request。

## 联系方式

如有问题，请提交Issue。
EOF
        print_success "已创建 README.md"
    else
        print_info "README.md 已存在，跳过创建"
    fi
}

# 创建GitHub Actions配置
create_github_actions() {
    print_info "创建GitHub Actions配置..."
    
    mkdir -p .github/workflows
    
    cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11"]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=rdagent --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      if: matrix.python-version == '3.10'
      with:
        file: ./coverage.xml
EOF
    
    print_success "已创建 GitHub Actions CI配置"
}

# 生成上传指南
generate_upload_guide() {
    print_info "生成GitHub上传指南..."
    
    cat > GITHUB_UPLOAD_GUIDE.md << 'EOF'
# GitHub上传指南

## 准备步骤（已完成）

1. ✅ 移除敏感信息
2. ✅ 创建示例配置文件
3. ✅ 准备文档
4. ✅ 设置.gitignore

## 上传步骤

### 1. 初始化Git仓库（如果尚未初始化）

```bash
git init
git add .
git commit -m "Initial commit: RD-Agent ETF Factor Mining System"
```

### 2. 创建GitHub仓库

1. 登录 [GitHub](https://github.com)
2. 点击 "New repository"
3. 填写仓库信息:
   - Repository name: `RD-Agent-ETF`
   - Description: `ETF Factor Mining System based on Microsoft RD-Agent`
   - Visibility: Private（建议先设为私有）
   - 不要初始化README、.gitignore或LICENSE

### 3. 连接远程仓库

```bash
# 替换YOUR_USERNAME为您的GitHub用户名
git remote add origin https://github.com/YOUR_USERNAME/RD-Agent-ETF.git
```

### 4. 推送代码

```bash
# 推送到main分支
git branch -M main
git push -u origin main
```

### 5. 创建开发分支

```bash
# 创建并切换到develop分支
git checkout -b develop
git push -u origin develop
```

## 推荐的分支策略

- `main`: 稳定版本
- `develop`: 开发版本
- `feature/*`: 功能开发
- `hotfix/*`: 紧急修复

## 设置仓库保护

1. 进入 Settings → Branches
2. 添加规则保护 `main` 分支:
   - Require pull request reviews
   - Require status checks to pass
   - Include administrators

## 添加协作者

1. 进入 Settings → Manage access
2. 点击 "Invite a collaborator"
3. 输入协作者的GitHub用户名

## 设置Secrets（用于CI/CD）

1. 进入 Settings → Secrets and variables → Actions
2. 添加以下secrets:
   - `OPENAI_API_KEY`: OpenAI API密钥（用于测试）
   - 其他需要的密钥

## 创建Release

当准备发布版本时:

```bash
# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

然后在GitHub上创建Release:
1. 进入 Releases → Create a new release
2. 选择标签
3. 填写发布说明

## 注意事项

1. **绝不要提交真实的API密钥**
2. 定期检查提交历史，确保没有敏感信息
3. 使用GitHub Secrets管理敏感配置
4. 保持.gitignore更新
5. 编写清晰的提交信息

## 提交信息规范

建议使用以下格式:

- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式化
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例:
```bash
git commit -m "feat: 添加momentum20d因子支持"
git commit -m "fix: 修复IC值计算错误"
git commit -m "docs: 更新部署文档"
```

## 完成检查清单

- [ ] 所有敏感信息已移除
- [ ] .env文件已删除
- [ ] .env.example已创建
- [ ] README.md已更新
- [ ] 文档完整
- [ ] .gitignore配置正确
- [ ] 测试通过
- [ ] CI/CD配置完成

---
*生成时间: $(date)*
EOF
    
    print_success "已生成 GITHUB_UPLOAD_GUIDE.md"
}

# 创建最终检查清单
create_checklist() {
    print_info "创建最终检查清单..."
    
    cat > UPLOAD_CHECKLIST.txt << 'EOF'
GitHub上传前检查清单
====================

安全检查:
□ .env文件已删除
□ API密钥已移除
□ 密码已移除
□ 私钥文件已删除
□ 数据库文件已排除

文档检查:
□ README.md已创建
□ DEPLOYMENT_GUIDE_CN.md已更新
□ .env.example已创建
□ .env.template完整
□ LICENSE文件存在

代码检查:
□ 硬编码的路径已修改为相对路径
□ 测试数据已准备
□ 依赖列表已更新(pyproject.toml)
□ 版本号已设置

Git检查:
□ .gitignore配置正确
□ 没有大文件(>100MB)
□ 提交历史干净
□ 分支结构清晰

测试检查:
□ 单元测试通过
□ 集成测试通过
□ 文档中的命令可执行
□ 快速启动脚本可运行

最终确认:
□ 项目可以全新克隆并运行
□ 所有路径使用环境变量
□ 交付文档完整清晰
□ 联系方式已提供

---
检查人: ________________
日期: __________________
EOF
    
    print_success "已创建 UPLOAD_CHECKLIST.txt"
}

# 生成项目统计
generate_statistics() {
    print_info "生成项目统计..."
    
    echo "项目统计信息" > PROJECT_STATS.txt
    echo "===========" >> PROJECT_STATS.txt
    echo "" >> PROJECT_STATS.txt
    
    echo "代码统计:" >> PROJECT_STATS.txt
    echo -n "Python文件数: " >> PROJECT_STATS.txt
    find . -name "*.py" -not -path '*/\.*' | wc -l >> PROJECT_STATS.txt
    
    echo -n "总代码行数: " >> PROJECT_STATS.txt
    find . -name "*.py" -not -path '*/\.*' -exec wc -l {} \; | awk '{sum+=$1} END {print sum}' >> PROJECT_STATS.txt
    
    echo "" >> PROJECT_STATS.txt
    echo "文件大小:" >> PROJECT_STATS.txt
    du -sh . >> PROJECT_STATS.txt
    
    echo "" >> PROJECT_STATS.txt
    echo "主要目录:" >> PROJECT_STATS.txt
    du -sh rdagent scripts claude_tools 2>/dev/null >> PROJECT_STATS.txt
    
    print_success "已生成 PROJECT_STATS.txt"
}

# 主函数
main() {
    clear
    echo "=========================================="
    echo "   RD-Agent GitHub上传准备工具"
    echo "=========================================="
    echo ""
    
    # 执行检查和准备
    check_directory
    print_separator
    
    backup_env_files
    print_separator
    
    check_sensitive_info
    print_separator
    
    # 确保.gitignore正确配置
    ensure_gitignore
    print_separator
    
    create_readme
    print_separator
    
    create_github_actions
    print_separator
    
    generate_upload_guide
    print_separator
    
    create_checklist
    print_separator
    
    generate_statistics
    print_separator
    
    # 完成提示
    echo ""
    print_success "✅ GitHub上传准备完成！"
    echo ""
    echo "下一步操作:"
    echo "1. 查看 UPLOAD_CHECKLIST.txt 完成最终检查"
    echo "2. 阅读 GITHUB_UPLOAD_GUIDE.md 了解上传步骤"
    echo "3. 确认所有敏感信息已移除"
    echo "4. 执行git命令上传到GitHub"
    echo ""
    echo "重要文件:"
    echo "- .env.example (示例配置)"
    echo "- .env.template (完整配置模板)"
    echo "- DEPLOYMENT_GUIDE_CN.md (部署指南)"
    echo "- GITHUB_UPLOAD_GUIDE.md (上传指南)"
    echo ""
    
    # 显示统计信息
    if [ -f "PROJECT_STATS.txt" ]; then
        echo "项目统计:"
        cat PROJECT_STATS.txt
    fi
}

# 运行主函数
main "$@"