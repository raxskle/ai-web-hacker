# 关键词批量分析报告（20260724-142450）

## 摘要

- 输入关键词数：7
- 成功关键词数：7
- 失败关键词数：0
- SIM 匹配成功数：2
- SIM 未命中数：5
- SIM 请求失败数：0
- 标准词表行数：7
- 有效 score 行数：2

## 抓取概览

- API：http://127.0.0.1:17311/sem/kwogw/v2/webapi/keywords.GetInfo
- SIM API：http://127.0.0.1:17311/sim/api/KeywordGenerator/google/suggest
- SIM 固定参数：rowsPerPage=5, type=Related, sort=score, asc=False
- SIM 默认口径：country=999, latest=28d, webSource=Total, isWindow=True, page=1
- 默认参数：device=0 currency=USD database=us locati0n=0 date=''
- timeoutMs=45000 / waitTimeoutMs=120000 / maxRetries=2

## 聚合结果概览

- totalGlobalVolume（所有关键词汇总）：89830
- avgGlobalCpc（关键词级均值）：0.92
- avgGlobalDifficulty（关键词级均值）：41

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| clean house | 37960 | 4.19 | 59 | 94 |
| steal brainrot | 28540 | 0.23 | 56 | 13 |
| chick flix | 23030 | 0.05 | 26 | 118 |
| stickman fight ragdoll | 300 | 0.12 | 23 | 10 |
| cuboy adventure | 0 | 0 | -<wbr> | 1 |
| boomy world | 0 | -<wbr> | -<wbr> | 0 |
| fashion fix studio | 0 | -<wbr> | -<wbr> | 0 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| clean house | both | 1661.997436 | 8990 | 37960 |
| steal brainrot | both | 33.237931 | 5670 | 28540 |
| chick flix | sem_<wbr>only | -<wbr> | -<wbr> | 23030 |
| stickman fight ragdoll | sem_<wbr>only | -<wbr> | -<wbr> | 300 |
| boomy world | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| cuboy adventure | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| fashion fix studio | sem_<wbr>only | -<wbr> | -<wbr> | 0 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260724-142350/analyze-words/report/history/report-20260724-142450.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260724-142350/analyze-words/report/history/keyword-table-20260724-142450.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260724-142350/analyze-words/report/history/keyword-table-20260724-142450.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
