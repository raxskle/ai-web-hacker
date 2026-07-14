# 关键词批量分析报告（20260713-213559）

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

- totalGlobalVolume（所有关键词汇总）：20140
- avgGlobalCpc（关键词级均值）：0.05
- avgGlobalDifficulty（关键词级均值）：45.50

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| om nom run | 12830 | 0.10 | 59 | 30 |
| jelly run | 7300 | 0.04 | 32 | 37 |
| divine clash | 10 | -<wbr> | -<wbr> | 2 |
| orecrusher | 0 | 0 | -<wbr> | 2 |
| alphablitz wty | 0 | -<wbr> | -<wbr> | 0 |
| farm mayhem merge | 0 | -<wbr> | -<wbr> | 0 |
| lafufu blind box dress up | 0 | -<wbr> | -<wbr> | 0 |
| panic patrol | 0 | -<wbr> | -<wbr> | 2 |
| recoil rumble knp | 0 | -<wbr> | -<wbr> | 0 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| om nom run | both | 64.400000 | 13570 | 12830 |
| jelly run | both | 36.625926 | 6380 | 7300 |
| divine clash | both | -<wbr> | 1330 | 10 |
| alphablitz wty | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| farm mayhem merge | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| lafufu blind box dress up | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| orecrusher | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| panic patrol | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| recoil rumble knp | sem_<wbr>only | -<wbr> | -<wbr> | 0 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260713-213155/analyze-words/report/history/report-20260713-213559.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260713-213155/analyze-words/report/history/keyword-table-20260713-213559.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260713-213155/analyze-words/report/history/keyword-table-20260713-213559.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
