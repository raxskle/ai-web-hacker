# 关键词批量分析报告（20260802-153201）

## 摘要

- 输入关键词数：18
- 成功关键词数：18
- 失败关键词数：0
- SIM 匹配成功数：17
- SIM 未命中数：1
- SIM 请求失败数：0
- 标准词表行数：18
- 有效 score 行数：1

## 抓取概览

- API：http://127.0.0.1:17311/sem/kwogw/v2/webapi/keywords.GetInfo
- SIM API：http://127.0.0.1:17311/sim/api/KeywordGenerator/google/suggest
- SIM 固定参数：rowsPerPage=5, type=Related, sort=score, asc=False
- SIM 默认口径：country=999, latest=28d, webSource=Total, isWindow=True, page=1
- 默认参数：device=0 currency=USD database=us locati0n=0 date=''
- timeoutMs=45000 / waitTimeoutMs=120000 / maxRetries=2

## 聚合结果概览

- totalGlobalVolume（所有关键词汇总）：17640
- avgGlobalCpc（关键词级均值）：0
- avgGlobalDifficulty（关键词级均值）：33.50

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| mtproto | 14900 | 0 | 45 | 60 |
| tkb sgu | 1320 | 0 | -<wbr> | 2 |
| cng calculator | 1100 | 0 | -<wbr> | 19 |
| mermaid to excalidraw | 270 | 0 | 22 | 6 |
| cult of the lamb editor | 30 | 0 | -<wbr> | 2 |
| message in the bottle vercel | 20 | 0 | -<wbr> | 2 |
| ddw creator | 0 | -<wbr> | -<wbr> | 0 |
| elden ring dresses interactive gallery | 0 | -<wbr> | -<wbr> | 0 |
| genius annotation maker | 0 | -<wbr> | -<wbr> | 1 |
| kagewatch | 0 | -<wbr> | -<wbr> | 0 |
| kalender akademik dan pengumuman lulus ut 2026 | 0 | -<wbr> | -<wbr> | 0 |
| roll color dise | 0 | -<wbr> | -<wbr> | 0 |
| s tier interceptor catalogy | 0 | -<wbr> | -<wbr> | 0 |
| sony e lookmee site de eventos | 0 | -<wbr> | -<wbr> | 0 |
| запуск 1с ras отключает службу сервера 1с на линуксе | 0 | -<wbr> | -<wbr> | 0 |
| калькулятор понлайн по фото | 0 | -<wbr> | -<wbr> | 0 |
| 쌀로아 | 0 | -<wbr> | -<wbr> | 0 |
| 올림픽공원 실시간 | 0 | -<wbr> | -<wbr> | 0 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| mtproto | both | 678.088235 | 230550 | 14900 |
| tkb sgu | both | -<wbr> | 4410 | 1320 |
| cng calculator | both | -<wbr> | 1700 | 1100 |
| mermaid to excalidraw | both | -<wbr> | 2180 | 270 |
| cult of the lamb editor | both | -<wbr> | 1210 | 30 |
| message in the bottle vercel | both | -<wbr> | 460 | 20 |
| elden ring dresses interactive gallery | both | -<wbr> | 3550 | 0 |
| kagewatch | both | -<wbr> | 1820 | 0 |
| sony e lookmee site de eventos | both | -<wbr> | 1700 | 0 |
| genius annotation maker | both | -<wbr> | 840 | 0 |
| kalender akademik dan pengumuman lulus ut 2026 | both | -<wbr> | 780 | 0 |
| s tier interceptor catalogy | both | -<wbr> | 490 | 0 |
| 쌀로아 | both | -<wbr> | 280 | 0 |
| 올림픽공원 실시간 | both | -<wbr> | 260 | 0 |
| ddw creator | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| roll color dise | both | -<wbr> | 0 | 0 |
| запуск 1с ras отключает службу сервера 1с на линуксе | both | -<wbr> | 0 | 0 |
| калькулятор понлайн по фото | both | -<wbr> | 0 | 0 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sub-domain/_internal/chained/20260802-152810/analyze-words/report/history/report-20260802-153201.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sub-domain/_internal/chained/20260802-152810/analyze-words/report/history/keyword-table-20260802-153201.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sub-domain/_internal/chained/20260802-152810/analyze-words/report/history/keyword-table-20260802-153201.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
