# analyze-sub-domain 指导文档

## 目标

将 `monitor-new-sub-domain` 已识别的候选子域名进一步深度分析，输出“适合按关键词建站”的行动报告。

## 数据来源

- monitor 快照：`monitor-new-sub-domain/_internal/snapshots/subdomains-YYYYMMDD-HHMM.json`
- 候选集合：
  - 新增 host（`current - previous`）
  - 持续上涨 host（非新增）

## 核心流程

1. 读取最新与上一期 monitor 快照
2. 复用 monitor 函数生成候选 host
3. 逐站同域抓取（默认限页数和深度）
4. 融合关键词（SimilarWeb + 页面发现）
5. 判定意图、问题、赛道分并执行硬过滤
6. 输出 JSON（可审计）+ Markdown（可读）

## 中间产物 JSON

输出至 `analyze-sub-domain/data/history/analysis-YYYYMMDD-HHMM.json`，包含：

- 元信息（数据源、时间、规则版本）
- 全量候选列表（含评分、过滤原因、证据）
- 通过项与排除项统计

## 报告结构（latest/history）

1. 执行摘要
2. Top 建站机会
3. 候选清单总览
4. 排除清单（含证据）
5. 附录（来源 stamp、阈值、版本）

## 运行命令

```bash
python3 analyze-sub-domain/_internal/scripts/analyze_subdomain.py run
python3 analyze-sub-domain/_internal/scripts/analyze_subdomain.py rebuild-reports
python3 analyze-sub-domain/_internal/scripts/analyze_subdomain.py validate-report --report analyze-sub-domain/reports/latest.md
```

## 注意事项

- 抓取失败时应保留失败信息，避免无依据强判。
- 报告推荐项必须输出“建议动作”与“MVP 页面建议”。
- 过滤项必须可追溯（命中词 + 页面线索）。
