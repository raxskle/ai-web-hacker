---
name: word-monitor-sitemap
version: 0.3.3
description: "抓取多站 sitemap（含 onlinegames/playhop/suikagame/crazygames/coolmathgames/poki），按站点归档快照并输出新增内页与关键词候选；在种子词表后串行调用 analyze-words/check-gefei-kd 补齐指标，输出最终合并报告与标准词表。"
---

# word-monitor-sitemap（MVP）

用于每天执行一次 sitemap 监控流程：

1. 按配置抓取站点 sitemap（默认跑 enabled=true）
2. 标准化 URL 并过滤非目标路径
3. 保存抓取归档与标准化快照
4. 与最近一次历史快照对比
5. 输出种子标准词表
6. 串行调用 `analyze-words` 与 `check-gefei-kd` 补齐指标
7. 输出 Markdown 合并报告（`latest.md`）与最终词表（`latest.xlsx`）
8. 同步最终词表到 `words/sitemap-YYYYMMDD-HHMMSS.xlsx`

## 执行方式

在仓库根目录执行：

```bash
# 默认运行 sites.json 中 enabled=true 的站点
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run

# 只运行一个站点
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run --site poki_com

# 运行配置中的全部站点（包含 enabled=false）
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run --all-sites

# 重建历史报告（合并报告 + 最终词表）
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py rebuild-reports

# 校验最新报告/词表（默认 latest.md + latest.xlsx）
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py validate-report
# 或显式指定
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py validate-report --report word-monitor-sitemap/report/latest.md --xlsx word-monitor-sitemap/report/latest.xlsx
```

可选参数：

- `--words-dir`：最终词表同步目录（默认 `words/`）
- `--chain-work-dir`：链式阶段工作目录（默认 `word-monitor-sitemap/_internal/chained/`）

## 输入/输出

- 站点配置：`word-monitor-sitemap/data/sites.json`
- 抓取归档：`word-monitor-sitemap/data/<site-id>/fetch-YYYYMMDD-HHMMSS.json`
- 标准化快照：`word-monitor-sitemap/_internal/snapshots/<site-id>/snapshot-YYYYMMDD-HHMMSS.json`
- 链式阶段产物：`word-monitor-sitemap/_internal/chained/<stamp>/...`
- 历史合并报告：`word-monitor-sitemap/report/history/report-YYYYMMDD-HHMMSS.md`
- 最新合并报告：`word-monitor-sitemap/report/latest.md`
- 历史最终词表：`word-monitor-sitemap/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx`
- 最新最终词表：`word-monitor-sitemap/report/latest.xlsx`
- 同步词表副本：`words/sitemap-YYYYMMDD-HHMMSS.xlsx`
