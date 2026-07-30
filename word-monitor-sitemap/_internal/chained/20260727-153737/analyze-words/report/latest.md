# 关键词批量分析报告（20260727-153941）

## 摘要

- 输入关键词数：17
- 成功关键词数：17
- 失败关键词数：0
- SIM 匹配成功数：7
- SIM 未命中数：10
- SIM 请求失败数：0
- 标准词表行数：17
- 有效 score 行数：5

## 抓取概览

- API：http://127.0.0.1:17311/sem/kwogw/v2/webapi/keywords.GetInfo
- SIM API：http://127.0.0.1:17311/sim/api/KeywordGenerator/google/suggest
- SIM 固定参数：rowsPerPage=5, type=Related, sort=score, asc=False
- SIM 默认口径：country=999, latest=28d, webSource=Total, isWindow=True, page=1
- 默认参数：device=0 currency=USD database=us locati0n=0 date=''
- timeoutMs=45000 / waitTimeoutMs=120000 / maxRetries=2

## 聚合结果概览

- totalGlobalVolume（所有关键词汇总）：183290
- avgGlobalCpc（关键词级均值）：2.36
- avgGlobalDifficulty（关键词级均值）：44

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| ai models | 74650 | 3.22 | 69 | 69 |
| ai answer | 40430 | 1.22 | 70 | 30 |
| image to 3d model | 33220 | 1.31 | 34 | 80 |
| speechnotes | 32760 | 1.58 | 33 | 101 |
| image2image | 840 | 0.93 | 19 | 28 |
| getimgai | 660 | 0.99 | 44 | 11 |
| ai ad creative | 420 | 9.77 | 39 | 12 |
| muryou aigazou | 310 | -<wbr> | -<wbr> | 4 |
| elev ai | 0 | 2.20 | -<wbr> | 11 |
| removevideobg | 0 | 0 | -<wbr> | 3 |
| agentgeo | 0 | -<wbr> | -<wbr> | 4 |
| aitoolslist tools | 0 | -<wbr> | -<wbr> | 0 |
| caret se | 0 | -<wbr> | -<wbr> | 0 |
| flux3 video | 0 | -<wbr> | -<wbr> | 0 |
| fortunetelleronline | 0 | -<wbr> | -<wbr> | 0 |
| imgvid | 0 | -<wbr> | -<wbr> | 1 |
| pixellisting | 0 | -<wbr> | -<wbr> | 0 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| ai models | both | 1487.400000 | 50250 | 74650 |
| image2image | both | 1011.333333 | 1850 | 840 |
| image to 3d model | both | 721.107692 | 41850 | 33220 |
| speechnotes | both | 126.941772 | 16440 | 32760 |
| ai answer | both | 84.175325 | 4470 | 40430 |
| getimgai | sem_<wbr>only | -<wbr> | -<wbr> | 660 |
| ai ad creative | both | -<wbr> | 930 | 420 |
| muryou aigazou | sem_<wbr>only | -<wbr> | -<wbr> | 310 |
| agentgeo | both | -<wbr> | 110 | 0 |
| aitoolslist tools | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| caret se | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| elev ai | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| flux3 video | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| fortunetelleronline | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| imgvid | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| pixellisting | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| removevideobg | sem_<wbr>only | -<wbr> | -<wbr> | 0 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260727-153737/analyze-words/report/history/report-20260727-153941.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260727-153737/analyze-words/report/history/keyword-table-20260727-153941.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260727-153737/analyze-words/report/history/keyword-table-20260727-153941.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
