---
name: wechat-video-download
description: 下载微信视频号(WeChat Channels)视频 — 处理 weixin.qq.com/sph/ 分享链接,通过页面 API 获取元数据、从微信客户端缓存提取视频文件。关键结论:预览页不返回视频流,可靠路径=客户端播放后提取缓存。捕获脚本见 scripts/sph_capture.py。
---

# 微信视频号视频下载

## 触发条件
用户发 `https://weixin.qq.com/sph/<id>` 链接要求"保存/下载这个视频"。

## 结论先行(重要,别浪费时间)
视频号网页预览页 **永远不返回视频流 URL**(设计如此,必须微信客户端播放)。不要花大量时间逆向视频地址 —— 直接走客户端缓存提取路径。

## 标准流程
1. **解析链接**:`weixin.qq.com/sph/<id>` 302 → `channels.weixin.qq.com/finder-preview/pages/sph?id=<id>`(Vue SPA;HTML 里无 video 元素,显示"可扫码前往微信观看此内容")
2. **拿元数据(可选,确认内容)**:POST `https://channels.weixin.qq.com/finder-preview/api/feed/get_feed_info`
   body: `{"baseReq":{"generalToken":""},"shortUri":"<id>"}`
   → 返回 feedInfo(description / coverUrl / 赞评转统计)+ sceneInfo.dynamicExportId
   再用 `{"baseReq":...,"exportId":"<dynamicExportId>"}` 调一次 → 返回"此内容暂时无法播放"(证实拿不到视频流)
   在浏览器 console 里 fetch 同源相对路径 `/finder-preview/api/feed/get_feed_info` 即可(带 cookie)
3. **客户端缓存提取(可靠路径)**:
   a. 让用户在电脑微信打开链接播放几秒(播放即缓存)
   b. 微信数据目录:默认 `Documents\xwechat_files\<wxid>\`,但用户可能自定义(本机实测:`E:\个人文件\xwechat_files\<wxid>\`)
   c. 视频缓存:`msg\video\<YYYY-MM>\<hash>.mp4`(聊天视频也在这);找最新的 mp4,与封面/时长比对确认
   d. 复制到用户目标目录(本机习惯 E:\<user>\ 下)

## 网络分析技巧(可复用到其他 SPA 逆向)
- `performance.getEntriesByType('resource')` 列出页面发起的所有请求,找 API 端点
- 页面内 hook:`window.fetch` 包装后 `resp.clone().text()` 存 `window.__captured`,再触发页面操作/重载读捕获
- Playwright 监听:`page.on("response", ...)`(headless 可能被微信风控,拿不到数据时改用带 cookie 的真实浏览器上下文)
- **Playwright 用系统 Chrome 免下载浏览器**:`p.chromium.launch(channel="chrome")`(用户网络受限时尤其重要)

## Pitfalls
- `finder.video.qq.com/.../stodownload` 那个 URL 是**封面图**(Content-Type: image/jpg),不是视频
- 微信缓存文件名是哈希,须按时间戳+文件大小+封面比对确认是目标视频,别拿错
- 旧缓存 `cache/<YYYY-MM>/Sns/Video/` 是朋友圈视频,别混淆
- 电脑微信版本过旧可能打不开视频号;备选:手机微信播放 → 文件传输助手转发 → 聊天缓存(msg/video)提取

## 脚本
- scripts/sph_capture.py — Playwright 监听预览页网络响应,一键导出 get_feed_info 等 API 响应到 resp_*.json
