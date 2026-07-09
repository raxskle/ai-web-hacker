# check-gefei-kd

输入一批关键词，调用哥飞 KD API，输出关键词 KD 及相关字段，并生成可复盘的快照与 Markdown 报告。

## 功能概览

每次 `run` 会执行：

1. 读取关键词输入（支持 `--keyword` / `--keyword-file` / `--keywords-csv`）
2. 清洗与去重关键词（lower + trim + 压缩空格）
3. 调用 `GET https://seo.web.cafe/kd/api/v1/kd`
4. 归档抓取原始结果到 `data/fetch-*.json`
5. 标准化写入快照到 `_internal/snapshots/snapshot-*.json`
6. 生成报告到 `report/history/report-*.md` 与 `report/latest.md`

## 目录说明

- `api_key.txt`：API Key 文件（默认读取）
- `data/`：抓取归档（`fetch-YYYYMMDD-HHMMSS.json`）
- `_internal/snapshots/`：标准化快照（`snapshot-YYYYMMDD-HHMMSS.json`）
- `report/history/`：历史 Markdown 报告
- `report/latest.md`：最新报告
- `_internal/scripts/check_gefei_kd.py`：主脚本
- `_internal/skill/SKILL.md`：技能内部说明
- `_internal/docs/SNAPSHOT_SCHEMA.md`：快照字段说明

## 运行前准备

1. 在 `check-gefei-kd/api_key.txt` 填写有效 API Key（例如 `wc_mcp_xxx`）
2. 可选：设置环境变量 `GEFEI_KD_API_KEY` 覆盖文件 key

## 使用方式

在仓库根目录执行：

```bash
# 方式一：直接传关键词
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run \
  --keyword "image to text" \
  --keyword "ocr online"

# 方式二：关键词文件（每行一个词）
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run \
  --keyword-file /absolute/path/keywords.txt

# 方式三：CSV 关键词
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run \
  --keywords-csv "image to text,ocr online"
```

可选命令：

```bash
# 参数检查，不发请求
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run --keyword "image to text" --dry-run

# 基于快照重建报告
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py rebuild-reports

# 校验报告结构
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py validate-report
```

## 常用参数

- `--gl`：国家代码（默认 `us`）
- `--hl`：语言代码（默认 `en`）
- `--force`：是否强制重算（`0/1`，默认 `0`）
- `--auth-mode`：`header`（默认）或 `query`
- `--api-key`：直接传 key（优先级最高）
- `--api-key-file`：key 文件路径（默认 `check-gefei-kd/api_key.txt`）
- `--min-interval-seconds`：最小请求间隔（默认 `6.2`）
- `--max-retries`：可重试错误重试次数（默认 `2`）

## 报告字段

报告中会输出：

- `score`
- `level`
- `keywordType`
- `genericScore`
- `keywordVolume`
- `keywordTrend`（domain/ratio）
- `linkBudget`（targetDr）
- `cached`
- `computedAt`
- `reasons`（摘要）

## 错误策略

- 可重试：网络错误、`429 rate`、`5xx`
- 不重试：`400`
- 全局终止：`401 auth`、`429 quota`
- 失败关键词会在报告“失败明细”中完整展示
