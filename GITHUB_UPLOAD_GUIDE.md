# GitHub独立项目上传指南

## 快速上传步骤

### 1. 准备工作

```bash
# 运行准备脚本（移除敏感信息）
chmod +x scripts/prepare_github_upload.sh
./scripts/prepare_github_upload.sh
```

### 2. 初始化本地Git仓库

```bash
# 如果还没有初始化Git
git init

# 设置用户信息（如果需要）
git config user.name "Yifan Yang"
git config user.email "yifanxyang@gmail.com"

# 添加所有文件
git add .

# 创建初始提交
git commit -m "Initial commit: RD-Agent ETF Factor Mining System"
```

### 3. 在GitHub创建新仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息:
   - **Repository name**: `RD-Agent-ETF` (或您喜欢的名字)
   - **Description**: `基于RD-Agent的ETF因子挖掘系统`
   - **Public/Private**: 选择Private（推荐私有）
   - ⚠️ **重要**: 不要勾选以下选项
     - ❌ Add a README file
     - ❌ Add .gitignore
     - ❌ Choose a license

### 4. 连接并推送到GitHub

```bash
# 添加远程仓库（替换YOUR_USERNAME为您的GitHub用户名）
git remote add origin https://github.com/franxyang/RD-Agent-ETF.git

# 或使用SSH（如果配置了SSH密钥）
git remote add origin git@github.com:YOUR_USERNAME/RD-Agent-ETF.git

# 推送代码
git branch -M main
git push -u origin main
```

## 常见问题

### 如果遇到认证问题

GitHub现在需要使用个人访问令牌(PAT)而不是密码：

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 填写：
   - Note: `RD-Agent Upload`
   - Expiration: 选择合适的过期时间
   - Select scopes: 勾选 `repo` (全部)
4. 生成并复制token
5. 推送时使用token作为密码：
   ```bash
   Username: YOUR_USERNAME
   Password: ghp_xxxxxxxxxxxxxxxxxxxx (您的token)
   ```

### 如果想使用SSH

```bash
# 检查是否有SSH密钥
ls -la ~/.ssh

# 如果没有，生成新密钥
ssh-keygen -t ed25519 -C "your-email@example.com"

# 添加到ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 复制公钥
cat ~/.ssh/id_ed25519.pub

# 添加到GitHub: Settings → SSH and GPG keys → New SSH key
# 然后使用SSH URL
git remote set-url origin git@github.com:YOUR_USERNAME/RD-Agent-ETF.git
```

## 后续管理

### 更新代码

```bash
# 查看修改
git status

# 添加修改
git add .

# 提交
git commit -m "更新说明"

# 推送
git push
```

### 创建备份分支

```bash
# 创建并切换到新分支
git checkout -b backup-$(date +%Y%m%d)

# 推送备份分支
git push -u origin backup-$(date +%Y%m%d)

# 切回主分支
git checkout main
```

### 添加协作者（如果需要）

1. 进入仓库 Settings → Manage access
2. 点击 "Invite a collaborator"
3. 输入协作者的GitHub用户名或邮箱

## 安全建议

### 1. 确认敏感信息已移除

```bash
# 检查是否有API密钥
grep -r "sk-" . --exclude-dir=.git --exclude="*.md"

# 检查.env文件是否已删除
ls -la | grep "\.env$"
```

### 2. 设置仓库为私有

除非必要，建议保持仓库私有：
- Settings → General → Danger Zone → Change visibility

### 3. 添加密钥到GitHub Secrets（可选）

如果需要在GitHub Actions中使用API密钥：
1. Settings → Secrets and variables → Actions
2. New repository secret
3. 添加需要的密钥（如 OPENAI_API_KEY）

## 完整性检查

上传前确认：
- ✅ .env文件已删除
- ✅ .env.example已创建（不含真实密钥）
- ✅ .env.template完整（配置说明文档）
- ✅ .gitignore包含敏感文件类型
- ✅ README.md已更新
- ✅ 部署文档完整

## 克隆测试

上传后，测试能否正常克隆使用：

```bash
# 克隆到新目录
cd /tmp
git clone https://github.com/YOUR_USERNAME/RD-Agent-ETF.git test-clone
cd test-clone

# 检查文件
ls -la

# 设置环境
cp .env.example .env
# 编辑.env填入真实配置

# 测试运行
./quick_start.sh
```

---

## 注意事项

1. 这是您的**独立项目**，与微软官方RD-Agent仓库无关
2. 您拥有完全的控制权，可以自由修改
3. 建议定期备份重要数据
4. 保持.gitignore更新，防止意外提交敏感信息

---

*生成时间: 2025-08-08*