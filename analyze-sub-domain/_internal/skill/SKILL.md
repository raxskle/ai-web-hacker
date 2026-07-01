---
name: analyze-sub-domain
version: 0.1.0
description: "将 monitor-new-sub-domain 的候选子域名做深度逐站分析，输出可执行的关键词建站机会报告。"
---

# analyze-sub-domain

## 目标

基于 `monitor-new-sub-domain` 的候选集合（新增 `*.vercel.app` + 持续上涨非新增），逐个站点深入抓取并完成建站决策分析：

- 关键词是否为新词
- 搜索意图是什么
- 网站在解决什么问题
- 是否是好赛道
- 是否应被过滤（个人博客、产品官网等）

## 执行命令

```bash
python3 analyze-sub-domain/_internal/scripts/analyze_subdomain.py run
python3 analyze-sub-domain/_internal/scripts/analyze_subdomain.py rebuild-reports
python3 analyze-sub-domain/_internal/scripts/analyze_subdomain.py validate-report --report analyze-sub-domain/reports/latest.md
```

## 输入输出

- monitor 快照输入目录（默认）：
  - `monitor-new-sub-domain/_internal/snapshots`
- analyze 中间数据：
  - `analyze-sub-domain/data/history/analysis-YYYYMMDD-HHMM.json`
- analyze 报告：
  - `analyze-sub-domain/reports/history/analyze-report-YYYYMMDD-HHMM.md`
  - `analyze-sub-domain/reports/latest.md`

## 处理流程（run）

1. 读取 monitor 最新快照与上一快照
2. 复用 monitor 规则提取候选（新增 + 持续上涨）
3. 对每个候选站点做同域深爬（限页数/深度）
4. 融合 SimilarWeb 与页面发现关键词
5. 计算新词分、意图、问题-解法、赛道分
6. 应用硬过滤规则
7. 生成结构化 JSON 与中文报告

## 报告重点

- Top 建站机会（可直接执行）
- 候选清单总览（含评分与动作）
- 排除清单（含证据）

> 样式约定：报告中的域名行使用纯文本，不使用 `**` 包裹。
> 说明：此 skill 不修改 `monitor-new-sub-domain` 的既有逻辑，仅消费其快照结果。
