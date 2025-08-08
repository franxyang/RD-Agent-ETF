# 🚀 快速上传到GitHub

## 方法一：自动上传（推荐）

```bash
# 运行自动上传脚本
chmod +x upload_to_github.sh
./upload_to_github.sh
```

按提示输入：
- GitHub用户名
- 仓库名称（建议：RD-Agent-ETF）
- 选择私有/公开
- 选择HTTPS/SSH连接

## 方法二：手动上传

### 1️⃣ 准备工作
```bash
# 运行准备脚本（保留.env，更新.gitignore）
./scripts/prepare_github_upload.sh
```

### 2️⃣ 创建本地仓库
```bash
git init
git add .
git commit -m "Initial commit"
```

### 3️⃣ 创建GitHub仓库
访问 https://github.com/new
- 仓库名：RD-Agent-ETF
- 设为Private
- 不要添加README/LICENSE/.gitignore

### 4️⃣ 推送代码
```bash
# 替换YOUR_USERNAME
git remote add origin https://github.com/franxyang/RD-Agent-ETF.git
git push -u origin main
```

## 📝 注意事项

✅ **会保留的文件**：
- .env（本地继续使用）
- 所有代码和文档

❌ **不会上传的文件**（.gitignore自动处理）：
- .env（包含API密钥）
- *.key, *.pem
- git_ignore_folder/
- pickle_cache/

## 🔑 GitHub认证

### 使用Token（HTTPS）
1. 访问 https://github.com/settings/tokens
2. Generate new token (classic)
3. 勾选 `repo` 权限
4. 推送时用token作为密码

### 使用SSH
```bash
ssh-keygen -t ed25519
cat ~/.ssh/id_ed25519.pub
# 复制公钥到 GitHub Settings → SSH keys
```

## ✨ 完成后

您的项目地址：
```
https://github.com/YOUR_USERNAME/RD-Agent-ETF
```

这是**您的独立项目**，与微软官方无关，您拥有完全控制权。

---
*更多详情见 [GITHUB_UPLOAD_GUIDE.md](GITHUB_UPLOAD_GUIDE.md)*