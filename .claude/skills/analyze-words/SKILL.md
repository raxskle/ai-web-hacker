---
name: analyze-words
version: 0.1.0
description: "输入关键词列表，调用 SEM keywords.GetInfo 批量获取总流量、综合 CPC、KD 等聚合指标并输出报告。"
---

# analyze-words

根据你提供的关键词列表，批量调用本地服务接口：

- `POST /sem/kwogw/v2/webapi/keywords.GetInfo`

并对每个关键词聚合输出：

- `globalVolume`（总流量）
- `globalCpcAvg`（综合 CPC）
- `globalDifficultyAvg`（综合 KD）

## 执行方式

```bash
# 方式一：直接传关键词（可重复 --keyword）
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --keyword "image to text" \
  --keyword "ocr online"

# 方式二：传关键词文件（每行一个词，支持 # 注释）
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --keyword-file /absolute/path/keywords.txt
```

可选命令：

```bash
# 基于快照重建 Markdown 报告
python3 analyze-words/_internal/scripts/analyze_words.py rebuild-reports

# 校验 latest.md 结构
python3 analyze-words/_internal/scripts/analyze_words.py validate-report
```

## 输入输出

- 本地服务文档：`analyze-words/local-service/API_REFERENCE.md`
- token 文件：`analyze-words/local-service/bridge_token.txt`
- gmitm 文件：`analyze-words/local-service/__gmitm.txt`
- 抓取归档：`analyze-words/data/fetch-YYYYMMDD-HHMMSS.json`
- 快照归档：`analyze-words/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史 Markdown：`analyze-words/report/history/report-YYYYMMDD-HHMMSS.md`
- 最新 Markdown：`analyze-words/report/latest.md`

## 规则摘要（MVP）

- 请求参数默认遵循 API 文档 Keyword Info 示例：
  - `device=0`、`currency=USD`、`database=us`、`locati0n=0`、`date=""`
- 每个关键词仅替换 `params.phrase`
- 聚合口径：
  - `globalVolume = sum(volume)`
  - `globalCpcAvg = avg(cpc, 忽略 null)`
  - `globalDifficultyAvg = avg(difficulty, 忽略 null)`
- 任一关键词最终失败：整次失败，不写入新产物
