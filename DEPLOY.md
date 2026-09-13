# 🚀 部署指南

## 1. 准备工作

### 1.1 创建 GitHub 仓库
1. 登录 [GitHub](https://github.com)
2. 点击右上角 "+" → "New repository"
3. 填写仓库名（如 `game-deals`）
4. 选择 Public（公开）
5. 点击 "Create repository"

### 1.2 本地准备
```bash
# 进入项目目录
cd /Users/hanxiaopeng/Games/game-deals

# 初始化 Git
git init

# 添加远程仓库
git remote add origin https://github.com/你的用户名/仓库名.git
```

## 2. 首次推送

```bash
# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit: Game Deals Hub"

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 3. 启用 GitHub Pages

1. 进入你的仓库页面
2. 点击 "Settings" 标签页
3. 左侧选择 "Pages"
4. 在 "Source" 部分：
   - 选择 "GitHub Actions"
5. 点击 "Save"

## 4. 手动触发首次部署

1. 进入仓库的 "Actions" 标签页
2. 选择 "Deploy to GitHub Pages" 工作流
3. 点击 "Run workflow"
4. 选择 "Run workflow" 按钮

等待约 1-2 分钟，工作流完成后：
- 绿色勾号表示成功
- 点击工作流运行，查看详细日志

## 5. 访问页面

部署成功后，访问：
```
https://你的用户名.github.io/仓库名/
```

例如：
```
https://hxp78522.github.io/game-deals/
```

## 6. 验证部署

### 6.1 检查 GitHub Pages
1. 回到仓库 Settings → Pages
2. 应该显示 "Your site is live at https://..."

### 6.2 检查 Actions
1. Actions 标签页应有成功的工作流运行记录
2. 点击运行记录可查看详细日志

### 6.3 检查页面内容
1. 打开部署的页面
2. 检查各栏目是否正常显示
3. 测试响应式布局（调整浏览器窗口大小）

## 7. 日常维护

### 7.1 自动更新
- 每天 UTC 0:00（北京时间 8:00）自动运行
- 无需手动操作

### 7.2 手动更新
如需立即更新：
1. 进入 Actions 标签页
2. 点击 "Deploy to GitHub Pages"
3. 点击 "Run workflow"

### 7.3 修改内容后更新
```bash
# 修改文件后
git add .
git commit -m "更新描述"
git push origin main
```
推送后会自动触发部署

## 8. 故障排除

### 8.1 页面无法访问
- 检查 GitHub Pages 是否已启用
- 检查 Actions 工作流是否成功
- 等待几分钟（首次部署可能需要时间）

### 8.2 工作流失败
- 检查 Actions 日志中的错误信息
- 常见问题：
  - 缺少 Python 依赖：确保 `requests` 已安装
  - API 请求失败：网络问题或 API 限制
  - 权限问题：确保 GITHUB_TOKEN 权限足够

### 8.3 图片不显示
- 检查网络控制台是否有 404 错误
- 可能是图片源 API 限制
- fallback 机制应确保至少显示占位符

### 8.4 样式问题
- 清除浏览器缓存
- 检查 CSS 是否正确加载
- 测试不同设备尺寸

## 9. 自定义配置

### 9.1 修改更新频率
编辑 `.github/workflows/deploy.yml`：
```yaml
schedule:
  # 每天 UTC 0:00 运行（北京时间 8:00）
  - cron: '0 0 * * *'
  # 可改为每小时：'0 * * * *'
```

### 9.2 修改游戏数据
编辑 `update_page.py` 中的：
- `fetch_steam_deals()` 函数
- `new_hot_games` 列表
- `physical_games` 列表

### 9.3 修改样式
编辑 `update_page.py` 中的 `generate_html()` 函数的 CSS 部分

## 10. 高级功能

### 10.1 自定义域名
1. 在域名服务商添加 CNAME 记录：
   ```
   yourdomain.com CNAME 你的用户名.github.io
   ```
2. 在仓库 Settings → Pages → Custom domain 填写域名
3. 勾选 "Enforce HTTPS"

### 10.2 添加分析
在 `generate_html()` 的 `<head>` 部分添加 Google Analytics 等代码

### 10.3 邮件通知
在 `.github/workflows/deploy.yml` 中添加失败通知

## 11. 安全建议

1. **不要提交敏感信息**
   - 不要在代码中包含 API 密钥
   - 使用 GitHub Secrets 存储敏感数据

2. **定期更新依赖**
   ```bash
   pip install --upgrade requests
   ```

3. **监控 API 使用**
   - 小黑盒 API 可能有频率限制
   - 如有需要可增加延迟时间

## 12. 支持

如有问题：
1. 查看 [GitHub Actions 文档](https://docs.github.com/actions)
2. 查看 [GitHub Pages 文档](https://docs.github.com/pages)
3. 提交 Issue 到本仓库

---

✅ 部署完成后，你的游戏折扣页面将每天自动更新，无需人工干预！