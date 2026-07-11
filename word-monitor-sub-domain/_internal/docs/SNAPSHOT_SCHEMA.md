# Snapshot Schema（MVP）

文件：`_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`

```json
{
  "meta": {
    "generatedAt": "2026-07-08T21:00:01",
    "stamp": "20260708-210001",
    "baselineMode": false,
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
      "endPage": 8,
      "standardWordTableVersion": "v1"
    },
    "api": {
      "apiUrl": "http://127.0.0.1:17311/sim/api/websiteOrganicLandingPagesV2",
      "pagesRequested": [1, 2, 3, 4, 5, 6, 7, 8],
      "basePayload": {},
      "gefeiKD": {
        "apiUrl": "https://seo.web.cafe/kd/api/v1/kd",
        "authMode": "header",
        "apiKeySource": ".../check-gefei-kd/api_key.txt"
      }
    },
    "output": {
      "reportHistoryPath": ".../report/history/report-20260708-210001.md",
      "excelHistoryPath": ".../report/history/keyword-table-20260708-210001.xlsx",
      "finalWordsXlsxPath": ".../words/sub-domain-20260708-210001.xlsx",
      "chainStages": {
        "status": "completed",
        "chainRoot": ".../_internal/chained/20260708-210001",
        "analyzeWords": {
          "latestXlsxPath": ".../_internal/chained/20260708-210001/analyze-words/report/latest.xlsx",
          "latestJsonPath": ".../_internal/chained/20260708-210001/analyze-words/report/latest.json"
        },
        "checkGefeiKd": {
          "latestXlsxPath": ".../_internal/chained/20260708-210001/check-gefei-kd/report/latest.xlsx",
          "latestJsonPath": ".../_internal/chained/20260708-210001/check-gefei-kd/report/latest.json"
        }
      }
    },
    "latestReportPath": ".../report/latest.md",
    "latestExcelPath": ".../report/latest.xlsx",
    "pagesFetched": 8,
    "startPage": 1,
    "endPage": 8,
    "rawRows": 800,
    "dedupedRows": 420,
    "subdomainCount": 220,
    "invalidUrlRows": 0,
    "nonTargetRows": 80,
    "gefeiKD": {
      "summary": {
        "inputCount": 20,
        "requestCount": 20,
        "successCount": 18,
        "successWithScoreCount": 17,
        "missingScoreCount": 1,
        "failedCount": 2
      },
      "failures": []
    }
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
    ],
    "standardWordRows": [
      {
        "keyword": "foo keyword",
        "correspondingDomain": "https://foo.vercel.app/path | https://foo.vercel.app/other",
        "score": null,
        "simWindowVolume": null,
        "simKd": null,
        "simCpc": null,
        "semVolume": null,
        "semKd": null,
        "semCpc": null,
        "gefeiKD": 18,
        "group": "",
        "sourcePresence": ""
      }
    ],
    "standardWordSummary": {
      "rowCount": 1,
      "newPageKeywordRows": 1,
      "newSubdomainKeywordRows": 0
    },
    "gefeiKD": {
      "summary": {
        "inputCount": 1,
        "requestCount": 1,
        "successCount": 1,
        "successWithScoreCount": 1,
        "missingScoreCount": 0,
        "failedCount": 0
      },
      "failures": [],
      "api": {
        "apiUrl": "https://seo.web.cafe/kd/api/v1/kd",
        "authMode": "header",
        "apiKeySource": ".../check-gefei-kd/api_key.txt"
      }
    }
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

`comparison.standardWordRows[]`（用于标准词表 Excel `keywords` sheet）包含：
- `keyword`
- `correspondingDomain`
- `score`
- `simWindowVolume`
- `simKd`
- `simCpc`
- `semVolume`
- `semKd`
- `semCpc`
- `gefeiKD`
- `group`
- `sourcePresence`

其中：
- 当前仅导出新增页面 / 新增子域名对应的 top keywords
- 相同 `keyword` 只保留一行
- `correspondingDomain` 聚合该 keyword 命中的全部域名 / 页面上下文，使用 ` | ` 连接；若同 host 已存在完整 URL（无论来自 `host url` 组合项还是独立 URL 项），则移除该 host 的裸子域名项
- 其余指标列允许为空，以兼容标准词表统一结构
- `gefeiKD` 为哥飞 KD API 返回的 `score`；查不到时允许为空

额外元信息：
- `comparison.gefeiKD.summary`：本次标准词表 enrichment 的输入量 / 成功量 / 失败量
- `comparison.gefeiKD.failures[]`：失败关键词及错误信息
- `meta.api.gefeiKD`：本次查询使用的 API 地址、鉴权方式与 key 来源
- `meta.output.finalWordsXlsxPath`：发布到 `words/sub-domain-[timestamp].xlsx` 的最终完整标准词表路径
- `meta.output.chainStages`：后置串联链路执行结果
  - `status=completed`：成功执行 analyze-words 与 check-gefei-kd
  - `status=skipped`：本次 `standardWordRows=0`，跳过串联，最终词表直接来自历史 `keyword-table-{stamp}.xlsx`

判定规则：
- 页面新增：today 有、baseline 无、`clicks>=100`
- 页面上涨：两边都有，且 `today.clicks>=100`、`delta>=30`、`growthRate>5%`
- 子域名新增：today 有、baseline 无、`observedSubdomainClicks>=150`
- 子域名上涨：两边都有，且 `today.observedSubdomainClicks>=150`、`delta>=50`、`growthRate>5%`

首次运行（`baselineMode=true`）：
- `comparison.reportRows` 为空
- `comparison.standardWordRows` 为空
