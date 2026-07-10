---
name: check-gefei-kd
version: 0.2.0
description: "输入任意形式的关键词列表（对话直述 / 列表 / 标准词表），批量调用哥飞 KD API，输出快照、Markdown 报告，并产出一份填好 gefeiKD 的标准词表。"
---

# check-gefei-kd

根据用户提供的关键词，批量调用哥飞 KD API：

- `GET https://seo.web.cafe/kd/api/v1/kd`

查询每个关键词的 KD（`score`）及相关字段（`level`、`keywordType`、`keywordVolume`、`linkBudget` 等），并**额外产出一份标准词表**（`standard-word-analysis` v1），把每个词的 `gefeiKD` 填进去。

## 输入：任意形式的关键词列表

用户给你关键词的形式不固定，按下表映射成 CLI 参数（在仓库根目录执行）：

| 用户给的形态 | 怎么传给脚本 |
|---|---|
| 对话里直接说出几个词（"查一下 image to text 和 ocr online"） | `--keyword "image to text" --keyword "ocr online"`（可重复），或 `--keywords-csv "image to text,ocr online"` |
| 一个关键词列表文件（每行一个词，支持 `#` 注释） | `--keyword-file /absolute/path/keywords.txt` |
| 逗号/分隔的字符串 | `--keywords-csv "a,b,c"` |
| 一份**标准词表**（`.json` 或 `.xlsx`，见 `standard-word-analysis`） | `--standard-word-table /absolute/path/table.json`（或 `.xlsx`） |

可以混用，也可以重复 `--standard-word-table` 传入多份词表，脚本会合并去重后统一查询。

### 标准词表输入的特别规则

当输入本身就是标准词表时：

- **只回填 `gefeiKD`，其余字段（`score`、`volume(sim)`、`group`、`对应域名`…）保持原值不动**，不会覆盖、不会清空。
- 脚本会从 `keyword` 列抽取关键词去查询；查不到的词 `gefeiKD` 留空。
- 读取依据 `standard-word-analysis/spec/standard-word-table.v1.json` 的列定义，XLSX 按表头反解为字段。

## 执行方式

```bash
# 方式一：对话直述 / 自由关键词
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run \
  --keyword "image to text" \
  --keyword "ocr online"

# 方式二：关键词文件
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run \
  --keyword-file /absolute/path/keywords.txt

# 方式三：CSV 关键词
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run \
  --keywords-csv "image to text,ocr online"

# 方式四：标准词表（.json 或 .xlsx）——仅回填 gefeiKD
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run \
  --standard-word-table /absolute/path/standard-word-table.v1.sample.json
```

可选命令：

```bash
# 参数检查（不发请求）
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run --keyword "image to text" --dry-run

# 基于快照重建历史报告 + 标准词表（不请求 API）
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py rebuild-reports

# 校验 latest.md 结构
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py validate-report
```

## 产物

每次 `run` 都会输出：

- 抓取归档：`check-gefei-kd/data/fetch-YYYYMMDD-HHMMSS.json`
- 快照归档：`check-gefei-kd/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史 Markdown：`check-gefei-kd/report/history/report-YYYYMMDD-HHMMSS.md`
- 最新 Markdown：`check-gefei-kd/report/latest.md`
- **标准词表 JSON**：`check-gefei-kd/report/history/keyword-table-YYYYMMDD-HHMMSS.json` + `check-gefei-kd/report/latest.json`
- **标准词表 XLSX**：`check-gefei-kd/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx` + `check-gefei-kd/report/latest.xlsx`

标准词表结构对齐 `standard-word-analysis` v1（`version` / `meta` / `rows`，列顺序与 `spec/standard-word-table.v1.json` 一致）：

- 自由关键词输入：每行只有 `keyword` 与 `gefeiKD` 有值，其余列为空。
- 标准词表输入：保留原行所有字段，仅覆盖 `gefeiKD`。

## 规则摘要

- API key 文件：`check-gefei-kd/api_key.txt`
- 鉴权优先级：`--api-key` > 环境变量 `GEFEI_KD_API_KEY` > `api_key.txt`
- 默认参数：`gl=us`、`hl=en`、`force=0`
- 默认每次请求最小间隔 `6.2s`（遵循 10 req/min 限制）
- 可重试错误：网络瞬态、`429 rate`、`5xx`
- 全局终止错误：`401 auth`、`429 quota`
- XLSX 导出依赖 `openpyxl`；缺失时可用 `--no-xlsx` 仅产出 JSON 标准词表
