# 关键词批量分析报告（20260724-142657）

## 摘要

- 输入关键词数：12
- 成功关键词数：12
- 失败关键词数：0
- SIM 匹配成功数：0
- SIM 未命中数：10
- SIM 请求失败数：2
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

- totalGlobalVolume（所有关键词汇总）：0
- avgGlobalCpc（关键词级均值）：-
- avgGlobalDifficulty（关键词级均值）：-

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| best web hosting companies in raleigh north carolina | 0 | -<wbr> | -<wbr> | 0 |
| best web hosting providers in sweden compared | 0 | -<wbr> | -<wbr> | 0 |
| brand name generators that inspire better business ideas | 0 | -<wbr> | -<wbr> | 0 |
| design platforms that can replace canva for everyday projects | 0 | -<wbr> | -<wbr> | 0 |
| greengeeks black friday deals historical discounts and buying tips | 0 | -<wbr> | -<wbr> | 0 |
| how to choose business card maker that matches your business needs | 0 | -<wbr> | -<wbr> | 0 |
| online logo makers that help build strong brand identity | 0 | -<wbr> | -<wbr> | 0 |
| pantheon wordpress hosting performance benchmarks speed caching and scalability | 0 | -<wbr> | -<wbr> | 0 |
| tatango and wordpress hosting evaluating compatibility and performance | 0 | -<wbr> | -<wbr> | 0 |
| top outsourced affiliate program management agencies | 0 | -<wbr> | -<wbr> | 0 |
| unblur image apps compared which one restores details best | 0 | -<wbr> | -<wbr> | 0 |
| vacation spots that combine fine dining live shows and luxury hotels | 0 | -<wbr> | -<wbr> | 0 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| best web hosting companies in raleigh north carolina | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| best web hosting providers in sweden compared | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| brand name generators that inspire better business ideas | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| design platforms that can replace canva for everyday projects | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| greengeeks black friday deals historical discounts and buying tips | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| how to choose business card maker that matches your business needs | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| online logo makers that help build strong brand identity | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| pantheon wordpress hosting performance benchmarks speed caching and scalability | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| tatango and wordpress hosting evaluating compatibility and performance | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| top outsourced affiliate program management agencies | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| unblur image apps compared which one restores details best | sem_<wbr>only | -<wbr> | -<wbr> | 0 |
| vacation spots that combine fine dining live shows and luxury hotels | sem_<wbr>only | -<wbr> | -<wbr> | 0 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260724-142535/analyze-words/report/history/report-20260724-142657.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260724-142535/analyze-words/report/history/keyword-table-20260724-142657.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sitemap/_internal/chained/20260724-142535/analyze-words/report/history/keyword-table-20260724-142657.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
