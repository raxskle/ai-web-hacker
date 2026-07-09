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
      "endPage": 5
    },
    "api": {
      "apiUrl": "http://127.0.0.1:17311/sim/api/websiteOrganicLandingPagesV2",
      "pagesRequested": [1, 2, 3, 4, 5],
      "basePayload": {}
    },
    "pagesFetched": 5,
    "startPage": 1,
    "endPage": 5,
    "rawRows": 500,
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
    "newlyObservedPage": [],
    "risingPage": [],
    "newlyObservedSubdomain": [],
    "risingSubdomain": []
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

`comparison` 规则：
- `newlyObservedPage`: today 有、baseline 无、`clicks>=100`
- `risingPage`: 两边都有，且 `today.clicks>=100`、`delta>=30`、`growth>=20%`
- `newlyObservedSubdomain`: today 有、baseline 无、`observedSubdomainClicks>=150`
- `risingSubdomain`: 两边都有，且 `today.observedSubdomainClicks>=150`、`delta>=50`（不限制增长率）

首次运行（`baselineMode=true`）：四类结果数组均为空。
