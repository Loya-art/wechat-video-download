# -*- coding: utf-8 -*-
"""微信视频号预览页网络响应捕获(Playwright + 系统 Chrome,免下载浏览器)
用法:
    python sph_capture.py <sph_id 或完整链接>
    # 例: python sph_capture.py AAGgj2C3As
输出: 打印捕获到的 get_feed_info 等 API 响应,并存到 resp_*.json
说明: 预览页 API 只返回元数据(描述/封面/统计),不含视频流 URL。
      视频流需微信客户端播放后从缓存提取(见 SKILL.md 流程)。
"""
import re
import sys
from playwright.sync_api import sync_playwright

arg = sys.argv[1] if len(sys.argv) > 1 else "AAGgj2C3As"
if arg.startswith("http"):
    m = re.search(r"id=([A-Za-z0-9]+)", arg)
    sph_id = m.group(1) if m else arg.rstrip("/").split("/")[-1]
else:
    sph_id = arg
URL = f"https://channels.weixin.qq.com/finder-preview/pages/sph?id={sph_id}"

captured = {}


def on_response(resp):
    if any(k in resp.url for k in ("get_feed_info", "feed_info", "finder")):
        try:
            captured[resp.url] = resp.text()[:20000]
        except Exception:
            pass


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"))
    page.on("response", on_response)
    page.goto(URL, wait_until="networkidle", timeout=45000)
    page.wait_for_timeout(4000)
    browser.close()

print(f"捕获 {len(captured)} 个相关响应")
for url, body in captured.items():
    fn = "resp_" + re.sub(r"[^a-zA-Z0-9]", "_", url.split("?")[0].split("/")[-1]) + ".json"
    with open(fn, "w", encoding="utf-8") as f:
        f.write(body)
    print("->", fn, f"{len(body)}B")
