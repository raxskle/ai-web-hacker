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
      "device": 0,
      "currency": "USD",
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
      "rowsCount": 80
    }
  ],
  "failures": []
}
```

## 字段说明

### `rows[]`（标准化关键词结果）

每项必须包含：
- `keyword`
- `keywordNormalized`
- `globalVolume`
- `globalCpcAvg`
- `globalDifficultyAvg`
- `databaseCount`
- `cpcSampleCount`
- `difficultySampleCount`
- `rowsCount`

### `failures[]`

当关键词抓取失败时记录：
- `keyword`
- `keywordNormalized`
- `attempts`
- `error`

MVP 默认策略为“任一失败即整次失败不落产物”，因此正常成功运行时 `failures` 应为空数组。
