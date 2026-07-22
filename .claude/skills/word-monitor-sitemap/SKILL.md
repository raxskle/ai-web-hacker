---
name: word-monitor-sitemap
version: 0.3.3
description: "监控多站 sitemap（含 onlinegames/playhop/suikagame/crazygames/coolmathgames/poki/dragganaitool/higgsfield），发现新增内页并从 URL 路由提炼关键词候选；在种子词表后串行调用 analyze-words 与 check-gefei-kd 补齐指标，输出最终合并报告与标准词表 Excel。"
---

# word-monitor-sitemap

用于按站点监控 sitemap，自动生成：

1. 站点可见 URL 快照
2. 与上一份快照相比的新增内页/新增路由模式
3. 基于新增 URL 的关键词候选（种子词表）
4. 串行调用 `analyze-words`（SIM/SEM）与 `check-gefei-kd`（gefeiKD）补齐最终词表
5. 单一合并报告（`latest.md`）
6. 最终标准词表 Excel（`latest.xlsx`）
7. 同步副本到 `words/sitemap-YYYYMMDD-HHMMSS.xlsx`

## 执行方式

在仓库根目录执行：

```bash
# 运行 sites.json 中 enabled=true 的站点
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run

# 仅运行单站
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run --site poki_com

# 运行全部站点（包含 enabled=false）
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run --all-sites

# 重建报告（合并报告 + 最终标准词表 Excel）
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py rebuild-reports

# 校验报告结构（默认 latest.md + latest.xlsx）
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py validate-report
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py validate-report --report word-monitor-sitemap/report/latest.md
```

可选参数：

- `--words-dir`：最终词表同步目录（默认 `words/`）
- `--chain-work-dir`：链式阶段工作目录（默认 `word-monitor-sitemap/_internal/chained/`）

## 输入输出

- 站点配置：`word-monitor-sitemap/data/sites.json`
- 抓取归档：`word-monitor-sitemap/data/<site-id>/fetch-YYYYMMDD-HHMMSS.json`
- 快照归档：`word-monitor-sitemap/_internal/snapshots/<site-id>/snapshot-YYYYMMDD-HHMMSS.json`
- 链式阶段产物：`word-monitor-sitemap/_internal/chained/<stamp>/...`
- 历史合并报告：`word-monitor-sitemap/report/history/report-YYYYMMDD-HHMMSS.md`
- 最新合并报告：`word-monitor-sitemap/report/latest.md`
- 历史最终词表 Excel：`word-monitor-sitemap/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx`
- 最新最终词表 Excel：`word-monitor-sitemap/report/latest.xlsx`
- 词表同步副本：`words/sitemap-YYYYMMDD-HHMMSS.xlsx`
- 自动清理：每次 `run` 成功后，自动删除最老一次执行（同一 `stamp`）的历史数据/快照/报告/链路产物；`report/latest.md` 与 `report/latest.xlsx` 不删除

## 规则摘要（MVP）

- 支持 `urlset` 与 `sitemapindex`（嵌套会持续递归跟随；保留 sitemap 总数上限保护）
- 仅保留站点配置内 `includeHosts` 的 URL
- 通过 `excludePathRegexes` 过滤工具页/聚合页
- 首次运行仅建立基线，不输出新增与关键词结论
- 关键词候选来自新增 URL slug 的清洗 phrase（保留完整 slug 词序，不再拆分单词/bigram；相同 keyword 去重后保留一行）
- 合并词表会在 sitemap 阶段先产出“种子表”，再通过 analyze/check 链路补齐 SIM/SEM/gefeiKD，最终回写到 report 与 words 目录
- 最终 `keywords` sheet 列顺序：`keyword -> 对应域名 -> score -> volume(sim) -> kd(sim) -> cpc(sim) -> volume(sem) -> kd(sem) -> cpc(sem) -> gefeiKD -> group -> sourcePresence(SIM/SEM)`
- Excel 数值列按数字类型写入，`keywords` 数据区配色：SIM 列浅蓝、SEM 列浅紫
