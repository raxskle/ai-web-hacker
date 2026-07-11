# 关键词批量分析报告（20260711-160340）

## 摘要

- 输入关键词数：9
- 成功关键词数：9
- 失败关键词数：0
- SIM 匹配成功数：3
- SIM 未命中数：6
- SIM 请求失败数：0
- 标准词表行数：9
- 有效 score 行数：2

## 抓取概览

- API：http://127.0.0.1:17311/sem/kwogw/v2/webapi/keywords.GetInfo
- SIM API：http://127.0.0.1:17311/sim/api/KeywordGenerator/google/suggest
- SIM 固定参数：rowsPerPage=5, type=Related, sort=score, asc=False
- SIM 默认口径：country=999, latest=28d, webSource=Total, isWindow=True, page=1
- 默认参数：device=0 currency=USD database=us locati0n=0 date=''
- timeoutMs=45000 / waitTimeoutMs=120000 / maxRetries=2

## 聚合结果概览

- totalGlobalVolume（所有关键词汇总）：1441680
- avgGlobalCpc（关键词级均值）：1.58
- avgGlobalDifficulty（关键词级均值）：61.50

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| green | 1257960 | 4.74 | 47 | 121 |
| unscrambled | 183690 | 0.01 | 76 | 120 |
| dd 2k shoot | 30 | 0 | -<wbr> | 4 |
| backrooms recovery | 0 | -<wbr> | -<wbr> | 0 |
| block sort jigsaw puzzle journey | 0 | -<wbr> | -<wbr> | 0 |
| downhill racer bvk | 0 | -<wbr> | -<wbr> | 0 |
| nightfall survivors imo | 0 | -<wbr> | -<wbr> | 0 |
| pixel world uyv | 0 | -<wbr> | -<wbr> | 0 |
| the flowers merge and sell bouquets | 0 | -<wbr> | -<wbr> | 0 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| green | both | 54518.094000 | 833610 | 1257960 |
| unscrambled | both | 36.685106 | 4660 | 183690 |
| dd 2k shoot | sem_<wbr>only | -<wbr> | -<wbr> | 30 |
| backrooms recovery | both | -<wbr> | 1260 | 0 |
| block sort jigsaw puzzle journey | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| downhill racer bvk | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| nightfall survivors imo | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| pixel world uyv | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| the flowers merge and sell bouquets | sem_<wbr>only | -<wbr> | -<wbr> | 0 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260711-160008/analyze-words/report/history/report-20260711-160340.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260711-160008/analyze-words/report/history/keyword-table-20260711-160340.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260711-160008/analyze-words/report/history/keyword-table-20260711-160340.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
