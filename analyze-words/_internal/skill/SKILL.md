---
name: analyze-words
version: 0.1.0
description: "批量关键词指标分析：调用 keywords.GetInfo，输出快照与 Markdown 报告。"
---

# analyze-words（MVP）

用于执行一次关键词批量分析流程：

1. 读取关键词输入（`--keyword` / `--keyword-file`）
2. 调用本地服务 `keywords.GetInfo`（每个关键词一请求）
3. 对 `result.keywords[]` 做客户端聚合
4. 写入抓取归档 + 标准化快照 + Markdown 报告

## 执行方式

```bash
python3 analyze-words/_internal/scripts/analyze_words.py run --keyword "image to text"
python3 analyze-words/_internal/scripts/analyze_words.py run --keyword-file /tmp/keywords.txt
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
- 最新报告：`analyze-words/report/latest.md`

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

## 失败策略

- token / gmitm 缺失：整次失败，不落产物
- 任一关键词请求失败：
  - 单关键词最多重试 2 次（退避 0.8s/1.6s）
  - 仍失败则整次失败，不落产物
- `rebuild-reports` 仅依赖快照，不请求 API
