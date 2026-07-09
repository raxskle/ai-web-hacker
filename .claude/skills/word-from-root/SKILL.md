---
name: word-from-root
version: 0.1.0
description: "输入一个词根，调用 SIM Suggest 与 SEM Keyword Magic，合并关键词并导出 Excel。"
---

# word-from-root

根据你提供的词根，抓取两路关键词数据：

1. SIM：`/sim/api/KeywordGenerator/google/suggest`
2. SEM：`ideas.GetKeywordsSummary` + `ideas.GetKeywords`

然后把两路结果合并为一张 Excel 表，并生成 Markdown 摘要报告。

## 执行方式

```bash
python3 word-from-root/_internal/scripts/word_from_root.py run --keyword "image to text"
```

可选命令：

```bash
# 基于快照重建 Markdown / Excel
python3 word-from-root/_internal/scripts/word_from_root.py rebuild-reports

# 校验 latest.md 与 latest.xlsx
python3 word-from-root/_internal/scripts/word_from_root.py validate-report
```

## 输入输出

- 本地服务文档：`word-from-root/local-service/API_REFERENCE.md`
- token 文件：`word-from-root/local-service/bridge_token.txt`
- gmitm 文件：`word-from-root/local-service/__gmitm.txt`
- 抓取归档：`word-from-root/data/fetch-YYYYMMDD-HHMMSS.json`
- 快照归档：`word-from-root/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史 Markdown：`word-from-root/report/history/report-YYYYMMDD-HHMMSS.md`
- 历史 Excel：`word-from-root/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx`
- 最新 Markdown：`word-from-root/report/latest.md`
- 最新 Excel：`word-from-root/report/latest.xlsx`

## 规则摘要（MVP）

- SIM 固定过滤：`cpc,0.1,|difficulty,1,80`
- SEM 固定过滤：`cpc > 0.1`、`difficulty < 90`
- 两路各自最多抓 300 个词
- 合并后按 `semVolume * semCpc / semKd` 降序排序
- Excel 是完整结果，Markdown 仅做预览
