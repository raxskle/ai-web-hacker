# 关键词批量分析报告（20260730-140820）

## 摘要

- 输入关键词数：20
- 成功关键词数：20
- 失败关键词数：0
- SIM 匹配成功数：3
- SIM 未命中数：16
- SIM 请求失败数：1
- 标准词表行数：20
- 有效 score 行数：1

## 抓取概览

- API：http://127.0.0.1:17311/sem/kwogw/v2/webapi/keywords.GetInfo
- SIM API：http://127.0.0.1:17311/sim/api/KeywordGenerator/google/suggest
- SIM 固定参数：rowsPerPage=5, type=Related, sort=score, asc=False
- SIM 默认口径：country=999, latest=28d, webSource=Total, isWindow=True, page=1
- 默认参数：device=0 currency=USD database=us locati0n=0 date=''
- timeoutMs=45000 / waitTimeoutMs=120000 / maxRetries=2

## 聚合结果概览

- totalGlobalVolume（所有关键词汇总）：34980
- avgGlobalCpc（关键词级均值）：3.96
- avgGlobalDifficulty（关键词级均值）：44.75

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| railway bridge | 26650 | 0 | 43 | 85 |
| dogs out | 6900 | 0.73 | 49 | 77 |
| demolition inc | 750 | 0 | 32 | 45 |
| ai ad agency | 540 | 11.10 | 55 | 12 |
| 20f8 | 110 | 0 | -<wbr> | 13 |
| best ai ad generators | 30 | 11.94 | -<wbr> | 8 |
| count and bounce bls | 0 | -<wbr> | -<wbr> | 0 |
| draw one line drawing puzzle | 0 | -<wbr> | -<wbr> | 0 |
| furriq | 0 | -<wbr> | -<wbr> | 0 |
| healthcare care management platforms for hospitals payers and community care organizations | 0 | -<wbr> | -<wbr> | 0 |
| how alltegrios voice ai agent streamlined insurance support | 0 | -<wbr> | -<wbr> | 0 |
| how to offer payment flexibility without hurting your brand | 0 | -<wbr> | -<wbr> | 0 |
| idle dairy tycoon | 0 | -<wbr> | -<wbr> | 0 |
| krea2turbo pro | 0 | -<wbr> | -<wbr> | 0 |
| merge haven fzh | 0 | -<wbr> | -<wbr> | 0 |
| road rage hva | 0 | -<wbr> | -<wbr> | 0 |
| robshoot | 0 | -<wbr> | -<wbr> | 0 |
| scale labs and paypal what the partnership means | 0 | -<wbr> | -<wbr> | 0 |
| squarespace vs shopify for paypal payments | 0 | -<wbr> | -<wbr> | 0 |
| unlimited mcp | 0 | -<wbr> | -<wbr> | 0 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| dogs out | both | 2.610526 | 40 | 6900 |
| railway bridge | both | -<wbr> | 3610 | 26650 |
| demolition inc | sem_<wbr>only | -<wbr> | -<wbr> | 750 |
| ai ad agency | both | -<wbr> | 70 | 540 |
| 20f8 | sem_<wbr>only | -<wbr> | -<wbr> | 110 |
| best ai ad generators | sem_<wbr>only | -<wbr> | -<wbr> | 30 |
| count and bounce bls | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| draw one line drawing puzzle | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| furriq | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| healthcare care management platforms for hospitals payers and community care organizations | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| how alltegrios voice ai agent streamlined insurance support | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| how to offer payment flexibility without hurting your brand | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| idle dairy tycoon | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| krea2turbo pro | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| merge haven fzh | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| road rage hva | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| robshoot | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| scale labs and paypal what the partnership means | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| squarespace vs shopify for paypal payments | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| unlimited mcp | sem_<wbr>only | -<wbr> | -<wbr> | 0 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260730-140234/analyze-words/report/history/report-20260730-140820.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260730-140234/analyze-words/report/history/keyword-table-20260730-140820.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260730-140234/analyze-words/report/history/keyword-table-20260730-140820.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
