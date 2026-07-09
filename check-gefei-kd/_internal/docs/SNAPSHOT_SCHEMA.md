# check-gefei-kd Snapshot Schema（MVP）

快照文件路径：

- `check-gefei-kd/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`

本文描述快照 JSON 的字段契约，供 `run` / `rebuild-reports` / `validate-report` 使用。

---

## 顶层结构

```json
{
  "meta": {},
  "rows": [],
  "failures": []
}
```

---

## meta

```json
{
  "generatedAt": "2026-07-09T18:00:00",
  "stamp": "20260709-180000",
  "target": {
    "keywords": ["image to text", "ocr online"],
    "keywordCount": 2
  },
  "request": {
    "apiBase": "https://seo.web.cafe",
    "endpoint": "/kd/api/v1/kd",
    "apiUrl": "https://seo.web.cafe/kd/api/v1/kd",
    "gl": "us",
    "hl": "en",
    "force": 0,
    "responseFormat": "json",
    "authMode": "header",
    "apiKeySource": "check-gefei-kd/api_key.txt",
    "minIntervalSeconds": 6.2,
    "maxRetries": 2,
    "timeoutSeconds": 60
  },
  "summary": {
    "inputCount": 2,
    "successCount": 2,
    "failureCount": 0,
    "avgScore": 45.5,
    "cachedHitRate": 0.5,
    "levelDistribution": {
      "容易": 1,
      "中等": 1
    },
    "keywordTypeDistribution": {
      "generic": 2
    }
  },
  "globalError": null,
  "output": {
    "reportHistoryPath": ".../report/history/report-20260709-180000.md",
    "latestReportPath": ".../report/latest.md"
  }
}
```

字段说明：

- `meta.generatedAt`: 生成时间（ISO8601）
- `meta.stamp`: 文件时间戳（`YYYYMMDD-HHMMSS`）
- `meta.target.keywords`: 本次输入关键词（去重后）
- `meta.target.keywordCount`: 去重后关键词数
- `meta.request.*`: 实际请求配置
- `meta.summary.*`: 本次统计摘要
- `meta.globalError`: 全局终止错误（如 auth/quota），无则 `null`
- `meta.output.*`: 报告路径

---

## rows

`rows` 表示成功关键词结果数组，每个元素结构：

```json
{
  "keyword": "image to text",
  "score": 58,
  "level": "中等",
  "keywordType": "generic",
  "genericScore": null,
  "keywordVolume": 1200,
  "keywordTrend": {
    "domain": 390,
    "ratio": 0.62
  },
  "linkBudget": {
    "targetDr": 43
  },
  "detailsCount": 10,
  "cached": true,
  "computedAt": 1730000000,
  "reasons": ["..."]
}
```

关键字段：

- `score`: KD 分值（0~100）
- `level`: 难度等级
- `keywordType`: 关键词类型（如 `generic` / `brand`）
- `keywordVolume`: 搜索量
- `keywordTrend`: 趋势对象（按上游返回透传）
- `linkBudget`: 外链预算对象（按上游返回透传）
- `detailsCount`: `details` 数组长度
- `cached`: 是否命中缓存
- `computedAt`: 计算时间（通常为 Unix 时间戳）
- `reasons`: 解释信息列表

---

## failures

`failures` 表示失败关键词数组，每个元素结构：

```json
{
  "keyword": "ocr online",
  "keywordNormalized": "ocr online",
  "attempts": 3,
  "error": "触发频率限制（rate）",
  "errorCode": "rate",
  "httpStatus": 429
}
```

字段说明：

- `keyword`: 原始关键词
- `keywordNormalized`: 归一化关键词
- `attempts`: 本关键词总尝试次数
- `error`: 最终错误文本
- `errorCode`: 错误码（如 `auth` / `quota` / `rate`）
- `httpStatus`: HTTP 状态码

---

## 兼容性说明

- `rebuild-reports` 仅依赖本 schema 的 `meta/rows/failures` 渲染报告。
- 如新增字段，需保持已有字段兼容，避免破坏历史快照重建。
