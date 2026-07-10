# Snapshot Schema（MVP）

文件：`_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`

```json
{
  "meta": {
    "generatedAt": "2026-07-08T21:00:01",
    "stamp": "20260708-210001",
    "baselineMode": true,
    "target": {
      "key": "vercel.app",
      "country": "999",
      "latest": "28d",
      "webSource": "Total",
      "sourceType": "organic"
    },
    "request": {
      "sort": "ClicksShare",
      "asc": false,
      "includeSubDomains": true,
      "isWindow": true,
      "searchType": "domain",
      "startPage": 1,
      "endPage": 8
    },
    "api": {
      "apiUrl": "http://127.0.0.1:17311/sim/api/websiteOrganicLandingPagesV2",
      "pagesRequested": [1, 2, 3, 4, 5, 6, 7, 8],
      "basePayload": {}
    },
    "pagesFetched": 8,
    "startPage": 1,
    "endPage": 8,
    "rawRows": 800,
    "dedupedRows": 420,
    "subdomainCount": 220,
    "invalidUrlRows": 0,
    "nonTargetRows": 80
  },
  "rows": [
    {
      "landingPageUrl": "https://foo.vercel.app/path",
      "hostname": "foo.vercel.app",
      "subdomain": "foo",
      "clicks": 123,
      "clicksShare": 0.001,
      "clicksChangeApi": 22,
      "topKeyword": "foo keyword",
      "page": 1,
      "rankInPage": 3
    }
  ],
  "subdomains": [
    {
      "subdomain": "foo",
      "observedSubdomainClicks": 260,
      "landingPagesCount": 2
    }
  ],
  "comparison": {
    "baselineStamp": "20260707-210001",
    "reportRows": [
      {
        "entityType": "subdomain",
        "trend": "上涨",
        "trendLabel": "上涨（+18.2%）",
        "subdomain": "foo",
        "path": "-",
        "clicks": 260,
        "topKeywords": "foo keyword / bar keyword"
      },
      {
        "entityType": "page",
        "trend": "新增",
        "trendLabel": "新增",
        "subdomain": "foo",
        "path": "/path",
        "clicks": 123,
        "topKeywords": "foo keyword"
      }
    ]
  }
}
```

## 字段说明

`rows[]`（标准化页面样本）必须包含：
- `landingPageUrl`
- `hostname`
- `subdomain`
- `clicks`
- `clicksShare`
- `clicksChangeApi`
- `topKeyword`
- `page`
- `rankInPage`

`comparison.reportRows[]`（统一报告行）包含：
- `entityType`：`page` 或 `subdomain`
- `trend`：`新增` 或 `上涨`
- `trendLabel`：展示用趋势文本；上涨时附带涨幅
- `subdomain`
- `path`：页面行为真实 path，子域名行为 `-`
- `clicks`：页面取页面 clicks，子域名取 `observedSubdomainClicks`
- `topKeywords`：页面取 `topKeyword`，子域名取样本内高点击页面关键词拼接预览

判定规则：
- 页面新增：today 有、baseline 无、`clicks>=100`
- 页面上涨：两边都有，且 `today.clicks>=100`、`delta>=30`、`growthRate>5%`
- 子域名新增：today 有、baseline 无、`observedSubdomainClicks>=150`
- 子域名上涨：两边都有，且 `today.observedSubdomainClicks>=150`、`delta>=50`、`growthRate>5%`

首次运行（`baselineMode=true`）：`comparison.reportRows` 为空。
