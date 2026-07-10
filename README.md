# AI 出海工具

本仓库包含 AI 出海工具、Skill、工作流等

## word-monitor-sub-domain

监控 vercel.app 新增的和点击量上涨的子域名，并从而得到关键词

## word-monitor-sitemap

监控游戏站的sitemap，发现新游戏

## word-from-root

根据词根，获取相关关键词

## analyze-word

验证关键词是否可做，检查kd

## check-gefei-kd

调用哥飞KD api

## 组合使用

vercel.app和sitemap只能得到词，而且是偏新词，所以要搭配analyze-words和check-gefei-kd，然后再人工看

word-from-root拿到的词带数据，搭配check-gefei-kd，然后人工看

标准词表，所有skill的输入和输出都是符合这个规范的，最终人工审查这一份完整的表

最终的结果词表已经使用了所有可以分析的工具，只需要挑看着顺眼的词，拿去Google Trends以及实际搜索查看结果 

只剩下把这几个skill组合起来，然后就只需要调三个找词skill了
