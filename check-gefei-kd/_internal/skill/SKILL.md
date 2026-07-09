---
name: check-gefei-kd
version: 0.1.0
description: "输入关键词批量查询哥飞 KD，归档快照并输出 Markdown 报告。"
---

# check-gefei-kd（MVP）

用于执行一次关键词 KD 批量查询流程：

1. 读取关键词输入（`--keyword` / `--keyword-file` / `--keywords-csv`）
2. 调用哥飞 KD API（每个关键词一次 `GET /kd/api/v1/kd`）
3. 归档原始抓取结果
4. 标准化输出行并生成快照
5. 生成 Markdown 报告（history + latest）

## 执行方式

在仓库根目录执行：

```bash
# 完整执行
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run --keyword "image to text"

# 参数检查（不发请求）
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run --keyword-file /tmp/keywords.txt --dry-run

# 基于快照重建历史报告
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py rebuild-reports

# 校验报告结构
python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py validate-report
```

## 输入/输出

- API key 文件：`check-gefei-kd/api_key.txt`
- 抓取归档：`check-gefei-kd/data/fetch-YYYYMMDD-HHMMSS.json`
- 标准化快照：`check-gefei-kd/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史报告：`check-gefei-kd/report/history/report-YYYYMMDD-HHMMSS.md`
- 最新报告：`check-gefei-kd/report/latest.md`

## 固定参数默认值

- `apiBase=https://seo.web.cafe`
- `endpoint=/kd/api/v1/kd`
- `gl=us`
- `hl=en`
- `force=0`
- `response-format=json`
- `auth-mode=header`
- `min-interval-seconds=6.2`
- `max-retries=2`

## 失败策略

- API key 缺失：整次失败，不落产物
- 单关键词失败：记录失败明细，继续执行后续关键词
- 全局终止条件（`401 auth` / `429 quota`）：立即终止后续请求，写入当前结果产物
- `rebuild-reports` 仅依赖快照，不请求 API
