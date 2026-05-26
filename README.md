# 游戏折扣页面自动部署项目

这是一个自动更新的游戏折扣信息页面，每天定时抓取 Steam 促销、PSN 港服价格和小黑盒游戏图片，生成静态 HTML 部署到 GitHub Pages。

## 功能特性

- 🔥 **每日自动更新**：GitHub Actions 每天 8:00（北京时间）自动运行
- 🎮 **多平台比价**：Steam 国区、PSN 港服、Switch eShop 港服
- 🖼️ **自动获取图片**：从小黑盒 API 获取游戏封面图
- 📱 **响应式设计**：适配手机和桌面设备
- 🚀 **零成本部署**：完全基于 GitHub Pages + Actions

## 文件结构

```
game-deals/
├── .github/workflows/deploy.yml    # GitHub Actions 工作流
├── update_page.py                  # 主更新脚本
├── requirements.txt                # Python 依赖
├── README.md                       # 本文件
└── index.html                      # 生成的页面（自动生成）
```

## 部署步骤

### 1. 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名：`game-deals`（或其他名称）
3. **重要**：选择 **Public**（GitHub Pages 需要公开仓库）
4. 不要勾选 "Initialize this repository with a README"

### 2. 上传文件到仓库

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/game-deals.git
cd game-deals

# 复制所有文件到仓库目录
cp -r /Users/hanxiaopeng/Games/game-deals/* .

# 提交并推送
git add .
git commit -m "初始提交：游戏折扣页面"
git push origin main
```

### 3. 启用 GitHub Pages

1. 进入仓库 Settings → Pages
2. Source：选择 **GitHub Actions**
3. 保存设置

### 4. 手动触发首次运行

1. 进入仓库 Actions 标签页
2. 找到 "每日更新游戏折扣页面" 工作流
3. 点击 "Run workflow" → "Run workflow"

## 自定义配置

### 修改更新频率

编辑 `.github/workflows/deploy.yml` 中的 cron 表达式：
- `'0 0 * * *'` = 每天 UTC 0:00（北京时间 8:00）
- `'0 12 * * *'` = 每天 UTC 12:00（北京时间 20:00）

### 修改游戏列表

编辑 `update_page.py` 中的函数：
- `fetch_steam_deals()`：修改 Steam 促销游戏
- `new_hot_games`：修改近期新游
- `eshop_prices`：修改 Switch 价格数据

### 修改页面样式

编辑 `update_page.py` 中的 `generate_html()` 函数，修改 CSS 或 HTML 结构。

## 工作原理

```
每天定时触发
    ↓
GitHub Actions 运行 update_page.py
    ↓
脚本执行：
  1. 获取 Steam 促销数据
  2. 从小黑盒 API 获取游戏图片
  3. 爬取 PSN 港服价格
  4. 生成 index.html
    ↓
Actions 自动部署到 GitHub Pages
    ↓
用户访问 https://YOUR_USERNAME.github.io/game-deals/
```

## 注意事项

1. **API 限制**：小黑盒 API 有频率限制，脚本已加入延迟
2. **PSN 爬取**：PlayStation Store 可能更新页面结构，需要定期维护
3. **图片失效**：Steam CDN 图片可能变化，脚本有 fallback 机制
4. **GitHub 限制**：Actions 每月有免费额度，足够每日运行

## 故障排除

### 页面不更新
- 检查 Actions 运行日志
- 确认 cron 表达式正确
- 查看 Python 脚本错误信息

### 图片不显示
- 检查网络连接
- 确认小黑盒 API 是否可用
- 查看浏览器控制台错误

### 部署失败
- 检查仓库是否为 Public
- 确认 Pages 设置正确
- 查看 Actions 权限设置

## 许可证

MIT License - 自由使用和修改