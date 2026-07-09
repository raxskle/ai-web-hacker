---
name: check-gefei-kd
version: 0.1.0
description: "输入一批关键词，调用哥飞 KD API，输出快照与 Markdown 报告。"
---

# check-gefei-kd

根据你提供的关键词列表，批量调用哥飞 KD API：

- `GET https://seo.web.cafe/kd/api/v1/kd`

并输出每个关键词的 KD 与相关字段（如 level、keywordType、keywordVolume、linkBudget 等）。

## 执行方式

```bash
# 方式一：直接传关键词（可重复 --keyword）
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run \
  --keyword "image to text" \
  --keyword "ocr online"

# 方式二：传关键词文件（每行一个词，支持 # 注释）
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run \
  --keyword-file /absolute/path/keywords.txt

# 方式三：CSV 关键词列表
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run \
  --keywords-csv "image to text,ocr online"
```

可选命令：

```bash
# 基于快照重建 Markdown 报告
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py rebuild-reports

# 校验 latest.md 结构
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py validate-report
```

## 输入输出

- API key 文件：`check-gefei-kd/api_key.txt`
- 抓取归档：`check-gefei-kd/data/fetch-YYYYMMDD-HHMMSS.json`
- 快照归档：`check-gefei-kd/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史 Markdown：`check-gefei-kd/report/history/report-YYYYMMDD-HHMMSS.md`
- 最新 Markdown：`check-gefei-kd/report/latest.md`

## 规则摘要（MVP）

- 默认参数：`gl=us`、`hl=en`、`force=0`
- 鉴权优先级：`--api-key` > 环境变量 `GEFEI_KD_API_KEY` > `api_key.txt`
- 默认每次请求最小间隔 `6.2s`（遵循 10 req/min 限制）
- 可重试错误：网络瞬态、`429 rate`、`5xx`
- 全局终止错误：`401 auth`、`429 quota`
