# 关键词批量分析报告（20260716-133031）

## 摘要

- 输入关键词数：12
- 成功关键词数：12
- 失败关键词数：0
- SIM 匹配成功数：2
- SIM 未命中数：10
- SIM 请求失败数：0
- 标准词表行数：12
- 有效 score 行数：0

## 抓取概览

- API：http://127.0.0.1:17311/sem/kwogw/v2/webapi/keywords.GetInfo
- SIM API：http://127.0.0.1:17311/sim/api/KeywordGenerator/google/suggest
- SIM 固定参数：rowsPerPage=5, type=Related, sort=score, asc=False
- SIM 默认口径：country=999, latest=28d, webSource=Total, isWindow=True, page=1
- 默认参数：device=0 currency=USD database=us locati0n=0 date=''
- timeoutMs=45000 / waitTimeoutMs=120000 / maxRetries=2

## 聚合结果概览

- totalGlobalVolume（所有关键词汇总）：880
- avgGlobalCpc（关键词级均值）：0.25
- avgGlobalDifficulty（关键词级均值）：-

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| smashing bottles | 600 | 0.50 | -<wbr> | 35 |
| chicken hell | 280 | 0 | -<wbr> | 20 |
| ai video from text and url | 0 | -<wbr> | -<wbr> | 0 |
| carrom stars io | 0 | -<wbr> | -<wbr> | 0 |
| cinema studio full tutorial | 0 | -<wbr> | -<wbr> | 0 |
| drone delivery chaos fkw | 0 | -<wbr> | -<wbr> | 0 |
| how to play lows adventures | 0 | -<wbr> | -<wbr> | 0 |
| idle car service tycoon | 0 | -<wbr> | -<wbr> | 0 |
| one of one studio interview | 0 | -<wbr> | -<wbr> | 0 |
| sandbox of elements | 0 | -<wbr> | -<wbr> | 0 |
| waddle quest | 0 | -<wbr> | -<wbr> | 0 |
| whatisthismovie | 0 | -<wbr> | -<wbr> | 3 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| smashing bottles | both | -<wbr> | 30 | 600 |
| chicken hell | sem_<wbr>only | -<wbr> | -<wbr> | 280 |
| ai video from text and url | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| carrom stars io | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| cinema studio full tutorial | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| drone delivery chaos fkw | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| how to play lows adventures | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| idle car service tycoon | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| one of one studio interview | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| sandbox of elements | both | -<wbr> | 0 | 0 |
| waddle quest | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| whatisthismovie | sem_<wbr>only | -<wbr> | -<wbr> | 0 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260716-130315/analyze-words/report/history/report-20260716-133031.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260716-130315/analyze-words/report/history/keyword-table-20260716-133031.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260716-130315/analyze-words/report/history/keyword-table-20260716-133031.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
