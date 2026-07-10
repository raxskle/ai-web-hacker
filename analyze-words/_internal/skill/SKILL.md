---
name: analyze-words
version: 0.2.0
description: "批量关键词指标分析：支持文本/txt/标准词表输入，调用 keywords.GetInfo，输出快照、Markdown 与标准词表结果。"
---

# analyze-words（MVP）

用于执行一次关键词批量分析流程：

1. 读取关键词输入（`--keyword` / `--keyword-file` / `--keywords-csv` / `--input-table`）
2. 调用本地服务 `keywords.GetInfo`（每个关键词一请求）
3. 对 `result.keywords[]` 做客户端聚合
4. 生成抓取归档 + 快照 + Markdown + 标准词表（Excel/JSON）

## 执行方式

```bash
python3 analyze-words/_internal/scripts/analyze_words.py run --keyword "image to text"
python3 analyze-words/_internal/scripts/analyze_words.py run --keyword-file /tmp/keywords.txt
python3 analyze-words/_internal/scripts/analyze_words.py run --keywords-csv "image to text,ocr online"
python3 analyze-words/_internal/scripts/analyze_words.py run --input-table standard-word-analysis/sample/standard-word-table.v1.sample.xlsx
python3 analyze-words/_internal/scripts/analyze_words.py rebuild-reports
python3 analyze-words/_internal/scripts/analyze_words.py validate-report
```

## 输入 / 输出

- 本地服务文档：`analyze-words/local-service/API_REFERENCE.md`
- token 文件：`analyze-words/local-service/bridge_token.txt`
- gmitm 文件：`analyze-words/local-service/__gmitm.txt`
- 抓取归档：`analyze-words/data/fetch-YYYYMMDD-HHMMSS.json`
- 标准化快照：`analyze-words/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史报告：`analyze-words/report/history/report-YYYYMMDD-HHMMSS.md`
- 历史标准词表 Excel：`analyze-words/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx`
- 历史标准词表 JSON：`analyze-words/report/history/keyword-table-YYYYMMDD-HHMMSS.json`
- 最新报告：`analyze-words/report/latest.md`
- 最新标准词表 Excel：`analyze-words/report/latest.xlsx`
- 最新标准词表 JSON：`analyze-words/report/latest.json`

## 固定参数默认值

- `apiBase=http://127.0.0.1:17311`
- `endpoint=/sem/kwogw/v2/webapi/keywords.GetInfo`
- `device=0`
- `currency=USD`
- `database=us`
- `locati0n=0`
- `date=""`
- `timeoutMs=45000`
- `waitTimeoutMs=120000`

## 聚合规则（按关键词）

- `globalVolume = sum(volume)`
- `globalCpcAvg = avg(cpc, 忽略 null)`
- `globalDifficultyAvg = avg(difficulty, 忽略 null)`

## 标准词表规则（v1）

- 规范：`standard-word-analysis/spec/standard-word-table.v1.json`
- 当前流程只补 SEM 字段（`semVolume/semKd/semCpc`）
- `score` 只依赖 SIM 字段：`simWindowVolume * simCpc / simKd`
- `sourcePresence` 根据 SIM/SEM 是否存在自动重算（`both/sim_only/sem_only`）

## 失败策略

- token / gmitm 缺失：整次失败，不落产物
- 任一关键词请求失败：
  - 单关键词最多重试 2 次（退避 0.8s/1.6s）
  - 仍失败则整次失败，不落产物
- `rebuild-reports` 仅依赖快照，不请求 API
