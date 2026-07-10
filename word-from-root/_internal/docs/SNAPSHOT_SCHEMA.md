# Snapshot Schema（MVP）

文件：`_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`

```json
{
  "meta": {
    "generatedAt": "2026-07-10T10:00:00",
    "stamp": "20260710-100000",
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
      "simRangeFilter": "cpc,0.1,|difficulty,1,70",
      "simSort": "windowVolume",
      "scoreFormula": "simWindowVolume * simCpc / simKd",
      "standardWordTableVersion": "v1",
      "grouping": {
        "enabled": true,
        "promptVersion": "v1",
        "model": "default",
        "temperature": 0,
        "timeoutSeconds": 120,
        "cacheDir": ".../_internal/grouping-cache"
      }
    },
    "grouping": {
      "sim": {
        "source": "sim",
        "promptVersion": "v1",
        "model": "default",
        "temperature": 0,
        "cacheHit": false,
        "groupCount": 180,
        "inputCount": 216
      },
      "sem": {
        "source": "sem",
        "promptVersion": "v1",
        "model": "default",
        "temperature": 0,
        "cacheHit": false,
        "groupCount": 210,
        "inputCount": 300
      }
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
      "reportHistoryPath": ".../report/history/report-20260710-100000.md",
      "excelHistoryPath": ".../report/history/keyword-table-20260710-100000.xlsx"
    },
    "summary": {
      "simRawCount": 216,
      "semRawCount": 300,
      "simCount": 180,
      "semCount": 210,
      "simGroupedCount": 180,
      "semGroupedCount": 210,
      "mergedCount": 320,
      "bothCount": 70,
      "simOnlyCount": 110,
      "semOnlyCount": 140,
      "scoredCount": 180
    }
  },
  "sim": {
    "rawRows": [],
    "rows": [
      {
        "keyword": "image to text",
        "keywordNormalized": "image to text",
        "mergeKey": "image to text",
        "groupMembers": ["image to text", "image-to-text"],
        "group": "image to text | image-to-text",
        "groupReason": "词序/连接符变体",
        "groupConfidence": 0.93,
        "groupSize": 2,
        "simWindowVolume": 12000,
        "simAverageVolume": 14000,
        "simCpc": 0.4,
        "simKd": 50
      }
    ],
    "raw": {}
  },
  "sem": {
    "rawRows": [],
    "rows": [
      {
        "keyword": "image to text converter",
        "keywordNormalized": "image to text converter",
        "mergeKey": "image to text converter",
        "groupMembers": ["image to text converter", "images to text converter"],
        "group": "image to text converter | images to text converter",
        "groupReason": "单复数变体",
        "groupConfidence": 0.89,
        "groupSize": 2,
        "semVolume": 18100,
        "semCpc": 1.88,
        "semKd": 68
      }
    ],
    "raw": {}
  },
  "mergedRows": [
    {
      "keyword": "image to text converter",
      "keywordNormalized": "image to text converter",
      "mergeKey": "image to text converter",
      "groupMembers": [
        "image to text converter",
        "images to text converter",
        "image-to-text converter"
      ],
      "group": "image to text converter | images to text converter | image-to-text converter",
      "sourcePresence": "both",
      "score": 500.35,
      "simWindowVolume": 12000,
      "simAverageVolume": 14000,
      "simCpc": 0.4,
      "simKd": 50,
      "semVolume": 18100,
      "semCpc": 1.88,
      "semKd": 68
    }
  ]
}
```

## 字段说明

### 标准词表版本信息

- `meta.request.standardWordTableVersion`：当前固定为 `v1`
- 对应规范文件：`standard-word-analysis/spec/standard-word-table.v1.json`

### `mergedRows[]`（用于 Excel `keywords` sheet）

`mergedRows[]` 必须至少包含：

- `keyword`
- `group`
- `sourcePresence`（`both` / `sim_only` / `sem_only`）
- `score`
- `simWindowVolume`
- `simKd`
- `simCpc`
- `semVolume`
- `semKd`
- `semCpc`

> 以上字段会映射到标准词表 v1 的 10 列。

### source 内分组结果

`sim.rows[]` / `sem.rows[]` 为 **source 内近义合并后行**，必须包含：

- `mergeKey`
- `groupMembers`
- `group`
- `groupReason`
- `groupConfidence`
- `groupSize`
- 各自 source 的聚合指标（volume / cpc / kd 等）

`sim.rawRows[]` / `sem.rawRows[]` 为分组前标准化结果，用于审计追溯。

## 排序与 score 规则

- 公式：`simWindowVolume * simCpc / simKd`
- `score` 为空的行排在已评分行之后
- 其后按 `simWindowVolume` 降序、`keyword` 升序

## 兼容性约束

- `rebuild-reports` 必须仅依赖 snapshot 重建 Markdown 与 Excel，不重新请求 API，不重新执行 AI 分组
- v1 阶段不改标准词表列名和顺序
- 本版不包含 `gefeiKD`
