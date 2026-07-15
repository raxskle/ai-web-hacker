# word-monitor-sitemap

用于监控网站 sitemap，发现新上的内页，并从新增 URL 路由提炼可做关键词。

当前默认监控（`enabled=true`）站点：
- `onlinegames_io`（https://www.onlinegames.io/）
- `playhop_com`（https://playhop.com/）
- `suikagame_io`（https://suikagame.io/）
- `crazygames_com`（https://www.crazygames.com/）
- `coolmathgames_com`（https://www.coolmathgames.com/）
- `poki_com`（https://poki.com/）
- `dragganaitool_com`（https://dragganaitool.com/）
- `higgsfield_ai`（https://higgsfield.ai/）

已预置但默认关闭：
- `gamejolt_com`（https://gamejolt.com/）
  - 当前未找到稳定可用的公开 XML sitemap 入口，暂不启用。

## 功能概览

每次运行会执行：

1. 抓取站点的 sitemap（支持 sitemapindex 递归）
2. 标准化 URL 并按站点规则过滤
3. 生成路由模式统计
4. 与最近一次同站点快照对比，识别新增内页/新增模式
5. 从新增 URL 提取关键词候选并生成种子标准词表
6. 串行调用 `analyze-words`（补齐 SIM/SEM）与 `check-gefei-kd`（补齐 gefeiKD）
7. 输出最终合并报告（Markdown）与最终标准词表（Excel），并同步一份到 `words/sitemap-YYYYMMDD-HHMMSS.xlsx`

## 目录说明

- `data/sites.json`：站点配置
- `data/<site-id>/`：抓取归档（`fetch-YYYYMMDD-HHMMSS.json`）
- `_internal/snapshots/<site-id>/`：标准化快照（`snapshot-YYYYMMDD-HHMMSS.json`）
- `_internal/chained/<stamp>/`：链式阶段产物（`analyze-words` / `check-gefei-kd`）
- `report/history/report-YYYYMMDD-HHMMSS.md`：历史合并报告
- `report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx`：历史标准词表（最终口径）
- `report/latest.md`：最新合并报告
- `report/latest.xlsx`：最新标准词表（最终口径）
- `../words/sitemap-YYYYMMDD-HHMMSS.xlsx`：同步出的最终标准词表副本

## 使用方式

在仓库根目录执行：

```bash
# 运行 sites.json 中 enabled=true 的站点
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run

# 仅运行单站
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run --site poki_com

# 运行 sites.json 中全部站点（包括 enabled=false）
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run --all-sites

# 重建报告（Markdown + Excel）
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py rebuild-reports

# 校验最新 Markdown + Excel
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py validate-report

# 或显式指定
python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py validate-report \
  --report word-monitor-sitemap/report/latest.md \
  --xlsx word-monitor-sitemap/report/latest.xlsx
```

### 额外参数

- `--words-dir`：最终标准词表同步目录（默认仓库根目录 `words/`）
- `--chain-work-dir`：链式阶段临时工作目录（默认 `word-monitor-sitemap/_internal/chained/`）

## 当前规则（MVP）

- 每个站点由配置驱动（sitemap、host 白名单、path 过滤、关键词规则）
- 路由模式由 path segment 结构推断（例如 `/{token}/`, `/{token}-{token}/`）
- 新增关键词只基于新增 URL，避免把历史存量页重复作为“新机会”
- 首次运行不输出新增结论，仅建立对比基线
- `sitemapindex` 遇到嵌套会持续递归跟随，保留 sitemap 总数上限保护
- 关键词候选只保留**清洗后的完整 slug phrase**，不再拆分单词或 bigram
  - 例如：`nightfall-survivors-imo -> nightfall survivors imo`
  - 例如：`travel-merge -> travel merge`
  - 停用词（如 `the`）不再被过滤，尽量保留原始 slug 词序
- 标准词表遵循 `standard-word-analysis/spec/standard-word-table.v1.json`
  - sitemap 阶段先生成种子表（`keyword` + `对应域名`）
  - 之后由 `analyze-words` / `check-gefei-kd` 补齐 SIM/SEM/gefeiKD 等字段
  - 相同 keyword 会去重后保留一行
  - `对应域名` 聚合命中该关键词的完整 URL
  - 文本列导出采用自动换行（wrap）+ 顶对齐，避免长内容遮挡相邻列
  - `group` / `对应域名` 在展示层按多值分行（单元格内换行）以提升可读性
- 最终 `keywords` sheet 列顺序：`keyword -> 对应域名 -> score -> volume(sim) -> kd(sim) -> cpc(sim) -> volume(sem) -> kd(sem) -> cpc(sem) -> gefeiKD -> group -> sourcePresence(SIM/SEM)`
- Excel 数值列按数字类型写入，`keywords` 数据区配色：SIM 列浅蓝、SEM 列浅紫
### Markdown 报告

`report/latest.md` 会输出：
- 站点汇总
- 新增内页
- 新增路由模式
- 新关键词候选（phrase-only）
- 最终标准词表摘要（含 SIM/SEM/gefeiKD 回填统计与预览）

### 标准词表 Excel

`report/latest.xlsx` 与 `report/history/keyword-table-*.xlsx`：
- 表头严格对齐标准词表 v1
- 先生成 sitemap 种子词表，再串行经 `analyze-words` + `check-gefei-kd` 补齐指标
- 最终版本会回写到 `report/latest.xlsx` / `report/history/keyword-table-*.xlsx`
- 并同步一份到 `words/sitemap-YYYYMMDD-HHMMSS.xlsx`

## 依赖

- 生成 / 校验 Excel 需要 `openpyxl`
- 若本地缺失，可安装：

```bash
pip3 install openpyxl
```

