# AI 出海工具

本仓库包含 AI 出海工具、Skill、工作流等

## monitor-new-sub-domain

基于 similarWeb 的子域名监控工具，搭配 hacker-extension 插件使用。

工作原理：通过 hacker-extension 插件获取 SimilarWeb 前几页的请求数据，拿到目标域名最新的点击量上涨的子域名列表，每天跑一次，对比前一天的数据，自动发现新出现在前面的子域名，以及点击量上涨的子域名。

报告分析得出有机会的子域名列表后，可以后续 AI 深入分析，或者再将这些子域名列表，回到 SimilarWeb 查看关键词、目标网站等。
