# 关键词批量分析报告（20260714-115446）

## 摘要

- 输入关键词数：5
- 成功关键词数：5
- 失败关键词数：0
- SIM 匹配成功数：4
- SIM 未命中数：1
- SIM 请求失败数：0
- 标准词表行数：5
- 有效 score 行数：1

## 抓取概览

- API：http://127.0.0.1:17311/sem/kwogw/v2/webapi/keywords.GetInfo
- SIM API：http://127.0.0.1:17311/sim/api/KeywordGenerator/google/suggest
- SIM 固定参数：rowsPerPage=5, type=Related, sort=score, asc=False
- SIM 默认口径：country=999, latest=28d, webSource=Total, isWindow=True, page=1
- 默认参数：device=0 currency=USD database=us locati0n=0 date=''
- timeoutMs=45000 / waitTimeoutMs=120000 / maxRetries=2

## 聚合结果概览

- totalGlobalVolume（所有关键词汇总）：12140
- avgGlobalCpc（关键词级均值）：0.25
- avgGlobalDifficulty（关键词级均值）：27.33

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| voxiom io | 11400 | 0 | 39 | 14 |
| noob archer | 500 | 0.11 | 14 | 13 |
| merge clash | 150 | 1.14 | 29 | 4 |
| fishing anomaly | 50 | 0 | -<wbr> | 6 |
| digworm io | 40 | 0 | -<wbr> | 3 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| voxiom io | both | 339.281250 | 9870 | 11400 |
| noob archer | both | -<wbr> | 120 | 500 |
| merge clash | both | -<wbr> | 1570 | 150 |
| fishing anomaly | sem_<wbr>only | -<wbr> | -<wbr> | 50 |
| digworm io | both | -<wbr> | 450 | 40 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260714-115015/analyze-words/report/history/report-20260714-115446.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260714-115015/analyze-words/report/history/keyword-table-20260714-115446.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260714-115015/analyze-words/report/history/keyword-table-20260714-115446.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
