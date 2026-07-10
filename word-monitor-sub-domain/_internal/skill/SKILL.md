---
name: word-monitor-sub-domain
version: 0.1.0
description: "抓取 vercel.app 在 Similarweb Landing Pages 前8页样本，归档快照并输出新增/上涨统一监控报告与标准词表 Excel。"
---

# word-monitor-sub-domain（MVP）

用于每天执行一次监控流程：

1. 通过本地服务抓取 `/sim/api/websiteOrganicLandingPagesV2` 的 page=1..8
2. 标准化并去重页面样本
3. 保存抓取归档与标准化快照
4. 对比最近一次历史快照
5. 输出 Markdown 报告（单表合并展示页面与子域名结果）
6. 输出标准词表 Excel（仅新增页面/子域名的 top keywords）
7. 查询哥飞 KD，补齐 `gefeiKD`

## 执行方式

在仓库根目录执行：

```bash
# 执行一次完整监控
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py run

# 基于快照重建历史 Markdown / Excel
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py rebuild-reports

# 校验 Markdown / Excel
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py validate-report
```

## 输入/输出

- 本地服务文档：`word-monitor-sub-domain/local-service/API_REFERENCE.md`
- token 文件：`word-monitor-sub-domain/local-service/bridge_token.txt`
- 抓取归档：`word-monitor-sub-domain/data/fetch-YYYYMMDD-HHMMSS.json`
- 标准化快照：`word-monitor-sub-domain/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史报告：`word-monitor-sub-domain/report/history/report-YYYYMMDD-HHMMSS.md`
- 历史 Excel：`word-monitor-sub-domain/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx`
- 最新报告：`word-monitor-sub-domain/report/latest.md`
- 最新 Excel：`word-monitor-sub-domain/report/latest.xlsx`

## 固定抓取参数（默认）

- key=vercel.app
- country=999
- latest=28d
- webSource=Total
- sourceType=organic
- sort=ClicksShare
- asc=false
- includeSubDomains=true
- isWindow=true
- searchType=domain
- page=1..8

## 对比逻辑（MVP）

- 基线：最近一次历史快照（同 key/country/latest/sourceType/startPage/endPage）
- 首次运行：仅建立基线，不输出新增/上涨结论

页面级：
- newlyObservedPage：今天有、基线无、clicks >= 100
- 页面上涨：今天和基线都有，且
  - today.clicks >= 100
  - deltaClicks >= 30
  - growthRate > 5%

子域名级：
- observedSubdomainClicks = 样本内该子域名页面 clicks 求和
- newlyObservedSubdomain：今天有、基线无、observedSubdomainClicks >= 150
- 子域名上涨：今天和基线都有，且
  - today.observedSubdomainClicks >= 150
  - deltaClicks >= 50
  - growthRate > 5%

## 产物说明

- Markdown 报告合并展示页面与子域名结果
- 标准词表 Excel 仅导出新增页面/子域名对应的 top keywords
- 相同 `keyword` 按词去重，仅保留一行
- `对应域名` 聚合同词命中的全部域名 / 页面上下文
- `gefeiKD` 使用哥飞 KD API 返回的 `score`
- 其余标准词表指标列可为空
