---
name: word-monitor-sitemap
version: 0.3.1
description: "抓取 onlinegames/playhop sitemap，按站点归档快照并输出新增内页、关键词候选，仅生成单一合并报告。"
---

# word-monitor-sitemap（MVP）

用于每天执行一次 sitemap 监控流程：

1. 抓取固定双站 sitemap（onlinegames_io + playhop_com）
2. 标准化 URL 并过滤非目标路径
3. 保存抓取归档与标准化快照
4. 与最近一次历史快照对比
5. 输出 Markdown 合并报告（单一 latest.md）

## 执行方式

在仓库根目录执行：

```bash
# 固定双站运行
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run

# 重建历史报告（仅合并报告）
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py rebuild-reports

# 校验最新报告（默认 latest.md）
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py validate-report
# 或显式指定
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py validate-report --report word-monitor-sitemap/report/latest.md
```

## 输入/输出

- 站点配置：`word-monitor-sitemap/data/sites.json`
- 抓取归档：`word-monitor-sitemap/data/<site-id>/fetch-YYYYMMDD-HHMMSS.json`
- 标准化快照：`word-monitor-sitemap/_internal/snapshots/<site-id>/snapshot-YYYYMMDD-HHMMSS.json`
- 历史合并报告：`word-monitor-sitemap/report/history/report-YYYYMMDD-HHMMSS.md`
- 最新合并报告：`word-monitor-sitemap/report/latest.md`

## 对比逻辑（MVP）

- 基线：最近一次历史快照（同 siteId）
- 首次运行：`baselineMode=true`，只建基线
- 非首次运行输出：
  - `newlyAddedUrls`
  - `removedUrls`
  - `newPatterns`
  - `keywords.topKeywordsFromNewUrls`

## 失败策略

- sitemap 抓取失败会自动重试
- 单站抓取/解析失败：该次运行失败，不落该站点新快照
