# 关键词批量分析报告（20260802-154519）

## 摘要

- 输入关键词数：17
- 成功关键词数：17
- 失败关键词数：0
- SIM 匹配成功数：12
- SIM 未命中数：5
- SIM 请求失败数：0
- 标准词表行数：17
- 有效 score 行数：3

## 抓取概览

- API：http://127.0.0.1:17311/sem/kwogw/v2/webapi/keywords.GetInfo
- SIM API：http://127.0.0.1:17311/sim/api/KeywordGenerator/google/suggest
- SIM 固定参数：rowsPerPage=5, type=Related, sort=score, asc=False
- SIM 默认口径：country=999, latest=28d, webSource=Total, isWindow=True, page=1
- 默认参数：device=0 currency=USD database=us locati0n=0 date=''
- timeoutMs=45000 / waitTimeoutMs=120000 / maxRetries=2

## 聚合结果概览

- totalGlobalVolume（所有关键词汇总）：211200
- avgGlobalCpc（关键词级均值）：1.49
- avgGlobalDifficulty（关键词级均值）：38.50

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| glaze | 169100 | 0.27 | 60 | 116 |
| penpot | 23050 | 2.21 | 56 | 12 |
| ai tools directory | 5660 | 4.59 | 66 | 13 |
| wron | 4340 | 0 | 27 | 50 |
| metaimage | 2910 | 1.26 | 34 | 61 |
| openseo | 2720 | 0 | -<wbr> | 48 |
| fancyai | 1600 | 1.20 | 7 | 12 |
| osaurus | 1190 | 0 | 43 | 39 |
| blunge | 560 | 0 | 15 | 25 |
| acebuilder | 40 | 5.35 | -<wbr> | 8 |
| seedance on higgsfield | 20 | -<wbr> | -<wbr> | 3 |
| docsalot | 10 | -<wbr> | -<wbr> | 1 |
| 2cimub39hmpt5ontf2uhzs | 0 | -<wbr> | -<wbr> | 0 |
| 61uhiqpnlvrx41wa7qgfdc | 0 | -<wbr> | -<wbr> | 0 |
| 7yl97oflfw8lcpod41wu2q | 0 | -<wbr> | -<wbr> | 0 |
| ai video camera control | 0 | -<wbr> | -<wbr> | 2 |
| humalike | 0 | -<wbr> | -<wbr> | 1 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| penpot | both | 2756.660317 | 166990 | 23050 |
| glaze | both | 1170.300000 | 82170 | 169100 |
| ai tools directory | both | 293.601176 | 21330 | 5660 |
| wron | both | -<wbr> | 6790 | 4340 |
| metaimage | both | -<wbr> | 340 | 2910 |
| openseo | both | -<wbr> | 91370 | 2720 |
| fancyai | both | -<wbr> | 4500 | 1600 |
| osaurus | both | -<wbr> | 8460 | 1190 |
| blunge | both | -<wbr> | 420 | 560 |
| acebuilder | both | -<wbr> | 1580 | 40 |
| seedance on higgsfield | sem_<wbr>only | -<wbr> | -<wbr> | 20 |
| docsalot | both | -<wbr> | 740 | 10 |
| humalike | both | -<wbr> | 1610 | 0 |
| 2cimub39hmpt5ontf2uhzs | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| 61uhiqpnlvrx41wa7qgfdc | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| 7yl97oflfw8lcpod41wu2q | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| ai video camera control | sem_<wbr>only | -<wbr> | -<wbr> | 0 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260802-154142/analyze-words/report/history/report-20260802-154519.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260802-154142/analyze-words/report/history/keyword-table-20260802-154519.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260802-154142/analyze-words/report/history/keyword-table-20260802-154519.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
