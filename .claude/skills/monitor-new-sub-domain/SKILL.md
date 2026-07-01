---
name: monitor-new-sub-domain
version: 1.4.0
description: "分析 monitor-new-sub-domain/data 中最新抓包 JSON，发现 *.vercel.app 新增子域名并输出可读中文报告（强制真实抓取页面信号后再判定用途）。"
---

# monitor-new-sub-domain

用于处理 SimilarWeb 抓包数据，自动生成：

1. 最新 `*.vercel.app` 子域名清单
2. 与上一份基线相比的新增子域名
3. 新增子域名点击量、趋势、趋势判断、网站用途（可读中文报告）

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

1. 标题与摘要（新增域名汇总、持续上涨域名汇总；新增数量、总点击量、趋势窗口、对比基线）
2. `新增子域名清单` 主表：
   - `#`
   - `新增子域名`
   - `点击量`
   - `趋势（最新/峰值)`
   - `趋势判断`
   - `页面抓取状态`
   - `网站用途`
   - `关键词覆盖`
3. `逐站分析（关键词趋势 + 网站用途）`：逐个列出
   - 页面抓取状态
   - 页面标题/描述/H1
   - 用途判断依据
   - 关键词（SimilarWeb / 页面候选 / 融合，非穷尽）

> 样式约定：报告内容使用纯文本，不使用 Markdown 粗体（`**...**`）。
> 注意：不再输出 `## 示例页面（Top N）` 区块。

## 关键约束

1. **用途分类必须先真实抓站**：仅在成功打开站点并抓取页面信号（title/description/h1）后，才允许用途判定。
2. **抓取失败不做盲判**：页面不可达时输出“未判定（失败原因）”。
3. **关键词完整性声明**：
   - SimilarWeb 侧来自抓包字段聚合（不是搜索引擎全量词库）
   - 页面侧为 title/description/h1 抽取的候选关键词
   - 融合关键词为“非穷尽”结果

## 处理逻辑

1. 识别最新抓包文件（按文件名时间 `YYYYMMDD-HHMM`）
2. 从 `records[].responseBody` 解析 `Data[]`
3. 提取并规范化 `*.vercel.app` host/subdomain
4. 按 host 聚合点击量、趋势、SimilarWeb关键词
5. 与上一份快照（或上一份 raw）对比新增
6. 对新增域名逐个：
   - 打开网站抓取 title/description/h1
   - 成功后进行用途判定并给出命中依据
   - 抽取页面候选关键词并与 SimilarWeb 关键词融合

## 请求/响应结构说明

详见：

- `monitor-new-sub-domain/_internal/docs/SKILL_GUIDE.md`
