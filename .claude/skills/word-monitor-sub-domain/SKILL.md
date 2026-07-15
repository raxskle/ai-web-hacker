---
name: word-monitor-sub-domain
version: 0.2.0
description: "抓取 vercel.app 的 Landing Pages 前8页样本，输出新增/上涨统一监控报告，并串联 analyze-words + check-gefei-kd 产出完整标准词表。"
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
- 历史 Excel：`word-monitor-sub-domain/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx`（最终完整词表）
- 最新报告：`word-monitor-sub-domain/report/latest.md`（最终词表口径）
- 最新 Excel：`word-monitor-sub-domain/report/latest.xlsx`（最终完整词表）
- **最终标准词表（完整）**：`words/sub-domain-YYYYMMDD-HHMMSS.xlsx`（仓库根目录）

## 规则摘要（MVP）

- 固定抓取参数：`key=vercel.app`，`page=1..8`，`sort=ClicksShare` 等
- 每页失败重试 2 次；仍失败则整次失败，不落快照/报告/Excel
- 基线取最近一次历史快照（同 key/country/latest/sourceType/startPage/endPage）；子域名上涨需连续两段比较均达阈值
- 首次运行仅建立基线，不输出新增/上涨结论
- 页面和子域名结果合并为一个 Markdown 表格，只区分 `新增` 与 `上涨`
- 标准词表种子先导出新增页面/新增子域名/连续上涨子域名对应的 top keywords，再经 `analyze-words` + `check-gefei-kd` 补全为最终完整词表
- 相同 `keyword` 按词去重，仅保留一行
- `对应域名` 聚合同词命中的全部域名 / 页面上下文；若同 host 已存在完整 URL（无论来自 `host url` 组合项还是独立 URL 项），则移除该 host 的裸子域名项
- 运行后置补全链路：按顺序调用 `analyze-words`（补全 SIM/SEM）→ `check-gefei-kd`（刷新 `gefeiKD`）
- 最终 `keywords` sheet 列顺序：`keyword -> 对应域名 -> score -> volume(sim) -> kd(sim) -> cpc(sim) -> volume(sem) -> kd(sem) -> cpc(sem) -> gefeiKD -> group -> sourcePresence(SIM/SEM)`
- Excel 数值列按数字类型写入，`keywords` 数据区配色：SIM 列浅蓝、SEM 列浅紫
- `report/history/*.md` 与 `report/latest.md` 会按最终词表口径重写，确保与最终词表一致
- 最终完整词表发布到 `words/sub-domain-[timestamp].xlsx`（仓库根目录）
- 上涨需同时满足现有绝对门槛，以及相对基线点击量 `> 5%`；子域名上涨要求最近两段比较（today vs t-1、t-1 vs t-2）均满足该条件
