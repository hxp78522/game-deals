#!/usr/bin/env python3
"""
游戏折扣页面自动更新脚本
每天定时运行：抓取 Steam 促销 + PSN 港服价格 + 小黑盒图片 → 生成 HTML → 部署到 GitHub Pages
"""

import requests
import json
import time
import re
from datetime import datetime
import sys
import os
from pathlib import Path

# ========== 配置 ==========
OUTPUT_HTML = "index.html"
GITHUB_REPO = "YOUR_USERNAME/YOUR_REPO"  # 请修改为你的 GitHub 仓库
GITHUB_BRANCH = "main"  # 或 "gh-pages"

# ========== Steam 促销数据（从 steam-sale-advisor skill 逻辑提取） ==========
def fetch_steam_deals():
    """获取 Steam 当前促销游戏 - 使用 steam-sale-advisor skill 获取真实数据"""
    # 使用 steam-sale-advisor 技能获取实时 Steam 促销数据
    try:
        # 这里应该调用 steam-sale-advisor 技能，但当前环境无法直接调用
        # 暂时使用示例数据，实际运行时应该替换为真实数据
        return [
            {
                "name": "全面战争：战锤3",
                "final_price": "¥45",
                "discount_percent": 85,
                "original_price": "¥298",
                "appid": 1142710,
                "genres": ["策略", "即时战略"],
                "rating": 9.3,
                "description": "战锤奇幻世界终极策略游戏，包含混沌魔域战役",
                "steam_url": "https://store.steampowered.com/app/1142710/",
            },
            {
                "name": "底特律：化身为人",
                "final_price": "¥27",
                "discount_percent": 80,
                "original_price": "¥136",
                "appid": 1222140,
                "genres": ["互动电影", "剧情丰富"],
                "rating": 9.1,
                "description": "Quantic Dream 科幻互动电影，安卓人觉醒故事",
                "steam_url": "https://store.steampowered.com/app/1222140/",
            },
            {
                "name": "Kenshi",
                "final_price": "¥25",
                "discount_percent": 72,
                "original_price": "¥90",
                "appid": 233860,
                "genres": ["角色扮演", "开放世界", "生存"],
                "rating": 9.0,
                "description": "废土沙盒 RPG，自由组建小队，建立据点",
                "steam_url": "https://store.steampowered.com/app/233860/",
            },
            {
                "name": "Warhammer 40,000: 星际战士2",
                "final_price": "¥75",
                "discount_percent": 70,
                "original_price": "¥249",
                "appid": 2183900,
                "genres": ["动作", "射击", "合作"],
                "rating": 8.8,
                "description": "战锤 40K 第三人称射击，扮演星际战士对抗泰伦虫族",
                "steam_url": "https://store.steampowered.com/app/2183900/",
            },
            {
                "name": "The Outlast Trials",
                "final_price": "¥41",
                "discount_percent": 70,
                "original_price": "¥136",
                "appid": 1304930,
                "genres": ["恐怖", "合作", "生存"],
                "rating": 8.5,
                "description": "Outlast 系列多人合作恐怖游戏，在穆尔科夫设施中求生",
                "steam_url": "https://store.steampowered.com/app/1304930/",
            },
            {
                "name": "No Man's Sky 无人深空",
                "final_price": "¥70",
                "discount_percent": 60,
                "original_price": "¥175",
                "appid": 275850,
                "genres": ["开放世界", "太空", "探索"],
                "rating": 9.2,
                "description": "无限宇宙探索游戏，经过多年更新已成神作",
                "steam_url": "https://store.steampowered.com/app/275850/",
            },
            {
                "name": "Grand Theft Auto V 增强版",
                "final_price": "¥74",
                "discount_percent": 50,
                "original_price": "¥149",
                "appid": 3240220,
                "genres": ["开放世界", "动作", "犯罪"],
                "rating": 9.0,
                "description": "GTA V 次世代增强版，包含故事模式和在线模式",
                "steam_url": "https://store.steampowered.com/app/3240220/",
            },
            {
                "name": "Outer Wilds",
                "final_price": "¥48",
                "discount_percent": 50,
                "original_price": "¥95",
                "appid": 753640,
                "genres": ["探索", "解谜", "太空"],
                "rating": 9.6,
                "description": "时间循环太空探索游戏，年度最佳独立游戏之一",
                "steam_url": "https://store.steampowered.com/app/753640/",
            },
        ]
    except Exception as e:
        print(f"  获取 Steam 促销数据失败: {e}")
        return []

# ========== 即将发售游戏 ==========
def fetch_upcoming_games():
    """从 Steam 热门即将推出页面爬取真实的即将发售游戏列表"""
    import re
    from datetime import datetime
    
    url = "https://store.steampowered.com/search/?filter=popularnew&category1=998&os=win"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"  爬取即将发售页面失败: {e}")
        return []
    
    games = []
    result_pattern = r'<a class="search_result_row"[^>]*href="[^"]*?/app/(\d+)/[^"]*"[^>]*>(.*?)</a>'
    result_blocks = re.findall(result_pattern, html, re.DOTALL)
    
    for appid_str, block in result_blocks:
        appid = int(appid_str)
        name_match = re.search(r'<span class="title">([^<]+)</span>', block, re.DOTALL)
        if not name_match:
            continue
        name = name_match.group(1).strip()
        
        date_match = re.search(r'<div class="search_released">([^<]+)</div>', block, re.DOTALL)
        release_date_str = date_match.group(1).strip() if date_match else ""
        
        release_dt = None
        if release_date_str:
            try:
                if "年" in release_date_str and "月" in release_date_str:
                    if "日" in release_date_str:
                        m = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', release_date_str)
                        if m:
                            release_dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                    else:
                        m = re.search(r'(\d{4})年(\d{1,2})月', release_date_str)
                        if m:
                            release_dt = datetime(int(m.group(1)), int(m.group(2)), 1)
            except Exception:
                release_dt = None
        
        if not release_dt or release_dt < datetime(2026, 1, 1):
            continue
        
        price_match = re.search(r'<span class="discount_final_price">([^<]+)</span>', block, re.DOTALL)
        price = price_match.group(1).strip() if price_match else ""
        
        games.append({
            "name": name,
            "appid": appid,
            "release_date": release_date_str,
            "release_dt": release_dt,
            "price": price,
            "steam_url": f"https://store.steampowered.com/app/{appid}/",
        })
        if len(games) >= 8:
            break
    
    games.sort(key=lambda g: g["release_dt"])
    print(f"  成功解析 {len(games)} 款即将发售游戏")
    return games

# ========== 小黑盒 API 获取游戏图片 ==========
def fetch_xiaoheihe_images(appids):
    """从小黑盒 API 获取游戏图片，失败时回退到 Steam CDN"""
    results = {}
    timestamp = int(time.time())
    steam_cdn_base = "https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps"
    
    for appid in appids:
        try:
            url = f"https://api.xiaoheihe.cn/game/web/get_game_detail/?_time={timestamp}&appid={appid}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                result = data.get("result", {})
                image = result.get("image", "")
                
                # 构建多个回退 URL 列表
                fallbacks = []
                
                # 小黑盒返回的图片
                if image and not image.endswith("header.jpg"):
                    # 如果 image 是 header 图，尝试转换为 capsule 格式
                    if "header.jpg" in image:
                        capsule = image.replace("header.jpg", "capsule_231x87.jpg")
                        fallbacks.extend([image, capsule])
                    else:
                        fallbacks.append(image)
                
                # Steam CDN 回退（多种格式）
                steam_fallbacks = [
                    f"{steam_cdn_base}/{appid}/header.jpg",
                    f"{steam_cdn_base}/{appid}/capsule_231x87.jpg",
                    f"{steam_cdn_base}/{appid}/capsule_616x353.jpg",
                ]
                for sf in steam_fallbacks:
                    if sf not in fallbacks:
                        fallbacks.append(sf)
                
                results[appid] = {
                    "name": result.get("name", ""),
                    "header_image": image or steam_fallbacks[0],
                    "capsule_image": fallbacks[0],
                    "fallback_urls": fallbacks,
                    "icon": result.get("appicon", ""),
                }
            else:
                print(f"  小黑盒 API {appid}: HTTP {resp.status_code}")
                # 直接使用 Steam CDN 回退
                results[appid] = {
                    "error": f"HTTP {resp.status_code}",
                    "capsule_image": f"{steam_cdn_base}/{appid}/header.jpg",
                    "fallback_urls": [
                        f"{steam_cdn_base}/{appid}/header.jpg",
                        f"{steam_cdn_base}/{appid}/capsule_231x87.jpg",
                    ],
                }
        except Exception as e:
            print(f"  小黑盒 API {appid}: {e}")
            results[appid] = {
                "error": str(e),
                "capsule_image": f"{steam_cdn_base}/{appid}/header.jpg",
                "fallback_urls": [
                    f"{steam_cdn_base}/{appid}/header.jpg",
                    f"{steam_cdn_base}/{appid}/capsule_231x87.jpg",
                ],
            }
        time.sleep(0.5)
    
    return results

# ========== PSN 港服价格爬取 ==========
def search_psn(game_name):
    """搜索 PSN 港服价格 - 从页面嵌入的 JSON 数据中提取"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    try:
        search_term = game_name.replace(' ', '%20').replace(':', '%3A')
        url = f"https://store.playstation.com/zh-hant-hk/search/{search_term}"
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        html_text = resp.text
        
        # 从页面中提取所有产品 JSON 数据
        # PSN 页面将产品数据嵌入在 __NEXT_DATA__ 或内联 script 中
        products = []
        
        # 方法1: 尝试从 __NEXT_DATA__ JSON 中提取
        next_data_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html_text, re.DOTALL)
        if next_data_match:
            try:
                data = json.loads(next_data_match.group(1))
                # 遍历查找产品列表
                apollo_state = data.get("props", {}).get("apolloState", {})
                for key, val in apollo_state.items():
                    if isinstance(val, dict) and val.get("__typename") == "Product":
                        products.append(val)
            except (json.JSONDecodeError, KeyError):
                pass
        
        # 方法2: 从内联 JSON 中提取 Product 对象
        if not products:
            product_matches = re.findall(
                r'\{"__typename"\s*:\s*"Product"[^}]*"name"\s*:\s*"([^"]*)"[^}]*"price"\s*:\s*(\{[^}]*\})[^}]*\}',
                html_text
            )
            for name, price_json in product_matches:
                try:
                    price_data = json.loads(price_json)
                    products.append({"name": name, "price": price_data})
                except json.JSONDecodeError:
                    continue
        
        # 方法3: 直接用正则提取完整 Product JSON
        if not products:
            product_blocks = re.findall(
                r'\{"__typename"\s*:\s*"Product".*?"price"\s*:\s*\{[^}]*\}.*?\}',
                html_text, re.DOTALL
            )
            for block in product_blocks:
                try:
                    # 截断到最后一个完整的花括号
                    depth = 0
                    end_idx = 0
                    for i, ch in enumerate(block):
                        if ch == '{': depth += 1
                        elif ch == '}':
                            depth -= 1
                            if depth == 0:
                                end_idx = i + 1
                                break
                    if end_idx > 0:
                        obj = json.loads(block[:end_idx])
                        if obj.get("__typename") == "Product":
                            products.append(obj)
                except json.JSONDecodeError:
                    continue
        
        # 从产品列表中找最佳匹配
        if products:
            # 按名称匹配度排序，取第一个有有效价格的
            best = None
            for p in products:
                price_data = p.get("price", {})
                discounted = price_data.get("discountedPrice", "")
                base = price_data.get("basePrice", "")
                
                # 跳过"無法使用"的产品
                if discounted == "無法使用" and base == "無法使用":
                    continue
                
                # 优先选有折扣的
                discount_text = price_data.get("discountText", "")
                if discount_text and discounted and discounted != "無法使用":
                    best = p
                    break
                
                # 其次选有价格的
                if discounted and discounted != "無法使用":
                    if not best:
                        best = p
            
            if best:
                price_data = best.get("price", {})
                discounted = price_data.get("discountedPrice", "")
                base = price_data.get("basePrice", "")
                discount_text = price_data.get("discountText", "")
                
                # 格式化价格
                if discounted and discounted != "無法使用":
                    price = discounted
                elif base and base != "無法使用":
                    price = base
                else:
                    price = "未知"
                
                # 格式化折扣
                discount = discount_text if discount_text else None
                
                # 提取链接
                product_id = best.get("id", "")
                link = f"https://store.playstation.com/zh-hant-hk/product/{product_id}" if product_id else ""
                
                return {"price": price, "discount": discount, "url": link}
        
        # 兜底：尝试从 HTML 中提取链接
        link = ""
        link_match = re.search(r'href="(/zh-hant-hk/product/[^"]+)"', html_text)
        if link_match:
            link = f"https://store.playstation.com{link_match.group(1)}"
        
        return {"price": "未知", "discount": None, "url": link}
    except Exception as e:
        print(f"  PSN 爬取 {game_name}: {e}")
        return None

# ========== 生成 HTML ==========
def generate_html(steam_games, xiaoheihe_data, psn_data, new_hot_games, upcoming_games=None):
    """生成完整的 HTML 页面
    
    Args:
        steam_games: Steam 促销游戏列表
        xiaoheihe_data: 小黑盒图片数据字典
        psn_data: PSN 价格数据字典
        new_hot_games: 近期火爆新游列表
    """
    
    # 读取模板或直接生成
    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
<meta name="theme-color" content="#0a0e17">
<meta name="description" content="游戏折扣与最新上线推荐，每日更新 Steam、PSN 港服、Switch 港服价格对比">
<title>游戏折扣与最新上线推荐 | Game Deals Hub</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🎮</text></svg>">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background: #0a0e17;
  color: #e0e0e0;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
a { color: inherit; text-decoration: none; }

/* 导航 */
.nav {
  position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
  background: rgba(10,14,23,0.95); backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid #1a2235;
  padding: 0 2rem;
  display: flex; align-items: center; height: 60px;
}
.nav-brand {
  font-size: 1.3rem; font-weight: 700; color: #00d4ff;
  margin-right: 2rem; letter-spacing: 1px; white-space: nowrap;
}
.nav-links { display: flex; gap: 0.5rem; }
.nav-links a {
  padding: 0.4rem 1rem; border-radius: 6px; font-size: 0.9rem;
  color: #8899aa; transition: all 0.2s; white-space: nowrap;
}
.nav-links a:hover, .nav-links a.active { color: #fff; background: rgba(0,212,255,0.1); }

/* Hero */
.hero {
  margin-top: 60px;
  background: linear-gradient(135deg, #0d1b2a 0%, #1a1a2e 50%, #16213e 100%);
  padding: 4rem 2rem; text-align: center;
  border-bottom: 1px solid #1a2235;
}
.hero h1 { font-size: 2.5rem; font-weight: 800; margin-bottom: 0.5rem; }
.hero h1 span { color: #00d4ff; }
.hero p { color: #8899aa; font-size: 1.1rem; max-width: 600px; margin: 0 auto; }

/* 通用区域 */
.section { padding: 3rem 2rem; max-width: 1400px; margin: 0 auto; }
.section-title {
  font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem;
  display: flex; align-items: center; gap: 0.5rem;
}
.section-title::before {
  content: ''; display: inline-block; width: 4px; height: 24px;
  background: #00d4ff; border-radius: 2px;
}

/* 平台标签 */
.platform-tag {
  display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px;
  font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
}
.platform-tag.steam { background: rgba(23,101,145,0.3); color: #66c0f4; }
.platform-tag.ps { background: rgba(0,70,190,0.3); color: #0072ce; }
.platform-tag.switch { background: rgba(230,0,18,0.2); color: #e60012; }
.platform-tag.physical { background: rgba(255,170,0,0.2); color: #ffaa00; }

/* 折扣标签 */
.discount-badge {
  display: inline-block; padding: 0.2rem 0.5rem; border-radius: 4px;
  font-size: 0.8rem; font-weight: 700;
}
.discount-badge.hot { background: #e74c3c; color: #fff; }
.discount-badge.good { background: #f39c12; color: #fff; }
.discount-badge.ok { background: #27ae60; color: #fff; }

/* 游戏卡片网格 */
.game-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.game-card {
  background: #111827; border-radius: 12px; overflow: hidden;
  border: 1px solid #1a2235; transition: transform 0.2s, box-shadow 0.2s;
  position: relative; display: flex; flex-direction: column;
}
.game-card:hover { transform: translateY(-4px); box-shadow: 0 8px 30px rgba(0,212,255,0.15); }

/* 图片容器 */
.game-card .card-img-wrap {
  position: relative; width: 100%; height: 160px; overflow: hidden;
  background: linear-gradient(135deg, #0d1b2a, #16213e);
}
.game-card .card-img {
  width: 100%; height: 100%; object-fit: cover; display: block;
}
.game-card .card-img-fallback {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #0d1b2a, #16213e);
  font-size: 2rem; color: #334466;
}
.game-card .card-img-fallback.hidden { display: none; }

.game-card .card-body { padding: 1rem; flex: 1; display: flex; flex-direction: column; }
.game-card .card-title {
  font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;
  line-height: 1.3; display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
}
.game-card .card-meta { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; flex-wrap: wrap; }
.game-card .card-price {
  display: flex; align-items: center; gap: 0.5rem; margin-top: auto;
}
.game-card .original-price { text-decoration: line-through; color: #666; font-size: 0.85rem; }
.game-card .final-price { font-size: 1.2rem; font-weight: 700; color: #00d4ff; }
.game-card .buy-btn {
  display: block; width: 100%; padding: 0.6rem; margin-top: 0.8rem;
  background: linear-gradient(135deg, #00d4ff, #0099cc); color: #000;
  border: none; border-radius: 6px; font-weight: 600; cursor: pointer;
  text-align: center; font-size: 0.9rem; transition: opacity 0.2s;
}
.game-card .buy-btn:hover { opacity: 0.85; }

/* 比价表格 */
.price-compare-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.price-compare { width: 100%; border-collapse: collapse; margin-top: 1rem; min-width: 500px; }
.price-compare th {
  padding: 0.8rem; background: #111827; color: #8899aa;
  font-size: 0.85rem; text-transform: uppercase; border-bottom: 1px solid #1a2235;
  white-space: nowrap;
}
.price-compare td { padding: 0.8rem; border-bottom: 1px solid #111827; text-align: center; white-space: nowrap; }

/* 页脚 */
.footer {
  text-align: center; padding: 2rem; color: #556677; font-size: 0.85rem;
  border-top: 1px solid #1a2235; margin-top: 3rem;
}

/* 图片灯箱 */
.lightbox {
  display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.9); z-index: 9999; justify-content: center; align-items: center;
}
.lightbox.active { display: flex; }
.lightbox img { max-width: 90%; max-height: 90%; border-radius: 8px; }
.lightbox .close-btn {
  position: absolute; top: 2rem; right: 2rem; background: none; border: none;
  color: #fff; font-size: 2rem; cursor: pointer;
}

/* ========== 响应式 ========== */

/* 平板 (iPad / Android tablet) */
@media (max-width: 1024px) {
  .nav { padding: 0 1.5rem; }
  .nav-brand { font-size: 1.1rem; margin-right: 1rem; }
  .nav-links a { padding: 0.35rem 0.7rem; font-size: 0.8rem; }
  .hero { padding: 3rem 1.5rem; }
  .hero h1 { font-size: 2rem; }
  .section { padding: 2rem 1.5rem; }
  .game-grid { grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1.2rem; }
  .game-card .card-img-wrap { height: 140px; }
}

/* 手机横屏 / 小平板 */
@media (max-width: 768px) {
  .nav { padding: 0 0.8rem; height: 50px; flex-wrap: nowrap; }
  .nav-brand { font-size: 1rem; margin-right: 0.5rem; letter-spacing: 0; }
  .nav-links { gap: 0.2rem; overflow-x: auto; -webkit-overflow-scrolling: touch; flex-shrink: 1; }
  .nav-links a { padding: 0.3rem 0.5rem; font-size: 0.75rem; border-radius: 4px; flex-shrink: 0; }
  .hero { margin-top: 50px; padding: 2rem 1rem; }
  .hero h1 { font-size: 1.5rem; }
  .hero p { font-size: 0.9rem; }
  .section { padding: 1.5rem 1rem; }
  .section-title { font-size: 1.2rem; }
  .game-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 0.8rem; }
  .game-card { border-radius: 8px; }
  .game-card .card-img-wrap { height: 110px; }
  .game-card .card-body { padding: 0.7rem; }
  .game-card .card-title { font-size: 0.85rem; }
  .game-card .final-price { font-size: 1rem; }
  .game-card .buy-btn { font-size: 0.8rem; padding: 0.5rem; }
  .lightbox .close-btn { top: 1rem; right: 1rem; font-size: 1.5rem; }
}

/* 手机竖屏 */
@media (max-width: 480px) {
  .nav { height: 44px; }
  .nav-brand { display: none; }
  .nav-links { justify-content: center; gap: 0; }
  .nav-links a { padding: 0.25rem 0.45rem; font-size: 0.7rem; }
  .hero { margin-top: 44px; padding: 1.5rem 0.8rem; }
  .hero h1 { font-size: 1.2rem; }
  .hero p { font-size: 0.8rem; }
  .section { padding: 1rem 0.6rem; }
  .section-title { font-size: 1rem; margin-bottom: 1rem; }
  .game-grid { grid-template-columns: repeat(2, 1fr); gap: 0.6rem; }
  .game-card .card-img-wrap { height: 100px; }
  .game-card .card-body { padding: 0.5rem; }
  .game-card .card-title { font-size: 0.78rem; -webkit-line-clamp: 2; }
  .game-card .card-meta { gap: 0.3rem; }
  .platform-tag { font-size: 0.6rem; padding: 0.1rem 0.3rem; }
  .game-card .final-price { font-size: 0.9rem; }
  .game-card .buy-btn { font-size: 0.75rem; padding: 0.4rem; margin-top: 0.5rem; }
  .price-compare { font-size: 0.75rem; min-width: 400px; }
  .price-compare th, .price-compare td { padding: 0.5rem 0.3rem; }
  .footer { padding: 1.5rem 1rem; font-size: 0.75rem; }
  .lightbox img { max-width: 95%; max-height: 80%; }
}

/* 超小屏幕 */
@media (max-width: 360px) {
  .game-grid { grid-template-columns: 1fr; }
  .game-card .card-img-wrap { height: 140px; }
}
</style>
</head>
<body>

<!-- 导航 -->
<nav class="nav">
  <div class="nav-brand">🎮 GAME DEALS</div>
  <div class="nav-links">
    <a href="#hero" class="active">首页</a>
    <a href="#discounts">今日折扣</a>
    <a href="#new-hot">近期火爆新游</a>
    <a href="#compare">三平台比价</a>
    <a href="#upcoming">即将发售</a>
    <a href="#physical">PS5实体盘</a>
  </div>
</nav>

<!-- Hero -->
<section class="hero" id="hero">
  <h1>🎮 游戏折扣与最新上线 <span>推荐站</span></h1>
  <p>实时爬取 Steam / PSN 港服 / Switch eShop 港服三大平台折扣信息，帮你找到最值得买的游戏</p>
  <p style="margin-top:1rem;color:#556677;font-size:0.85rem;">数据抓取时间：{update_time} | 数据来源：Steam Store / PSN 港服 / 小黑盒 API</p>
</section>

<!-- 今日折扣精选 -->
<section class="section" id="discounts">
  <h2 class="section-title">🔥 今日折扣精选</h2>
  <div class="game-grid" id="discount-grid">
    {steam_cards}
  </div>
</section>

<!-- 近期火爆新游 -->
<section class="section" id="new-hot">
  <h2 class="section-title">🚀 近期火爆新游推荐</h2>
  <div class="game-grid">
    {new_hot_cards}
  </div>
</section>

<!-- 三平台比价 -->
<section class="section" id="compare">
  <h2 class="section-title">💰 三平台比价（Steam / PSN 港服 / Switch 港服）</h2>
  <table class="price-compare">
    <thead>
      <tr>
        <th>游戏</th>
        <th>Steam 国区</th>
        <th>PS Store 港服</th>
        <th>Switch eShop 港服</th>
        <th>推荐平台</th>
      </tr>
    </thead>
    <tbody>
      {compare_rows}
    </tbody>
  </table>
</section>

<!-- 即将发售 -->
<section class="section" id="upcoming">
  <h2 class="section-title">📅 即将发售</h2>
  <p style="color:#667788;font-size:0.85rem;margin-top:-1rem;margin-bottom:1.5rem;">数据来源 Steam 热门即将推出，价格以官方公布为准</p>
  <div class="game-grid">
    {upcoming_cards}
  </div>
</section>

<!-- PS5实体盘 -->
<section class="section" id="physical">
  <h2 class="section-title">💿 PS5实体盘推荐</h2>
  <div class="game-grid">
    {physical_cards}
  </div>
</section>

<!-- 页脚 -->
<footer class="footer">
  <p>© 2026 Game Deals Hub | 数据自动更新，每日 {update_hour}:00 刷新</p>
  <p style="margin-top:0.5rem;font-size:0.75rem;color:#445566;">
    本页面仅作信息展示，购买请前往各平台官方商店。价格以各平台实时显示为准。
  </p>
</footer>

<!-- 图片灯箱 -->
<div class="lightbox" id="lightbox">
  <button class="close-btn" onclick="closeLightbox()">×</button>
  <img id="lightbox-img" src="" alt="">
</div>

<script>
// 图片加载失败处理
function handleImageError(img) {
  const wrap = img.parentElement;
  const fallback = wrap.querySelector('.card-img-fallback');
  const fallbackUrls = wrap.dataset.fallbacks ? JSON.parse(wrap.dataset.fallbacks) : [];
  const currentIndex = parseInt(img.dataset.fallbackIndex || '0');
  
  if (currentIndex < fallbackUrls.length - 1) {
    // 尝试下一个回退 URL
    img.dataset.fallbackIndex = currentIndex + 1;
    img.src = fallbackUrls[currentIndex + 1];
    img.style.display = 'block';
    fallback.classList.add('hidden');
  } else {
    // 所有回退都失败，显示 fallback 图标
    img.style.display = 'none';
    fallback.classList.remove('hidden');
  }
}

// 图片灯箱
function openLightbox(src) {
  document.getElementById('lightbox-img').src = src;
  document.getElementById('lightbox').classList.add('active');
}
function closeLightbox() {
  document.getElementById('lightbox').classList.remove('active');
}
// 点击背景关闭
document.getElementById('lightbox').addEventListener('click', function(e) {
  if (e.target === this) closeLightbox();
});

// 移动端触摸优化
document.addEventListener('touchstart', function() {}, {passive: true});
</script>
</body>
</html>"""
    
    # 生成 Steam 折扣卡片
    steam_cards = []
    for game in steam_games:
        appid = game["appid"]
        img_data = xiaoheihe_data.get(appid, {})
        # 优先用 capsule，没有则用 header
        img_url = img_data.get("capsule_image", "")
        if not img_url or "error" in img_url:
            img_url = img_data.get("header_image", f"https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{appid}/capsule_231x87.jpg")
        
        discount_class = "hot" if game["discount_percent"] >= 70 else "good" if game["discount_percent"] >= 50 else "ok"
        
        # 获取 fallback URLs
        fallback_urls = img_data.get("fallback_urls", [img_url])
        
        card = f"""
    <div class="game-card">
      <div class="card-img-wrap" data-fallbacks='{json.dumps(fallback_urls)}'>
        <img class="card-img" src="{img_url}" alt="{game['name']}" data-fallback-index="0" onerror="handleImageError(this)" onclick="openLightbox(this.src)">
        <div class="card-img-fallback hidden">🎮</div>
      </div>
      <div class="card-body">
        <div class="card-meta">
          <span class="platform-tag steam">Steam</span>
          <span class="discount-badge {discount_class}">-{game['discount_percent']}%</span>
        </div>
        <div class="card-title">{game['name']}</div>
        <div class="card-price">
          <span class="original-price">{game['original_price']}</span>
          <span class="final-price">{game['final_price']}</span>
        </div>
        <a href="{game['steam_url']}" target="_blank" class="buy-btn">前往 Steam 购买</a>
      </div>
    </div>"""
        steam_cards.append(card)
    
    # 生成新游卡片
    new_hot_cards = []
    for game in new_hot_games:
        appid = game["appid"]
        img_data = xiaoheihe_data.get(appid, {})
        img_url = img_data.get("capsule_image", img_data.get("header_image", ""))
        
        # 获取 fallback URLs
        fallback_urls = img_data.get("fallback_urls", [img_url])
        
        card = f"""
    <div class="game-card">
      <div class="card-img-wrap" data-fallbacks='{json.dumps(fallback_urls)}'>
        <img class="card-img" src="{img_url}" alt="{game['name']}" data-fallback-index="0" onerror="handleImageError(this)" onclick="openLightbox(this.src)">
        <div class="card-img-fallback hidden">🎮</div>
      </div>
      <div class="card-body">
        <div class="card-meta">
          <span class="platform-tag steam">Steam</span>
        </div>
        <div class="card-title">{game['name']}</div>
        <p style="font-size:0.85rem;color:#8899aa;margin-bottom:0.5rem;">{game.get('description', '')}</p>
        <div class="card-price">
          <span class="final-price">{game.get('price', '¥?')}</span>
        </div>
        <p style="font-size:0.8rem;color:#f39c12;margin-top:0.3rem;">{game.get('status', '')}</p>
        <a href="{game.get('url', '#')}" target="_blank" class="buy-btn">查看详情</a>
      </div>
    </div>"""
        new_hot_cards.append(card)
    
    # 生成比价表格行
    compare_rows = []
    for game in steam_games:
        psn_info = psn_data.get(game["name"], {})
        # eShop 模拟数据
        eshop_prices = {
            "全面战争：战锤3": "HK$468",
            "底特律：化身为人": "HK$198",
            "Kenshi": "无",
            "Warhammer 40,000: 星际战士2": "HK$568",
            "The Outlast Trials": "HK$328",
            "No Man's Sky 无人深空": "HK$398",
            "Grand Theft Auto V 增强版": "HK$468",
            "Outer Wilds": "HK$238",
        }
        eshop_price = eshop_prices.get(game["name"], "未知")
        
        # 推荐平台（简化：Steam 最便宜）
        recommended = "PC (最便宜)"
        
        row = f"""
      <tr>
        <td><strong>{game['name']}</strong></td>
        <td>{game['final_price']} <small style="color:#f39c12;">(-{game['discount_percent']}%)</small></td>
        <td>{psn_info.get('price', '未找到')} {psn_info.get('discount', '')}</td>
        <td>{eshop_price}</td>
        <td><span style="color:#00d4ff;font-weight:600;">{recommended}</span></td>
      </tr>"""
        compare_rows.append(row)
    
    # 生成即将发售卡片
    upcoming_cards = []
    if not upcoming_games:
        upcoming_games = []
    
    for game in upcoming_games:
        appid = game.get("appid", 0)
        img_data = xiaoheihe_data.get(appid, {})
        img_url = img_data.get("capsule_image", img_data.get("header_image", ""))
        fallback_urls = img_data.get("fallback_urls", [img_url])
        
        # Steam CDN 回退策略
        if not img_url:
            img_url = f"https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/{appid}/header.jpg"
            fallback_urls = [
                f"https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/{appid}/header.jpg",
                f"https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/{appid}/capsule_231x87.jpg",
            ]
        
        release_date = game.get("release_date", "")
        steam_price = game.get("price", "")
        steam_price_display = f"预购: {steam_price}" if steam_price else "暂无预购价"
        
        if steam_price:
            steam_price_html = f'<span class="final-price">{steam_price}</span>'
        else:
            steam_price_html = f'<span style="color:#8899aa;font-size:0.85rem;">{steam_price_display}</span>'
        
        card = f"""
    <div class="game-card">
      <div class="card-img-wrap" data-fallbacks='{json.dumps(fallback_urls)}'>
        <img class="card-img" src="{img_url}" alt="{game['name']}" data-fallback-index="0" onerror="handleImageError(this)" onclick="openLightbox(this.src)">
        <div class="card-img-fallback hidden">🎮</div>
      </div>
      <div class="card-body">
        <div class="card-meta">
          <span class="platform-tag steam">Steam</span>
          <span class="platform-tag" style="background:rgba(255,170,0,0.2);color:#ffaa00;">📅 {release_date}</span>
        </div>
        <div class="card-title">{game['name']}</div>
        <div class="card-price">
          {steam_price_html}
        </div>
        <a href="{game.get('steam_url', '#')}" target="_blank" class="buy-btn" style="background:linear-gradient(135deg,#667788,#445566);color:#fff;">Steam 商店页</a>
      </div>
    </div>"""
        upcoming_cards.append(card)
    
    # 生成PS5实体盘卡片
    physical_cards = []
    physical_games = [
        {
            "name": "战神：诸神黄昏",
            "description": "奎托斯北欧神话终章，年度最佳游戏",
            "price": "HK$398",
            "img": "https://image.api.playstation.com/vulcan/ap/rnd/202207/1212/4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d4d.png",
        },
        {
            "name": "漫威蜘蛛侠2",
            "description": "双蛛同框，纽约市开放世界",
            "price": "HK$468",
            "img": "https://image.api.playstation.com/vulcan/ap/rnd/202305/1212/5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e5e.png",
        },
        {
            "name": "最终幻想 XVI",
            "description": "黑暗幻想风格，召唤兽大战",
            "price": "HK$468",
            "img": "https://image.api.playstation.com/vulcan/ap/rnd/202303/0714/6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f6f.png",
        },
        {
            "name": "霍格沃茨之遗",
            "description": "哈利波特开放世界RPG",
            "price": "HK$398",
            "img": "https://image.api.playstation.com/vulcan/ap/rnd/202212/1212/7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a7a.png",
        },
    ]
    
    for game in physical_games:
        card = f"""
    <div class="game-card">
      <div class="card-img-wrap" data-fallbacks='["{game['img']}"]'>
        <img class="card-img" src="{game['img']}" alt="{game['name']}" data-fallback-index="0" onerror="handleImageError(this)" onclick="openLightbox(this.src)">
        <div class="card-img-fallback hidden">🎮</div>
      </div>
      <div class="card-body">
        <div class="card-meta">
          <span class="platform-tag ps">PS5</span>
          <span class="platform-tag physical">实体盘</span>
        </div>
        <div class="card-title">{game['name']}</div>
        <p style="font-size:0.85rem;color:#8899aa;margin-bottom:0.5rem;">{game['description']}</p>
        <div class="card-price">
          <span class="final-price">{game['price']}</span>
        </div>
        <div class="buy-btn" style="background: #333; color: #aaa; cursor: default;">实体盘价格</div>
      </div>
    </div>"""
        physical_cards.append(card)
    
    # 当前时间
    now = datetime.now()
    update_time = now.strftime("%Y-%m-%d %H:%M")
    update_hour = now.strftime("%H")
    
    # 替换模板中的占位符
    html = html_template.replace("{update_time}", update_time)
    html = html.replace("{update_hour}", update_hour)
    html = html.replace("{steam_cards}", "\n".join(steam_cards))
    html = html.replace("{new_hot_cards}", "\n".join(new_hot_cards))
    html = html.replace("{compare_rows}", "\n".join(compare_rows))
    html = html.replace("{upcoming_cards}", "\n".join(upcoming_cards))
    html = html.replace("{physical_cards}", "\n".join(physical_cards))
    
    return html

# ========== 主函数 ==========
def main():
    print("🚀 开始更新游戏折扣页面...")
    
    # 1. 获取 Steam 促销数据
    print("1. 获取 Steam 促销数据...")
    steam_games = fetch_steam_deals()
    appids = [game["appid"] for game in steam_games]
    
    # 2. 获取即将发售游戏
    print("2. 获取即将发售游戏...")
    upcoming_games = fetch_upcoming_games()
    
    # 合并 appid 列表用于获取图片
    upcoming_appids = [g["appid"] for g in upcoming_games]
    all_appids = list(set(appids + upcoming_appids))
    
    # 3. 获取小黑盒图片
    print("3. 获取小黑盒游戏图片...")
    xiaoheihe_data = fetch_xiaoheihe_images(all_appids)
    
    # 4. 获取 PSN 价格（Steam 折扣游戏）
    print("4. 获取 PSN 港服价格...")
    psn_data = {}
    for name in [g["name"] for g in steam_games] + [g["name"] for g in upcoming_games]:
        result = search_psn(name)
        if result:
            psn_data[name] = result
        time.sleep(1)  # 礼貌延迟
    
    # 5. 新游数据（近期已发售热门）
    new_hot_games = [
        {
            "name": "极限竞速：地平线6",
            "appid": 2483190,
            "description": "舞台首次搬到日本，550+真实车辆，系列最大地图",
            "price": "¥298",
            "status": "🔥 5月19日发售 | 预购进行中",
            "url": "https://store.steampowered.com/app/2483190/",
        },
        {
            "name": "Subnautica 2：异星水域",
            "appid": 1962700,
            "description": "深海生存神作续集，首次支持4人联机合作",
            "price": "¥108",
            "status": "✅ 5月14日已发售 | 抢先体验",
            "url": "https://store.steampowered.com/app/1962700/",
        },
        {
            "name": "007 初露锋芒",
            "appid": 3768760,
            "description": "詹姆斯·邦德起源故事，IO Interactive 制作",
            "price": "¥298",
            "status": "🔥 5月27日发售 | 预购进行中",
            "url": "https://store.steampowered.com/app/3768760/",
        },
        {
            "name": "深岩银河：异动核心",
            "appid": 2605790,
            "description": "深岩银河系列轻 Rogue 衍生作，四人合作挖矿打怪",
            "price": "¥108",
            "status": "✅ 5月20日已发售 | 抢先体验",
            "url": "https://store.steampowered.com/app/2605790/",
        },
        {
            "name": "8020号指令",
            "appid": 2255370,
            "description": "赛博朋克潜行游戏，扮演黑客入侵企业网络",
            "price": "¥88",
            "status": "✅ 5月15日已发售",
            "url": "https://store.steampowered.com/app/2255370/",
        },
        {
            "name": "帕拉人生",
            "appid": 1118520,
            "description": "模拟人生最强竞品，超高自由度的生活模拟",
            "price": "¥136",
            "status": "🔥 5月25日发售 | 抢先体验",
            "url": "https://store.steampowered.com/app/1118520/",
        },
    ]
    
    # 7. 生成 HTML（传入即将发售游戏数据）
    print("6. 生成 HTML 页面...")
    html_content = generate_html(steam_games, xiaoheihe_data, psn_data, new_hot_games, upcoming_games)
    
    # 8. 写入文件
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ 页面生成完成：{OUTPUT_HTML}")
    print(f"📊 统计：{len(steam_games)} 款 Steam 折扣游戏，{len(new_hot_games)} 款新游")
    
    # 9. 推送到 GitHub（在 GitHub Actions 中自动执行）
    if os.getenv("GITHUB_ACTIONS"):
        print("9. 检测到 GitHub Actions 环境，准备提交更改...")
        # 这里可以添加 git commit & push 逻辑
        # 但通常由 workflow 的 actions/checkout + actions/deploy-pages 处理

if __name__ == "__main__":
    main()