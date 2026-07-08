---
name: word-monitor-sitemap
version: 0.3.1
description: "监控 onlinegames/playhop sitemap，发现新增内页并从 URL 路由提炼关键词候选，仅输出单一合并报告。"
---

# word-monitor-sitemap

用于按站点监控 sitemap，自动生成：

1. 站点可见 URL 快照
2. 与上一份快照相比的新增内页/新增路由模式
3. 基于新增 URL 的关键词候选
4. 单一合并报告（`latest.md`）

## 执行方式

在仓库根目录执行：

```bash
# 运行固定双站（onlinegames_io + playhop_com）
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run

# 重建报告（仅合并报告）
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py rebuild-reports

# 校验报告结构（默认 latest.md）
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py validate-report
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py validate-report --report word-monitor-sitemap/report/latest.md
```

## 输入输出

- 站点配置：`word-monitor-sitemap/data/sites.json`
- 抓取归档：`word-monitor-sitemap/data/<site-id>/fetch-YYYYMMDD-HHMMSS.json`
- 快照归档：`word-monitor-sitemap/_internal/snapshots/<site-id>/snapshot-YYYYMMDD-HHMMSS.json`
- 历史合并报告：`word-monitor-sitemap/report/history/report-YYYYMMDD-HHMMSS.md`
- 最新合并报告：`word-monitor-sitemap/report/latest.md`

## 规则摘要（MVP）

- 支持 `urlset` 与 `sitemapindex`（含递归，受深度/数量上限保护）
- 仅保留站点配置内 `includeHosts` 的 URL
- 通过 `excludePathRegexes` 过滤工具页/聚合页
- 首次运行仅建立基线，不输出新增与关键词结论
- 关键词候选仅来自新增 URL slug 分词（token / bigram / phrase）
