# Snapshot Schema（MVP）

文件：`_internal/snapshots/<site-id>/snapshot-YYYYMMDD-HHMMSS.json`

```json
{
  "meta": {
    "generatedAt": "2026-07-08T21:00:01",
    "stamp": "20260708-210001",
    "baselineMode": true,
    "site": {
      "id": "onlinegames_io",
      "displayName": "onlinegames",
      "sitemapUrls": ["https://www.onlinegames.io/sitemap.xml"],
      "includeHosts": ["www.onlinegames.io", "onlinegames.io"]
    },
    "crawl": {
      "sitemapsFetched": 1,
      "sitemapUrlsDiscovered": 0,
      "ignoredByDepthLimit": 0,
      "rawPageUrlCount": 297,
      "dedupedPageUrlCount": 297
    },
    "normalize": {
      "rawUrls": 297,
      "invalidUrls": 0,
      "nonTargetHostUrls": 0,
      "excludedByPathRules": 4,
      "dedupedUrls": 293
    },
    "effectiveUrlCount": 293,
    "patternCount": 3,
    "baselineStamp": null
  },
  "urls": [
    {
      "url": "https://www.onlinegames.io/basketball-stars",
      "host": "www.onlinegames.io",
      "path": "/basketball-stars",
      "segments": ["basketball-stars"],
      "slug": "basketball-stars",
      "depth": 1
    }
  ],
  "patterns": [
    {
      "pattern": "/{token}-{token}/",
      "count": 120,
      "exampleUrls": ["https://www.onlinegames.io/basketball-stars"]
    }
  ],
  "comparison": {
    "baselineStamp": "20260707-210001",
    "newlyAddedUrls": [],
    "removedUrls": [],
    "newPatterns": []
  },
  "keywords": {
    "topKeywordsFromNewUrls": [
      {
        "type": "token",
        "keyword": "basketball",
        "count": 3,
        "urlCount": 3,
        "score": 3.3,
        "exampleUrls": ["https://www.onlinegames.io/basketball-stars"]
      }
    ],
    "counters": {
      "phrase": [["basketball stars", 2]],
      "bigram": [["basketball stars", 2]],
      "token": [["basketball", 3]]
    }
  }
}
```

## 字段说明

- `urls[]`：标准化后的有效内页 URL。
- `patterns[]`：从 path 推断出的路由模式统计。
- `comparison.newlyAddedUrls`：今日有、基线无。
- `comparison.newPatterns`：今日有、基线无的 pattern。
- `keywords.topKeywordsFromNewUrls`：仅从新增 URL 提取的关键词候选。

首次运行（`baselineMode=true`）时，`comparison` 与 `keywords.topKeywordsFromNewUrls` 为空。