# word-monitor-sub-domain

用于监控 `vercel.app` 在 Similarweb Organic Landing Pages（`ClicksShare` 排序）前 5 页样本，按天归档并输出“新增/上涨”报告。

## 功能概览

每次运行会执行：

1. 调用本地服务抓取 `page=1..5`
2. 标准化并去重页面数据
3. 归档抓取结果与快照
4. 与最近一次历史快照对比
5. 生成 Markdown 报告（页面级 + 子域名级）

## 目录说明

- `data/`：每次抓取归档（`fetch-YYYYMMDD-HHMMSS.json`）
- `_internal/snapshots/`：标准化快照（`snapshot-YYYYMMDD-HHMMSS.json`）
- `report/history/`：历史报告
- `report/latest.md`：最新报告
- `local-service/`：本地服务接口文档与 token 文件

## 运行前准备

1. 本地服务已启动
2. 浏览器扩展已安装并可用
3. 已登录 `https://sim.3ue.co`
4. token 文件存在：`local-service/bridge_token.txt`

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
# 基于快照重建报告
python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py rebuild-reports

# 校验报告结构
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
- `page=1..5`

### 失败策略

- 每页请求失败会自动重试 2 次
- 任意一页最终失败：整次运行失败，不落快照、不出结论（避免污染数据）

### 对比基线

- 使用最近一次历史快照（同 `key/country/latest/sourceType`）
- 首次运行仅建立基线，不输出新增/上涨结论

### 判定阈值

页面级：
- `newlyObservedPage`：今天有、基线无，且 `clicks >= 100`
- `risingPage`：今天和基线都有，且
  - `today.clicks >= 100`
  - `deltaClicks >= 30`
  - `growthRate >= 20%`

子域名级：
- `newlyObservedSubdomain`：今天有、基线无，且 `observedSubdomainClicks >= 150`
- `risingSubdomain`：今天和基线都有，且
  - `today.observedSubdomainClicks >= 150`
  - `deltaClicks >= 50`（不限制增长率）

## 报告备注（固定输出）

报告中会固定包含以下声明：

1. 当前监控仅覆盖 ClicksShare 排序下前5页样本
2. “新进入样本”不等于全站首次出现
3. 子域名流量是样本内观测值，不代表全站完整总量

## 相关文件

- 外层 skill 入口：`.claude/skills/word-monitor-sub-domain/SKILL.md`
- 内部说明：`word-monitor-sub-domain/_internal/skill/SKILL.md`
- 快照结构：`word-monitor-sub-domain/_internal/docs/SNAPSHOT_SCHEMA.md`
