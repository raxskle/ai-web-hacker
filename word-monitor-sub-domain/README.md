# word-monitor-sub-domain

用于监控 `vercel.app` 在 Similarweb Organic Landing Pages（`ClicksShare` 排序）前 8 页样本，按天归档并输出“新增/上涨”统一报告，以及配套标准词表。

## 功能概览

每次运行会执行：

1. 调用本地服务抓取 `page=1..8`
2. 标准化并去重页面数据
3. 归档抓取结果与快照
4. 与最近两次历史快照对比（用于判断子域名连续上涨）
5. 生成 Markdown 报告（单表合并展示页面与子域名结果）
6. 生成初始标准词表 Excel（输出新增页面/新增子域名/连续上涨子域名的 top keywords）
7. 串联 `analyze-words` 补全 SIM/SEM
8. 串联 `check-gefei-kd` 回填/刷新 `gefeiKD`
9. 发布最终完整标准词表到 `words/sub-domain-YYYYMMDD-HHMMSS.xlsx`

## 目录说明

- `data/`：每次抓取归档（`fetch-YYYYMMDD-HHMMSS.json`）
- `_internal/snapshots/`：标准化快照（`snapshot-YYYYMMDD-HHMMSS.json`）
- `report/history/`：历史报告与最终完整标准词表 Excel
- `report/latest.md`：最新报告（最终词表口径）
- `report/latest.xlsx`：最新最终完整标准词表 Excel
- `words/`（仓库根目录）：最终完整标准词表（`sub-domain-YYYYMMDD-HHMMSS.xlsx`）
- `local-service/`：本地服务接口文档与 token 文件

## 运行前准备

1. 本地服务已启动
2. 浏览器扩展已安装并可用
3. 已登录 `https://sim.3ue.co`
4. token 文件存在：`local-service/bridge_token.txt`
5. 已安装 Excel 导出依赖：

```bash
pip3 install openpyxl
```

可先检查健康状态：

```bash
curl -s http://127.0.0.1:17311/health
```

## 使用方式

在仓库根目录执行：

```bash
# 执行一次完整监控
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py run
```

可选命令：

```bash
# 基于快照重建 Markdown / Excel
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py rebuild-reports

# 校验 Markdown / Excel
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py validate-report
```

## 当前规则（MVP）

### 固定抓取参数

- `key=vercel.app`
- `country=999`
- `latest=28d`
- `webSource=Total`
- `sourceType=organic`
- `sort=ClicksShare`
- `asc=false`
- `includeSubDomains=true`
- `isWindow=true`
- `searchType=domain`
- `page=1..8`

### 失败策略

- 每页请求失败会自动重试 2 次
- 任意一页最终失败：整次运行失败，不落快照、不出结论（避免污染数据）
- 哥飞 KD 认证/全局额度错误：整次运行失败，不落半残标准词表
- 单关键词哥飞 KD 查询失败：该行 `gefeiKD` 留空，并写入 snapshot 失败明细
- 串联补全链路（analyze/check）任一步失败：本次 run 返回失败

### 对比基线

- 页面 / 新增子域名：基线取最近一次历史快照（同 `key/country/latest/sourceType/startPage/endPage`）
- 子域名上涨：同时检查最近两次历史快照，仅当
  - `(today vs t-1)` 满足上涨阈值，且
  - `(t-1 vs t-2)` 也满足上涨阈值
  才计入“上涨子域名”
- 首次运行仅建立基线，不输出新增/上涨结论

### 判定阈值

页面级：
- `newlyObservedPage`：今天有、基线无，且 `clicks >= 100`
- 页面上涨：今天和基线都有，且
  - `today.clicks >= 100`
  - `deltaClicks >= 30`
  - `growthRate > 5%`

子域名级：
- `newlyObservedSubdomain`：今天有、基线无，且 `observedSubdomainClicks >= 150`
- 子域名上涨：必须连续 2 次比较都满足上涨阈值
  - `(today vs t-1)`：`today.observedSubdomainClicks >= 150`、`deltaClicks >= 50`、`growthRate > 5%`
  - `(t-1 vs t-2)`：`t-1.observedSubdomainClicks >= 150`、`deltaClicks >= 50`、`growthRate > 5%`
  - 仅当同一 `subdomain` 两段都达标，才在报告中标记为 `上涨`

### 报告与标准词表输出

- 页面和子域名结果合并为同一个 Markdown 表格
- Markdown 仍仅区分 `新增` 与 `上涨`
- 标准词表种子先导出 `新增` 页面/子域名 + `连续上涨子域名` 的 top keywords
- 标准词表表头对齐 `standard-word-analysis/spec/standard-word-table.v1.json`
- 相同 `keyword` 按词去重，仅保留一行
- `对应域名` 聚合同词命中的全部域名 / 页面上下文，使用 ` | ` 连接；若同 host 已存在完整 URL（无论来自 `host url` 组合项还是独立 URL 项），则移除该 host 的裸子域名项
- 种子词表会继续串联 `analyze-words` 与 `check-gefei-kd`，并将最终完整结果同步覆盖到：
  - `word-monitor-sub-domain/report/history/report-[timestamp].md`
  - `word-monitor-sub-domain/report/latest.md`
  - `word-monitor-sub-domain/report/history/keyword-table-[timestamp].xlsx`
  - `word-monitor-sub-domain/report/latest.xlsx`
  - `words/sub-domain-[timestamp].xlsx`（仓库根目录）
- 文本列导出采用自动换行（wrap）+ 顶对齐，避免长内容遮挡相邻列
- `group` / `对应域名` 在展示层按多值分行（单元格内换行）以提升可读性
- 最终 `keywords` sheet 列顺序：`keyword -> 对应域名 -> score -> volume(sim) -> kd(sim) -> cpc(sim) -> volume(sem) -> kd(sem) -> cpc(sem) -> gefeiKD -> group -> sourcePresence(SIM/SEM)`
- Excel 数值列按数字类型写入，`keywords` 数据区配色：SIM 列浅蓝、SEM 列浅紫
- 其他指标列允许为空

## 报告备注（固定输出）

报告中会固定包含以下声明：

1. 当前监控仅覆盖 ClicksShare 排序下前8页样本
2. “新进入样本”不等于全站首次出现
3. 子域名流量是样本内观测值，不代表全站完整总量

## 相关文件

- 外层 skill 入口：`.claude/skills/word-monitor-sub-domain/SKILL.md`
- 内部说明：`word-monitor-sub-domain/_internal/skill/SKILL.md`
- 快照结构：`word-monitor-sub-domain/_internal/docs/SNAPSHOT_SCHEMA.md`
