# standard-word-analysis

用于定义“找词/研究词”流程之间的数据交换层（标准词表）。

## 目标

- 给所有 skill 一个统一可读写的词表契约。
- 让不同 skill 产物可以直接串联（先填关键词，再逐步补列）。
- 保持仓库内 `word-from-root` 与 `word-monitor-sub-domain` 输出格式一致。

## 当前版本

- 版本：`v1`
- 规范文件：`spec/standard-word-table.v1.json`
- 样例数据：`sample/standard-word-table.v1.sample.json`
- 样例表格：`sample/standard-word-table.v1.sample.xlsx`

## v1 列定义（严格顺序）

1. `keyword`
2. `对应域名`
3. `group`
4. `sourcePresence(SIM/SEM)`
5. `score(simWindowVolume*cpc/kd)`
6. `volume(sim)`
7. `kd(sim)`
8. `cpc(sim)`
9. `volume(sem)`
10. `kd(sem)`
11. `cpc(sem)`
12. `gefeiKD`

## 规则说明（v1）

- `score` 公式固定为：`simWindowVolume * simCpc / simKd`
- 当缺失完整 SIM 指标时（任一缺失或 <= 0），`score` 允许为空
- `sourcePresence` 取值：`both` / `sim_only` / `sem_only`
- `对应域名` 用于记录关键词对应的页面/子域名归属；暂时拿不到域名时允许为空
- `gefeiKD` 为哥飞 KD API 返回的 score；查不到时允许为空
- 当前直接覆盖 v1 schema，不保留旧表头兼容层

## 范围声明

- 本版本包含 `gefeiKD` 列
- `word-from-root` 与 `word-monitor-sub-domain` 都应输出同一份 v1 当前表头

## 当前生产方

### word-from-root

`word-from-root` 当前输出对齐本标准（v1）：

- 产物：`word-from-root/report/latest.xlsx`
- 代码入口：`word-from-root/_internal/scripts/word_from_root.py`
- `对应域名` 当前默认留空
- `gefeiKD` 在导出前批量查询补齐

### word-monitor-sub-domain

`word-monitor-sub-domain` 当前也输出本标准（v1）：

- 产物：`word-monitor-sub-domain/report/latest.xlsx`
- 代码入口：`word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py`
- 内容来源：报告中的 `新增` / `上涨` 页面与子域名 top keywords
- 相同 `keyword` 按词去重，仅保留一行
- `对应域名` 聚合该 keyword 命中的全部域名 / 页面上下文
- `gefeiKD` 在导出前批量查询补齐
