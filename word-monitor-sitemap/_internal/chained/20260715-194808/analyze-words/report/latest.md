# 关键词批量分析报告（20260715-195139）

## 摘要

- 输入关键词数：6
- 成功关键词数：6
- 失败关键词数：0
- SIM 匹配成功数：1
- SIM 未命中数：5
- SIM 请求失败数：0
- 标准词表行数：6
- 有效 score 行数：0

## 抓取概览

- API：http://127.0.0.1:17311/sem/kwogw/v2/webapi/keywords.GetInfo
- SIM API：http://127.0.0.1:17311/sim/api/KeywordGenerator/google/suggest
- SIM 固定参数：rowsPerPage=5, type=Related, sort=score, asc=False
- SIM 默认口径：country=999, latest=28d, webSource=Total, isWindow=True, page=1
- 默认参数：device=0 currency=USD database=us locati0n=0 date=''
- timeoutMs=45000 / waitTimeoutMs=120000 / maxRetries=2

## 聚合结果概览

- totalGlobalVolume（所有关键词汇总）：280
- avgGlobalCpc（关键词级均值）：0
- avgGlobalDifficulty（关键词级均值）：-

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| chicken hell | 280 | 0 | -<wbr> | 20 |
| escape from school runaway | 0 | 0 | -<wbr> | 3 |
| craft 4eva | 0 | -<wbr> | -<wbr> | 0 |
| home makeover cleaning game | 0 | -<wbr> | -<wbr> | 0 |
| strange mazes | 0 | -<wbr> | -<wbr> | 1 |
| zombie lab escape | 0 | -<wbr> | -<wbr> | 0 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| chicken hell | sem_<wbr>only | -<wbr> | -<wbr> | 280 |
| zombie lab escape | both | -<wbr> | 430 | 0 |
| craft 4eva | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| escape from school runaway | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| home makeover cleaning game | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| strange mazes | sem_<wbr>only | -<wbr> | -<wbr> | 0 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260715-194808/analyze-words/report/history/report-20260715-195139.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260715-194808/analyze-words/report/history/keyword-table-20260715-195139.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260715-194808/analyze-words/report/history/keyword-table-20260715-195139.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
