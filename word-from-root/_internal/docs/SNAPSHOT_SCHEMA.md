# Snapshot Schema（MVP）

文件：`_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`

```json
{
  "meta": {
    "generatedAt": "2026-07-09T13:30:01",
    "stamp": "20260709-133001",
    "target": {
      "keyword": "image to text",
      "country": "999",
      "latest": "28d",
      "database": "us",
      "currency": "USD"
    },
    "request": {
      "simRowsPerPage": 100,
      "simMaxKeywords": 300,
      "semPageSize": 100,
      "semMaxKeywords": 300,
      "simRangeFilter": "cpc,0.1,|difficulty,1,80",
      "simSort": "windowVolume",
      "semScoreFormula": "semVolume * semCpc / semKd"
    },
    "api": {
      "baseUrl": "http://127.0.0.1:17311",
      "sim": {
        "totalRecords": 216,
        "effectiveTotal": 216,
        "pagesFetched": 3
      },
      "sem": {
        "totalRecords": 549,
        "effectiveTotal": 300,
        "pagesFetched": 3
      }
    },
    "output": {
      "reportHistoryPath": ".../report/history/report-20260709-133001.md",
      "excelHistoryPath": ".../report/history/keyword-table-20260709-133001.xlsx"
    },
    "summary": {
      "simCount": 216,
      "semCount": 300,
      "mergedCount": 410,
      "bothCount": 88,
      "simOnlyCount": 128,
      "semOnlyCount": 194,
      "scoredCount": 282
    }
  },
  "sim": {
    "rows": [
      {
        "keyword": "image text editor",
        "keywordNormalized": "image text editor",
        "simKeyword": "image text editor",
        "simWindowVolume": 56740,
        "simAverageVolume": 64524,
        "simCpc": 0.22,
        "simKd": 53,
        "simRank": 2,
        "simPage": 1,
        "simRankInPage": 2
      }
    ],
    "raw": {}
  },
  "sem": {
    "rows": [
      {
        "keyword": "image to text converter",
        "keywordNormalized": "image to text converter",
        "semKeyword": "image to text converter",
        "semVolume": 18100,
        "semCpc": 1.88,
        "semKd": 68,
        "semCompetitionLevel": 0.11,
        "semResults": 122,
        "semSnapshotDate": "20260620",
        "semTrend": [67, 44, 36],
        "semRank": 2,
        "semPage": 1,
        "semRankInPage": 2
      }
    ],
    "raw": {}
  },
  "mergedRows": [
    {
      "keyword": "image to text converter",
      "keywordNormalized": "image to text converter",
      "sourcePresence": "both",
      "score": 500.35,
      "simWindowVolume": 12000,
      "simAverageVolume": 14000,
      "simCpc": 0.4,
      "simKd": 50,
      "semVolume": 18100,
      "semCpc": 1.88,
      "semKd": 68,
      "semCompetitionLevel": 0.11,
      "semResults": 122,
      "semSnapshotDate": "20260620"
    }
  ]
}
```

## 字段说明

`mergedRows[]` 必须至少包含：
- `keyword`
- `keywordNormalized`
- `sourcePresence`（`both` / `sim_only` / `sem_only`）
- `score`
- `simWindowVolume`
- `simAverageVolume`
- `simCpc`
- `simKd`
- `semVolume`
- `semCpc`
- `semKd`
- `semCompetitionLevel`
- `semResults`
- `semSnapshotDate`

排序规则：
- 优先按 `score` 降序
- `score` 为空的行排在已评分行之后
- 再按 `semVolume` 降序、`keyword` 升序

`rebuild-reports` 必须仅依赖 snapshot 重建 Markdown 与 Excel，不重新请求 API。
