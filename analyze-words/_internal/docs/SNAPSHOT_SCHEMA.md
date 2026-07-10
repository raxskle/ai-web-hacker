# Snapshot Schema（MVP）

文件：`_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`

```json
{
  "meta": {
    "generatedAt": "2026-07-09T15:10:22",
    "stamp": "20260709-151022",
    "target": {
      "keywords": ["image to text", "ocr online"],
      "keywordCount": 2
    },
    "request": {
      "apiBase": "http://127.0.0.1:17311",
      "endpoint": "/sem/kwogw/v2/webapi/keywords.GetInfo",
      "simEndpoint": "/sim/api/KeywordGenerator/google/suggest",
      "simRowsPerPage": 5,
      "simType": "Related",
      "simSort": "score",
      "simAsc": false,
      "simCountry": "999",
      "simLatest": "28d",
      "simWebSource": "Total",
      "simIsWindow": true,
      "simPage": 1,
      "device": 0,      "currency": "USD",
      "database": "us",
      "locati0n": 0,
      "date": "",
      "timeoutMs": 45000,
      "waitTimeoutMs": 120000,
      "maxRetries": 2
    },
    "summary": {
      "inputCount": 2,
      "successCount": 2,
      "failureCount": 0,
      "simMatchedCount": 1,
      "simNoMatchCount": 1,
      "simFailureCount": 0,
      "totalGlobalVolume": 10340,
      "avgGlobalCpc": 1.1942,
      "avgGlobalDifficulty": 63.211
    },
    "output": {
      "reportHistoryPath": ".../report/history/report-20260709-151022.md"
    }
  },
  "rows": [
    {
      "keyword": "image to text",
      "keywordNormalized": "image to text",
      "globalVolume": 7100,
      "globalCpcAvg": 1.4234,
      "globalDifficultyAvg": 67.12,
      "databaseCount": 42,
      "cpcSampleCount": 18,
      "difficultySampleCount": 20,
      "rowsCount": 80,
      "simWindowVolume": 78380,
      "simCpc": 0.2,
      "simKd": 50,
      "simStatus": "matched"
    }
  ],
  "failures": []
}
```

## 字段说明

### `rows[]`（标准化关键词结果）

每项包含：
- `keyword`
- `keywordNormalized`
- `globalVolume`
- `globalCpcAvg`
- `globalDifficultyAvg`
- `databaseCount`
- `cpcSampleCount`
- `difficultySampleCount`
- `rowsCount`
- `simWindowVolume` / `simCpc` / `simKd`（SIM 命中时有值）
- `simStatus`（`matched` / `no_match` / `request_error`）

### `failures[]`

记录 SEM 失败关键词：
- `keyword`
- `keywordNormalized`
- `attempts`
- `error`

说明：
- SEM 保持硬失败策略（任一关键词最终失败，整次失败不落产物）；
- SIM 失败或未命中不进入 `failures[]`，仅体现在 `summary` 统计与 `rows[].simStatus`。

### `meta.summary`（新增 SIM 统计）

- `simMatchedCount`：SIM top5 内匹配到对应关键词的数量
- `simNoMatchCount`：SIM 请求成功但 top5 未匹配到对应关键词的数量
- `simFailureCount`：SIM 请求失败数量

### `meta.request`（新增 SIM 配置）

- `simEndpoint`
- `simRowsPerPage`（固定 `5`）
- `simType`（固定 `Related`）
- `simSort`（固定 `score`）
- `simAsc`（固定 `false`）
- `simCountry`（固定 `999`）
- `simLatest`（固定 `28d`）
- `simWebSource`（固定 `Total`）
- `simIsWindow`（固定 `true`）
- `simPage`（固定 `1`）

### 归档补充说明（`data/fetch-*.json`）

每个关键词请求记录包含并列的 `sem` 与 `sim` 结果，便于排查 SIM 列为何为空。SIM 结果可能为：
- `status=matched`
- `status=no_match`
- `status=request_error`
- `status=skipped_due_to_sem_failure`

其中 `skipped_due_to_sem_failure` 仅在该关键词 SEM 失败时出现。
