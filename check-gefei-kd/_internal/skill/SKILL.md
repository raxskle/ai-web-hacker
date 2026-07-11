---
name: check-gefei-kd
version: 0.2.0
description: "输入任意形式关键词（自由关键词 / 列表 / 标准词表），批量查询哥飞 KD，归档快照、报告，并产出填好 gefeiKD 的标准词表。"
---

# check-gefei-kd

用于执行一次关键词 KD 批量查询流程：

1. 读取关键词输入：
   - 自由关键词：`--keyword` / `--keyword-file` / `--keywords-csv`
   - 标准词表：`--standard-word-table <.json|.xlsx>`（按 `standard-word-analysis` v1 解析）
2. 抽取去重关键词，调用哥飞 KD API（复用仓库根目录 `shared_gefei_kd.fetch_gefei_kd_rows`，每个关键词一次 `GET /kd/api/v1/kd`）
3. 归档原始抓取结果到 `data/fetch-*.json`
4. 标准化写入快照到 `_internal/snapshots/snapshot-*.json`（含 `rows` / `failures` / `standardWordTable`）
5. 生成 Markdown 报告（history + latest）
6. 产出标准词表（JSON + XLSX），回填 `gefeiKD`

## 输入模式

- `free_keywords`：仅关键词；标准词表行只有 `keyword` 与 `gefeiKD` 有值。
- `standard_word_table`：读取标准词表行，**仅覆盖 `gefeiKD`，其余字段保持原值**。

两种输入可混用：同时给标准词表与自由关键词时，自由关键词会作为骨架行追加。

## 执行方式

在仓库根目录执行：

```bash
# 自由关键词
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run --keyword "image to text"

# 标准词表输入（仅回填 gefeiKD）
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run \
  --standard-word-table path/to/standard-word-table.v1.sample.json

# 参数检查（不发请求）
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run --keyword-file /tmp/keywords.txt --dry-run

# 基于快照重建历史报告 + 标准词表
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py rebuild-reports

# 校验报告结构（latest.md + latest.xlsx）
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py validate-report
```

## 输入/输出

- API key 文件：`check-gefei-kd/api_key.txt`
- 抓取归档：`check-gefei-kd/data/fetch-YYYYMMDD-HHMMSS.json`
- 标准化快照：`check-gefei-kd/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史报告：`check-gefei-kd/report/history/report-YYYYMMDD-HHMMSS.md`
- 最新报告：`check-gefei-kd/report/latest.md`
- 标准词表 JSON：`check-gefei-kd/report/history/keyword-table-YYYYMMDD-HHMMSS.json` + `check-gefei-kd/report/latest.json`
- 标准词表 XLSX：`check-gefei-kd/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx` + `check-gefei-kd/report/latest.xlsx`
- `keywords` sheet 列顺序：`keyword -> 对应域名 -> score -> volume(sim) -> kd(sim) -> cpc(sim) -> volume(sem) -> kd(sem) -> cpc(sem) -> gefeiKD -> group -> sourcePresence(SIM/SEM)`
- Excel 数值列（`score/sim*/sem*/gefeiKD`）按数字类型写入，`keywords` 数据区配色：SIM 列浅蓝、SEM 列浅紫

## 固定参数默认值

- `apiBase=https://seo.web.cafe`
- `endpoint=/kd/api/v1/kd`
- `gl=us`、`hl=en`、`force=0`、`response-format=json`、`auth-mode=header`
- `min-interval-seconds=6.2`、`max-retries=2`、`timeout-seconds=60`
- 标准词表版本：`v1`，规范文件 `standard-word-analysis/spec/standard-word-table.v1.json`

## 失败策略

- API key 缺失：整次失败，不落产物
- 单关键词失败：记录失败明细，继续执行后续关键词；其 `gefeiKD` 留空
- 全局终止条件（`401 auth` / `429 quota`）：`shared_gefei_kd` 抛 `RuntimeError` 终止
- `rebuild-reports` 仅依赖快照，不请求 API；旧快照若无 `standardWordTable`，仅重建 Markdown 报告
- XLSX 导出依赖 `openpyxl`；缺失时可用 `--no-xlsx` 仅产出 JSON
