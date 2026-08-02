# 关键词批量分析报告（20260801-154947）

## 摘要

- 输入关键词数：13
- 成功关键词数：13
- 失败关键词数：0
- SIM 匹配成功数：6
- SIM 未命中数：7
- SIM 请求失败数：0
- 标准词表行数：13
- 有效 score 行数：4

## 抓取概览

- API：http://127.0.0.1:17311/sem/kwogw/v2/webapi/keywords.GetInfo
- SIM API：http://127.0.0.1:17311/sim/api/KeywordGenerator/google/suggest
- SIM 固定参数：rowsPerPage=5, type=Related, sort=score, asc=False
- SIM 默认口径：country=999, latest=28d, webSource=Total, isWindow=True, page=1
- 默认参数：device=0 currency=USD database=us locati0n=0 date=''
- timeoutMs=45000 / waitTimeoutMs=120000 / maxRetries=2

## 聚合结果概览

- totalGlobalVolume（所有关键词汇总）：130380
- avgGlobalCpc（关键词级均值）：0.70
- avgGlobalDifficulty（关键词级均值）：45.80

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| seedance | 106180 | 1.48 | 78 | 15 |
| swat cats | 16940 | 0 | 39 | 70 |
| hexa stack | 4360 | 0.63 | 39 | 13 |
| perfect shape | 2260 | 2.04 | 34 | 73 |
| robynn | 590 | 0 | 39 | 21 |
| videotto | 50 | 0.03 | -<wbr> | 6 |
| ai presentation makers compared which one fits your workflow best | 0 | -<wbr> | -<wbr> | 0 |
| ai short film pipeline | 0 | -<wbr> | -<wbr> | 0 |
| flip pounce | 0 | -<wbr> | -<wbr> | 0 |
| how ai powered promotions help merchants increase sales | 0 | -<wbr> | -<wbr> | 0 |
| pananto platform review features benefits and alternatives | 0 | -<wbr> | -<wbr> | 0 |
| seedance unlimited days | 0 | -<wbr> | -<wbr> | 0 |
| top salesforce apps that improve sales and productivity | 0 | -<wbr> | -<wbr> | 0 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| seedance | both | 17532.546875 | 1181140 | 106180 |
| swat cats | both | 509.040000 | 2520 | 16940 |
| videotto | both | 128.252542 | 22930 | 50 |
| hexa stack | both | 69.575410 | 3010 | 4360 |
| perfect shape | both | -<wbr> | 1520 | 2260 |
| robynn | both | -<wbr> | 140 | 590 |
| ai presentation makers compared which one fits your workflow best | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| ai short film pipeline | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| flip pounce | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| how ai powered promotions help merchants increase sales | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| pananto platform review features benefits and alternatives | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| seedance unlimited days | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| top salesforce apps that improve sales and productivity | sem_<wbr>only | -<wbr> | -<wbr> | 0 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260801-154641/analyze-words/report/history/report-20260801-154947.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260801-154641/analyze-words/report/history/keyword-table-20260801-154947.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260801-154641/analyze-words/report/history/keyword-table-20260801-154947.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
