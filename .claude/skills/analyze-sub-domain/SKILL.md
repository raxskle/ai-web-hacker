---
name: analyze-sub-domain
version: 0.1.0
description: "基于 monitor-new-sub-domain 的候选子域名做逐站深度分析，识别新词/搜索意图/问题-解法/赛道质量，并输出可执行建站报告。"
---

# analyze-sub-domain

用于在 `monitor-new-sub-domain` 已识别候选（新增 + 持续上涨）的基础上，进一步给出“是否值得按关键词建站”的决策报告。

## 执行方式

在仓库根目录执行：

```bash
# 分析最新一期 monitor 快照并输出建站建议报告
python3 analyze-sub-domain/_internal/scripts/analyze_subdomain.py run

# 用历史分析 JSON 重建全部报告
python3 analyze-sub-domain/_internal/scripts/analyze_subdomain.py rebuild-reports

# 校验报告结构完整性
python3 analyze-sub-domain/_internal/scripts/analyze_subdomain.py validate-report --report analyze-sub-domain/reports/latest.md
```

## 输入输出

- 依赖输入：`monitor-new-sub-domain/_internal/snapshots/subdomains-YYYYMMDD-HHMM.json`
- 中间产物：`analyze-sub-domain/data/history/analysis-YYYYMMDD-HHMM.json`
- 历史报告：`analyze-sub-domain/reports/history/analyze-report-YYYYMMDD-HHMM.md`
- 最新报告：`analyze-sub-domain/reports/latest.md`

## 分析维度

1. 关键词新词分（Novelty）
2. 搜索意图（Intent）
3. 网站解决的问题与可复制解法
4. 赛道质量评分（Track Score）
5. 不适合建站类型过滤（个人博客、产品官网等）

## 关键约束

1. **逐站真实抓取后再判定**：仅抓到页面信号才输出意图/问题/赛道结论。
2. **过滤有证据**：命中过滤规则时必须写明命中词与页面线索。
3. **推荐可执行**：每个推荐机会需包含站型建议、MVP 页面建议、建议动作。
4. **域名样式统一**：报告中的域名行使用纯文本，不使用 `**` 包裹。

## 详细说明

详见：

- `analyze-sub-domain/_internal/skill/SKILL.md`
- `analyze-sub-domain/_internal/docs/SKILL_GUIDE.md`
- `analyze-sub-domain/_internal/docs/SCORING_RUBRIC.md`
