---
name: monitor-new-sub-domain
version: 1.4.0
description: "分析 monitor-new-sub-domain/data 中最新抓包 JSON，输出新增子域名与最近持续上涨（非新增）子域名的可读中文报告（强制真实抓取页面信号后再判定用途）。"
---

# monitor-new-sub-domain

用于处理 SimilarWeb 抓包数据，自动生成：

1. 最新 `*.vercel.app` 子域名清单
2. 与上一份基线相比的新增子域名
3. 最近点击量持续上涨的非新增子域名
4. 两类子域名的点击量、趋势、趋势判断、网站用途（可读中文报告）

## 执行方式

在仓库根目录执行：

```bash
# 生成最新报告（默认读取 data 下最新 JSON）
python3 monitor-new-sub-domain/_internal/scripts/monitor_new_subdomain.py run

# 重建全部历史报告（按当前模板回填 reports/history）
python3 monitor-new-sub-domain/_internal/scripts/monitor_new_subdomain.py rebuild-reports
```

## 输入输出

- 输入目录：`monitor-new-sub-domain/data`
- 规范化快照：`monitor-new-sub-domain/_internal/snapshots/subdomains-YYYYMMDD-HHMM.json`
- 子域名列表：`monitor-new-sub-domain/_internal/snapshots/subdomain-list-YYYYMMDD-HHMM.txt`
- 历史报告：`monitor-new-sub-domain/reports/history/final-report-YYYYMMDD-HHMM.md`
- 最新报告：`monitor-new-sub-domain/reports/latest.md`

## 报告格式（当前约定）

报告固定包含：

1. 标题与摘要（新增域名汇总、持续上涨域名汇总；新增数量、持续上涨数量、两类总点击量、趋势窗口、对比基线）
2. `新增子域名详情（关键词趋势 + 网站用途）`（列表形式，非表格，直接合并原“清单信息+详情信息”）：
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
3. `最近点击量持续上涨的子域名详情（非新增，关键词趋势 + 网站用途）`（列表形式，非表格，直接合并原“清单信息+详情信息”）：
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

> 样式约定：报告中的域名行使用纯文本，不使用 `**` 包裹。
> 注意：不再输出 `## 示例页面（Top N）` 区块。

## 关键约束

1. **用途分类必须先真实抓站**：仅在成功打开站点并抓取页面信号（title/description/h1）后，才允许用途判定。
2. **抓取失败不做盲判**：页面不可达时输出“未判定（失败原因）”。
3. **关键词完整性声明**：
   - SimilarWeb 侧来自抓包字段聚合（不是搜索引擎全量词库）
   - 网站发现关键词来自页面抓取得到的 title/h1/description 信号（去噪、去重后）

## 处理逻辑

1. 识别最新抓包文件（按文件名时间 `YYYYMMDD-HHMM`）
2. 从 `records[].responseBody` 解析 `Data[]`
3. 提取并规范化 `*.vercel.app` host/subdomain
4. 按 host 聚合点击量、趋势、SimilarWeb关键词
5. 与上一份快照（或上一份 raw）对比并输出两类结果：
   - 新增子域名
   - 持续上涨子域名（非新增，默认口径：最近4周连续上涨 + 窗口涨幅≥30% + 最新值≥50）
6. 对命中域名逐个：
   - 打开网站抓取 title/description/h1
   - 成功后进行用途判定并给出命中依据
   - 输出 SimilarWeb 关键词与网站发现关键词（仅保留这两类）

## 请求/响应结构说明

详见：

- `monitor-new-sub-domain/_internal/docs/SKILL_GUIDE.md`
