# 关键词批量分析报告（20260724-143218）

## 摘要

- 输入关键词数：8
- 成功关键词数：8
- 失败关键词数：0
- SIM 匹配成功数：2
- SIM 未命中数：6
- SIM 请求失败数：0
- 标准词表行数：8
- 有效 score 行数：0

## 抓取概览

- API：http://127.0.0.1:17311/sem/kwogw/v2/webapi/keywords.GetInfo
- SIM API：http://127.0.0.1:17311/sim/api/KeywordGenerator/google/suggest
- SIM 固定参数：rowsPerPage=5, type=Related, sort=score, asc=False
- SIM 默认口径：country=999, latest=28d, webSource=Total, isWindow=True, page=1
- 默认参数：device=0 currency=USD database=us locati0n=0 date=''
- timeoutMs=45000 / waitTimeoutMs=120000 / maxRetries=2

## 聚合结果概览

- totalGlobalVolume（所有关键词汇总）：90
- avgGlobalCpc（关键词级均值）：1.61
- avgGlobalDifficulty（关键词级均值）：-

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| free unlimited ai video generation | 80 | 1.61 | -<wbr> | 4 |
| higgsfield after effects | 10 | -<wbr> | -<wbr> | 6 |
| ai batch generation tools | 0 | -<wbr> | -<wbr> | 0 |
| ai product videos no studio | 0 | -<wbr> | -<wbr> | 0 |
| best platforms seedream | 0 | -<wbr> | -<wbr> | 0 |
| higgsfield all unlimited explained | 0 | -<wbr> | -<wbr> | 0 |
| higgsfield figma plugin | 0 | -<wbr> | -<wbr> | 0 |
| most reliable ai video generators | 0 | -<wbr> | -<wbr> | 0 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| free unlimited ai video generation | sem_<wbr>only | -<wbr> | -<wbr> | 80 |
| higgsfield after effects | both | -<wbr> | 890 | 10 |
| higgsfield figma plugin | both | -<wbr> | 20 | 0 |
| ai batch generation tools | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| ai product videos no studio | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| best platforms seedream | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| higgsfield all unlimited explained | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| most reliable ai video generators | sem_<wbr>only | -<wbr> | -<wbr> | 0 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260724-142816/analyze-words/report/history/report-20260724-143218.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260724-142816/analyze-words/report/history/keyword-table-20260724-143218.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260724-142816/analyze-words/report/history/keyword-table-20260724-143218.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
