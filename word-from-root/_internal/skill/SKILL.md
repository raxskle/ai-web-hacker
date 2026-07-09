---
name: word-from-root
version: 0.1.0
description: "基于词根抓取 SIM/SEM 相关关键词，输出快照、Markdown 摘要和 Excel 明细。"
---

# word-from-root（MVP）

用于执行一次按词根扩词的完整流程：

1. 调用 SIM Suggest 第 1 页，读取 `totalRecords`
2. 继续抓取剩余页，最多累计 300 词
3. 调用 SEM Summary 获取 `total`
4. 分页调用 SEM Keywords，最多累计 300 词
5. 标准化两路结果并按关键词合并
6. 计算 `score = semVolume * semCpc / semKd`
7. 写入原始归档、标准化快照、Markdown 报告、Excel 文件

## 执行方式

```bash
python3 word-from-root/_internal/scripts/word_from_root.py run --keyword "image to text"
python3 word-from-root/_internal/scripts/word_from_root.py rebuild-reports
python3 word-from-root/_internal/scripts/word_from_root.py validate-report
```

## 输入/输出

- 本地服务文档：`word-from-root/local-service/API_REFERENCE.md`
- token 文件：`word-from-root/local-service/bridge_token.txt`
- gmitm 文件：`word-from-root/local-service/__gmitm.txt`
- 抓取归档：`word-from-root/data/fetch-YYYYMMDD-HHMMSS.json`
- 标准化快照：`word-from-root/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史报告：`word-from-root/report/history/report-YYYYMMDD-HHMMSS.md`
- 历史 Excel：`word-from-root/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx`
- 最新报告：`word-from-root/report/latest.md`
- 最新 Excel：`word-from-root/report/latest.xlsx`

## 固定规则（MVP）

- SIM 默认：`latest=28d`、`country=999`、`sort=windowVolume`、`rowsPerPage=100`
- SIM 过滤：`rangeFilter=cpc,0.1,|difficulty,1,80`
- SEM 默认：`database=us`、`currency=USD`、`page.size=100`
- SEM 过滤：`cpc > 0.1`、`difficulty < 90`
- 排序值只使用 SEM 指标：`semVolume * semCpc / semKd`
- 若缺失完整 SEM 指标，则 `score` 为空并排在已评分结果之后

## 失败策略

- token / gmitm 缺失：整次失败，不落任何新产物
- 任一 API 请求失败：整次失败，不落任何新产物
- `rebuild-reports` 仅依赖 snapshot，不重新请求 API
