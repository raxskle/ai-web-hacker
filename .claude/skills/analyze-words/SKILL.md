---
name: analyze-words
version: 0.2.0
description: "输入任意形态关键词（文本/txt/标准词表），调用 SEM keywords.GetInfo 批量补全并输出标准词表结果。"
---

# analyze-words

根据你提供的关键词输入，批量调用本地服务接口：

- `POST /sem/kwogw/v2/webapi/keywords.GetInfo`

并输出：

- 关键词级 SEM 聚合指标（`globalVolume` / `globalCpcAvg` / `globalDifficultyAvg`）
- 标准词表（v1）结果文档（Excel + JSON）

## 执行方式

```bash
# 方式一：直接传关键词（可重复 --keyword；支持逗号/分号/中文标点分隔）
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --keyword "image to text, ocr online" \
  --keyword "pdf to text"

# 方式二：传关键词文件（每行一个关键词，支持 # 注释）
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --keyword-file /absolute/path/keywords.txt

# 方式三：CSV 关键词列表（可重复）
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --keywords-csv "image to text,ocr online,pdf to text"

# 方式四：标准词表输入（json / xlsx）
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --input-table standard-word-analysis/sample/standard-word-table.v1.sample.json

python3 analyze-words/_internal/scripts/analyze_words.py run \
  --input-table standard-word-analysis/sample/standard-word-table.v1.sample.xlsx

# 方式五：混合输入（标准词表 + 新增词）
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --input-table /absolute/path/existing-standard-table.xlsx \
  --keywords-csv "new keyword 1,new keyword 2"
```

可选命令：

```bash
# 基于快照重建 Markdown + 标准词表产物
python3 analyze-words/_internal/scripts/analyze_words.py rebuild-reports

# 校验 latest.md + latest.xlsx + latest.json
python3 analyze-words/_internal/scripts/analyze_words.py validate-report
```

## 输入输出

- 本地服务文档：`analyze-words/local-service/API_REFERENCE.md`
- token 文件：`analyze-words/local-service/bridge_token.txt`
- gmitm 文件：`analyze-words/local-service/__gmitm.txt`
- 抓取归档：`analyze-words/data/fetch-YYYYMMDD-HHMMSS.json`
- 快照归档：`analyze-words/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史 Markdown：`analyze-words/report/history/report-YYYYMMDD-HHMMSS.md`
- 历史标准词表 Excel：`analyze-words/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx`
- 历史标准词表 JSON：`analyze-words/report/history/keyword-table-YYYYMMDD-HHMMSS.json`
- 最新 Markdown：`analyze-words/report/latest.md`
- 最新标准词表 Excel：`analyze-words/report/latest.xlsx`
- 最新标准词表 JSON：`analyze-words/report/latest.json`

## 规则摘要（MVP）

- 请求参数默认遵循 API 文档 Keyword Info 示例：
  - `device=0`、`currency=USD`、`database=us`、`locati0n=0`、`date=""`
- 每个关键词仅替换 `params.phrase`
- 聚合口径：
  - `globalVolume = sum(volume)`
  - `globalCpcAvg = avg(cpc, 忽略 null)`
  - `globalDifficultyAvg = avg(difficulty, 忽略 null)`
- 标准词表补全口径：
  - 只补 SEM 字段：`volume(sem)` / `kd(sem)` / `cpc(sem)`
  - `score(simWindowVolume*cpc/kd)` 仅由 SIM 字段计算
  - 当缺失完整 SIM 指标（任一缺失或 <= 0）时，`score` 允许为空
  - `sourcePresence(SIM/SEM)` 根据 SIM/SEM 是否存在自动重算
- 任一关键词抓取失败：整次失败，不写入新产物
