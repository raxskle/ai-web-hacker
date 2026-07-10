---
name: word-monitor-sub-domain
version: 0.1.0
description: "抓取 vercel.app 的 Landing Pages 前8页样本，输出新增/上涨统一监控报告与标准词表 Excel。"
---

# word-monitor-sub-domain

每天执行一次监控流程：

```bash
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py run
```

可选命令：

```bash
# 基于快照重建 Markdown / Excel
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py rebuild-reports

# 校验 Markdown / Excel
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py validate-report
```

## 输入输出

- 本地服务文档：`word-monitor-sub-domain/local-service/API_REFERENCE.md`
- token 文件：`word-monitor-sub-domain/local-service/bridge_token.txt`
- 抓取归档：`word-monitor-sub-domain/data/fetch-YYYYMMDD-HHMMSS.json`
- 快照归档：`word-monitor-sub-domain/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史报告：`word-monitor-sub-domain/report/history/report-YYYYMMDD-HHMMSS.md`
- 历史 Excel：`word-monitor-sub-domain/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx`
- 最新报告：`word-monitor-sub-domain/report/latest.md`
- 最新 Excel：`word-monitor-sub-domain/report/latest.xlsx`

## 规则摘要（MVP）

- 固定抓取参数：`key=vercel.app`，`page=1..8`，`sort=ClicksShare` 等
- 每页失败重试 2 次；仍失败则整次失败，不落快照/报告/Excel
- 基线取最近一次历史快照（同 key/country/latest/sourceType/startPage/endPage）
- 首次运行仅建立基线，不输出新增/上涨结论
- 页面和子域名结果合并为一个 Markdown 表格，只区分 `新增` 与 `上涨`
- 标准词表仅导出新增页面/子域名对应的 top keywords
- 相同 `keyword` 按词去重，仅保留一行
- `对应域名` 聚合同词命中的全部域名 / 页面上下文
- `gefeiKD` 使用哥飞 KD API 返回的 `score`
- 上涨需同时满足现有绝对门槛，以及相对基线点击量 `> 5%`
