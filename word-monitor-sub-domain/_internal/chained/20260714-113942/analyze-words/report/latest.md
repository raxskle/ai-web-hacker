# 关键词批量分析报告（20260714-114720）

## 摘要

- 输入关键词数：21
- 成功关键词数：21
- 失败关键词数：0
- SIM 匹配成功数：20
- SIM 未命中数：1
- SIM 请求失败数：0
- 标准词表行数：21
- 有效 score 行数：1

## 抓取概览

- API：http://127.0.0.1:17311/sem/kwogw/v2/webapi/keywords.GetInfo
- SIM API：http://127.0.0.1:17311/sim/api/KeywordGenerator/google/suggest
- SIM 固定参数：rowsPerPage=5, type=Related, sort=score, asc=False
- SIM 默认口径：country=999, latest=28d, webSource=Total, isWindow=True, page=1
- 默认参数：device=0 currency=USD database=us locati0n=0 date=''
- timeoutMs=45000 / waitTimeoutMs=120000 / maxRetries=2

## 聚合结果概览

- totalGlobalVolume（所有关键词汇总）：377080
- avgGlobalCpc（关键词级均值）：0
- avgGlobalDifficulty（关键词级均值）：21

## 关键词结果预览

| keyword | globalVolume | globalCpcAvg | globalDifficultyAvg | databaseCount |
| --- | --- | --- | --- | --- |
| lion parcel | 373780 | 0 | 30 | 31 |
| kcd interactive map | 1400 | 0 | 12 | 25 |
| hero siege items | 450 | 0 | -<wbr> | 25 |
| угадай цвет персонажа | 430 | -<wbr> | -<wbr> | 2 |
| suite tv | 410 | 0 | -<wbr> | 31 |
| 12 word phrase generator | 230 | 0 | -<wbr> | 17 |
| butterstream | 210 | 0 | -<wbr> | 4 |
| letterboxd top 4 match | 90 | 0 | -<wbr> | 1 |
| what dbd killer should i play | 80 | 0 | -<wbr> | 4 |
| fe engage calc | 0 | 0 | -<wbr> | 7 |
| dsa algorithm visualization | 0 | -<wbr> | -<wbr> | 1 |
| fc26 sbc free chrome extension | 0 | -<wbr> | -<wbr> | 0 |
| glow nails babelsberg | 0 | -<wbr> | -<wbr> | 0 |
| leetify-<wbr>dun | 0 | -<wbr> | -<wbr> | 0 |
| russia virtual sms sim only | 0 | -<wbr> | -<wbr> | 0 |
| sberbank.com/<wbr>sms/<wbr>pay | 0 | -<wbr> | -<wbr> | 0 |
| yakithesapla.net | 0 | -<wbr> | -<wbr> | 0 |
| какое напряжение в кулере ноутбука асер | 0 | -<wbr> | -<wbr> | 0 |
| кредитка от альфа банка как работает беспроцентный период | 0 | -<wbr> | -<wbr> | 0 |
| нейрохам онлайн | 0 | -<wbr> | -<wbr> | 0 |
| 스마트스테이션 드라이버 | 0 | -<wbr> | -<wbr> | 0 |

## 标准词表预览

| keyword | sourcePresence | score(sim) | volume(sim) | volume(sem) |
| --- | --- | --- | --- | --- |
| lion parcel | both | 393.904110 | 191700 | 373780 |
| kcd interactive map | both | -<wbr> | 2110 | 1400 |
| hero siege items | both | -<wbr> | 1140 | 450 |
| угадай цвет персонажа | both | -<wbr> | 10490 | 430 |
| suite tv | both | -<wbr> | 15130 | 410 |
| 12 word phrase generator | both | -<wbr> | 0 | 230 |
| butterstream | both | -<wbr> | 14470 | 210 |
| letterboxd top 4 match | both | -<wbr> | 2680 | 90 |
| what dbd killer should i play | both | -<wbr> | 710 | 80 |
| leetify-<wbr>dun | both | -<wbr> | 2680 | 0 |
| yakithesapla.net | both | -<wbr> | 1320 | 0 |
| fe engage calc | both | -<wbr> | 1060 | 0 |
| dsa algorithm visualization | both | -<wbr> | 610 | 0 |
| fc26 sbc free chrome extension | both | -<wbr> | 520 | 0 |
| glow nails babelsberg | both | -<wbr> | 490 | 0 |
| нейрохам онлайн | both | -<wbr> | 90 | 0 |
| russia virtual sms sim only | both | -<wbr> | 0 | 0 |
| sberbank.com/<wbr>sms/<wbr>pay | both | -<wbr> | 0 | 0 |
| какое напряжение в кулере ноутбука асер | both | -<wbr> | 0 | 0 |
| кредитка от альфа банка как работает беспроцентный период | both | -<wbr> | 0 | 0 |
| 스마트스테이션 드라이버 | sem_<wbr>only | -<wbr> | -<wbr> | 0 |

## 失败关键词

（无）

## 产物路径

- Markdown：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sub-domain/_internal/chained/20260714-113942/analyze-words/report/history/report-20260714-114720.md
- Excel：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sub-domain/_internal/chained/20260714-113942/analyze-words/report/history/keyword-table-20260714-114720.xlsx
- JSON：/Users/bytedance/work/raxskle/sitte/ai/word-monitor-sub-domain/_internal/chained/20260714-113942/analyze-words/report/history/keyword-table-20260714-114720.json

## 备注

- globalVolume = sum(volume)
- globalCpcAvg / globalDifficultyAvg 仅统计非 null 项
- 标准词表 score 仅由 SIM 字段计算：simWindowVolume * simCpc / simKd
- SIM Suggest 使用 rowsPerPage=5、type=Related、sort=score、asc=false（其它参数走默认口径）
- SIM 请求失败或未命中对应关键词时：继续执行并将 SIM 字段置空
- 任一关键词 SEM 抓取失败时默认整次失败，不落任何新产物
