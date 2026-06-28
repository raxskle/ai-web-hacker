# monitor-new-sub-domain 指导文档

## 目标

自动分析 `monitor-new-sub-domain/data` 中最新抓包 JSON，提取 `*.vercel.app` 子域名快照，和上一份结果对比，输出两类中文报告：

- 新增子域名
- 最近点击量持续上涨的非新增子域名

新版重点：

1. **用途判定必须先真实打开站点**并抓取 `title / description / h1`
2. 抓取失败时**不允许盲判网站用途**
3. 关键词按来源区分展示（SimilarWeb / 网站发现）
4. 额外识别“持续上涨（非新增）”子域名（默认口径：最近4周连续上涨 + 涨幅阈值 + 最新值阈值）

---

## 输入文件规范

### 1) 文件命名

`[输入匹配规则]-[YYYYMMDD-HHMM].json`

示例：

- `websiteOrganicLandingPagesV2-20260627-1327.json`

流程按文件名中的时间选择“最新”与“上一份”，不依赖文件修改时间。

### 2) 顶层结构

```json
{
  "meta": {},
  "records": [],
  "grouped": [],
  "ai_hint": ""
}
```

---

## 请求/响应结构（基于当前目录样本）

样本来源：

- `monitor-new-sub-domain/data/websiteOrganicLandingPagesV2-20260626-1523.json`

### A. `meta`

常见字段：

- `exportedAt`: 导出时间戳（毫秒）
- `rule`: 录制规则（可能多行）
- `startedAt`, `stoppedAt`: 录制开始/结束时间戳
- `capturedCount`, `dedupedCount`, `duplicateCollapsedCount`, `droppedCount`, `totalChars`

### B. `records[]`

每条记录为一次请求抓包（去重后），关键字段：

- `timestamp`, `url`, `method`, `status`, `contentType`
- `requestBody`
- `responseBody`（关键：这里是字符串化 JSON）
- `responseEncoding`, `responseTruncated`
- `requestHeaders`, `responseHeaders`, `error`
- `duplicateCount`, `duplicateRecordIds`

处理时仅消费：

- `status == 200`
- `responseBody` 可成功 `JSON.parse`

### C. `responseBody` 内层结构

`records[i].responseBody` 解析后常见结构：

```json
{
  "FromAlternativeSources": false,
  "TotalCount": 11672,
  "TotalTopLevelCount": 0,
  "Data": []
}
```

### D. `Data[]` 关键字段

每行至少关注：

- `Url`: 可能是 `host/path?query` 形式（常见为 `*.vercel.app`）
- `Clicks`: 点击量
- `ClicksShare`: 点击占比
- `Trend`: 周维度序列（样本中为 13 个日期点）
- `TopKeyword`

---

## 处理规则

### 1) 子域名提取

从 `Data[].Url` 提取 host，仅保留：

- `host.endswith('.vercel.app')`
- `host != 'vercel.app'`

### 2) 聚合口径（按 host）

一个 host 可能对应多个路径，按 host 聚合并输出：

- `clicks_sum`
- `trend_13w_sum`（同日期周点求和）
- `top_keyword` + `keywords`（SimilarWeb 来源聚合）

### 3) 对比口径

- current：最新 raw 文件生成的快照
- previous：上一份快照（若无则回退上一份 raw 临时构建）
- 新增：`new_hosts = current_hosts - previous_hosts`
- 持续上涨（非新增）：在 `current ∩ previous` 中筛选，默认口径：
  - 最近 4 个趋势点连续上涨（严格单调）
  - 窗口涨幅 ≥ 30%
  - 最新值 ≥ 50

### 4) 页面抓取与用途判定（强制门禁）

对命中的新增域名与持续上涨域名：

1. 真实请求站点页面
2. 解析并抽取 `title / description / h1`
3. **仅在页面抓取成功时**允许用途判定
4. 抓取失败：输出 `未判定（失败原因）`

### 5) 关键词输出规则

逐站报告按两类输出：

- `关键词（SimilarWeb）`：抓包字段聚合
- `关键词（网站发现）`：从 `title/description/h1` 抽取（去噪、去重后）

> 说明：本工具不承诺输出“搜索引擎全量关键词”。网站发现关键词来源于页面抓取得到的内容信号。

---

## 报告格式（当前约定）

报告分为三段：

1. 标题与摘要
   - 新增数量 / 持续上涨数量
   - 两类总点击量
   - 趋势统计窗口
   - 持续上涨判定口径
   - 对比基线
2. 新增子域名详情（关键词趋势 + 网站用途，列表形式，非表格）
   - 直接合并原“新增子域名清单 + 新增逐站详情”
   - `#`
   - `新增子域名`
   - `点击量`
   - `趋势判断（最新/峰值）`
   - `页面抓取状态`
   - `网站用途`
   - `页面标题（抓取）`
   - `页面H1（抓取）`
   - `关键词（SimilarWeb）`
   - `关键词（网站发现）`
3. 持续上涨子域名详情（非新增，关键词趋势 + 网站用途，列表形式，非表格）
   - 直接合并原“持续上涨清单 + 持续上涨逐站详情”
   - `#`
   - `持续上涨子域名`
   - `点击量`
   - `趋势判断（最新/峰值）`
   - `连续上涨窗口`
   - `窗口涨幅`
   - `持续上涨证据`
   - `页面抓取状态`
   - `网站用途`
   - `页面标题（抓取）`
   - `页面H1（抓取）`
   - `关键词（SimilarWeb）`
   - `关键词（网站发现）`

说明：
- 不再输出 `## 示例页面（Top N）` 区块。
- 报告以“可审计、可读、可回溯”为优先。

---

## 产物

- 快照：`monitor-new-sub-domain/_internal/snapshots/subdomains-YYYYMMDD-HHMM.json`
- 子域名列表：`monitor-new-sub-domain/_internal/snapshots/subdomain-list-YYYYMMDD-HHMM.txt`
- 历史报告：`monitor-new-sub-domain/reports/history/final-report-YYYYMMDD-HHMM.md`
- 最新报告：`monitor-new-sub-domain/reports/latest.md`

---

## 执行命令

```bash
# 生成最新报告（读取 data 下最新 JSON）
python3 monitor-new-sub-domain/_internal/scripts/monitor_new_subdomain.py run

# 根据已有快照重建全部历史报告并更新 latest.md
python3 monitor-new-sub-domain/_internal/scripts/monitor_new_subdomain.py rebuild-reports
```
