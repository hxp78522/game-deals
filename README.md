# 🎮 Game Deals Hub

自动更新的游戏折扣与最新上线推荐页面，每日抓取 Steam、PSN 港服、Switch 港服价格对比。

## ✨ 功能特性

- **每日自动更新**：通过 GitHub Actions 每天自动抓取最新数据
- **多平台比价**：Steam、PSN 港服、Switch 港服价格对比
- **响应式设计**：完美适配桌面、平板、手机等所有设备
- **智能图片加载**：多级回退机制，确保封面图始终显示
- **一键购买**：直接跳转各平台官方商店页面

## 📱 页面预览

![页面截图](https://via.placeholder.com/800x450/0a0e17/00d4ff?text=Game+Deals+Hub)

### 主要栏目

1. **今日折扣** - Steam 当前促销游戏，按折扣力度分类
2. **近期火爆新游** - 最新发售的热门游戏
3. **三平台比价** - Steam、PSN、Switch 价格对比表格
4. **PS5实体盘推荐** - PS5 实体盘价格参考

## 🚀 快速部署

### 1. Fork 本仓库

点击右上角 Fork 按钮，将仓库复制到你的 GitHub 账户。

### 2. 启用 GitHub Pages

1. 进入你的仓库 Settings → Pages
2. Source 选择 **GitHub Actions**
3. 保存设置

### 3. 配置自动更新

第一次需要手动触发一次工作流：
1. 进入 Actions 标签页
2. 选择 "Deploy to GitHub Pages" 工作流
3. 点击 "Run workflow"

### 4. 访问页面

部署完成后，访问：`https://[你的用户名].github.io/[仓库名]/`

## ⚙️ 本地运行

```bash
# 克隆仓库
git clone https://github.com/你的用户名/game-deals.git
cd game-deals

# 安装依赖
pip install requests

# 运行更新脚本
python update_page.py

# 在浏览器中打开
open index.html  # macOS
# 或
start index.html  # Windows
```

## 📊 数据来源

- **Steam 促销数据**：通过 steam-sale-advisor 技能获取
- **小黑盒图片**：小黑盒游戏详情 API
- **PSN 价格**：PlayStation Store 港服页面爬取
- **新游数据**：手动维护的近期热门游戏列表

## 🔧 技术栈

- **Python 3.10+**：数据抓取与处理
- **Requests**：HTTP 请求库
- **GitHub Actions**：自动化部署
- **GitHub Pages**：静态页面托管
- **纯 HTML/CSS/JS**：前端展示

## 📅 更新频率

- **自动更新**：每天 UTC 0:00（北京时间 8:00）
- **手动触发**：可在 Actions 页面随时手动运行
- **推送触发**：每次推送到 main 分支时自动更新

## 🛠️ 自定义配置

### 修改游戏列表

编辑 `update_page.py` 中的以下部分：

```python
# Steam 促销游戏
def fetch_steam_deals():
    # 返回游戏列表

# 近期火爆新游
new_hot_games = [
    # 游戏配置
]

# PS5 实体盘
physical_games = [
    # 游戏配置
]
```

### 调整样式

CSS 样式直接内嵌在 `update_page.py` 的 `generate_html()` 函数中，可自由修改。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源。

## ⚠️ 免责声明

- 本页面仅作信息展示，不保证价格准确性
- 购买请前往各平台官方商店
- 价格以各平台实时显示为准
- 本工具仅供学习交流使用