---
name: word-monitor-sub-domain
version: 0.1.0
description: "抓取 vercel.app 的 Landing Pages 前5页样本，输出新增/上涨页面与子域名监控报告。"
---

# word-monitor-sub-domain

每天执行一次监控流程：

```bash
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py run
```

可选命令：

```bash
# 基于快照重建报告
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py rebuild-reports

# 校验报告结构
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py validate-report
```

## 输入输出

- 本地服务文档：`word-monitor-sub-domain/local-service/API_REFERENCE.md`
- token 文件：`word-monitor-sub-domain/local-service/bridge_token.txt`
- 抓取归档：`word-monitor-sub-domain/data/fetch-YYYYMMDD-HHMMSS.json`
- 快照归档：`word-monitor-sub-domain/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史报告：`word-monitor-sub-domain/report/history/report-YYYYMMDD-HHMMSS.md`
- 最新报告：`word-monitor-sub-domain/report/latest.md`

## 规则摘要（MVP）

- 固定抓取参数：`key=vercel.app`，`page=1..5`，`sort=ClicksShare` 等
- 每页失败重试 2 次；仍失败则整次失败，不落快照/报告
- 基线取最近一次历史快照（同 key/country/latest/sourceType）
- 首次运行仅建立基线，不输出新增/上涨结论
