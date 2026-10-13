# wechat-video-download

下载微信视频号(WeChat Channels)视频 — 处理 weixin.qq.com/sph/ 分享链接,通过页面 API 获取元数据、从微信客户端缓存提取视频文件。关键结论:预览页不返回视频流,可靠路径=客户端播放后提取缓存。捕获脚本见 scripts/sph_capture.py。

> 完整说明见 [SKILL.md](./SKILL.md)
