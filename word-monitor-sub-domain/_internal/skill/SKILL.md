---
name: word-monitor-sub-domain
version: 0.1.0
description: "抓取 vercel.app 在 Similarweb Landing Pages 前5页样本，归档快照并输出新增/上涨页面与子域名报告。"
---

# word-monitor-sub-domain（MVP）

用于每天执行一次监控流程：

1. 通过本地服务抓取 `/sim/api/websiteOrganicLandingPagesV2` 的 page=1..5
2. 标准化并去重页面样本
3. 保存抓取归档与标准化快照
4. 对比最近一次历史快照
5. 输出 Markdown 报告（页面级 + 子域名级）

## 执行方式

在仓库根目录执行：

```bash
# 执行一次完整监控
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py run

# 基于快照重建历史报告
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py rebuild-reports

# 校验报告结构
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py validate-report
```

## 输入/输出

- 本地服务文档：`word-monitor-sub-domain/local-service/API_REFERENCE.md`
- token 文件：`word-monitor-sub-domain/local-service/bridge_token.txt`
- 抓取归档：`word-monitor-sub-domain/data/fetch-YYYYMMDD-HHMMSS.json`
- 标准化快照：`word-monitor-sub-domain/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史报告：`word-monitor-sub-domain/report/history/report-YYYYMMDD-HHMMSS.md`
- 最新报告：`word-monitor-sub-domain/report/latest.md`

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
- page=1..5

## 对比逻辑（MVP）

- 基线：最近一次历史快照（同 key/country/latest/sourceType）
- 首次运行：仅建立基线，不输出新增/上涨结论

页面级：
- newlyObservedPage：今天有、基线无、clicks >= 100
- risingPage：今天和基线都有，且
  - today.clicks >= 100
  - deltaClicks >= 30
  - growthRate >= 20%

子域名级：
- observedSubdomainClicks = 样本内该子域名页面 clicks 求和
- newlyObservedSubdomain：今天有、基线无、observedSubdomainClicks >= 150
- risingSubdomain：今天和基线都有，且
  - today.observedSubdomainClicks >= 150
  - deltaClicks >= 50（不限制增长率）

## 失败策略（已确认）

- 每页最多重试2次
- 任一页最终失败：整次分析失败，不落快照、不出报告
