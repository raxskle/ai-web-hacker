---
name: word-from-root
version: 0.2.2
description: "基于词根抓取 SIM/SEM 相关关键词，先做分源 AI 近义合并，再通过 check-gefei-kd（默认前50词）回填 gefeiKD 并导出标准词表 Excel。"
---

# word-from-root（MVP）

用于执行一次按词根扩词的完整流程：

1. 调用 SIM Suggest 第 1 页，读取 `totalRecords`
2. 继续抓取剩余页，最多累计 300 词
3. 调用 SEM Summary 获取 `total`
4. 分页调用 SEM Keywords，最多累计 300 词
5. 标准化两路结果
6. 分别对 SIM / SEM 做 AI 近义分组
7. 计算组内聚合（volume 求和、CPC/KD volume 加权）
8. 按分组后的结果做跨源 merge 与排序
9. 先写入基础快照、Markdown 报告、标准词表 Excel
10. 调用 `check-gefei-kd`（默认仅前 50 个标准词）回填 `gefeiKD`
11. 重写最终 Markdown / Excel，并发布到 `words/root-[关键词根]-[time].xlsx`

## 执行方式

```bash
python3 word-from-root/_internal/scripts/word_from_root.py run --keyword "image to text"
python3 word-from-root/_internal/scripts/word_from_root.py rebuild-reports
python3 word-from-root/_internal/scripts/word_from_root.py validate-report
```

## 后置 KD 参数

```bash
python3 word-from-root/_internal/scripts/word_from_root.py run \
  --keyword "image to text" \
  --gefei-kd-max-keywords 50 \
  --words-dir "$(pwd)/words" \
  --chain-work-dir "word-from-root/_internal/chained"
```

- `--gefei-kd-max-keywords`：后置 `check-gefei-kd` 最多分析词数（默认 50；0 表示不限制）
- `--words-dir`：最终 xlsx 发布目录（默认仓库根 `words/`）
- `--chain-work-dir`：后置 stage 产物目录（默认 `word-from-root/_internal/chained/`）

## 输入/输出

- 本地服务文档：`word-from-root/local-service/API_REFERENCE.md`
- token 文件：`word-from-root/local-service/bridge_token.txt`
- gmitm 文件：`word-from-root/local-service/__gmitm.txt`
- 抓取归档：`word-from-root/data/fetch-YYYYMMDD-HHMMSS.json`
- 标准化快照：`word-from-root/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 分组缓存：`word-from-root/_internal/grouping-cache/`
- 历史报告：`word-from-root/report/history/report-YYYYMMDD-HHMMSS.md`
- 历史 Excel：`word-from-root/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx`
- 最新报告：`word-from-root/report/latest.md`
- 最新 Excel：`word-from-root/report/latest.xlsx`
- 后置 stage 目录：`word-from-root/_internal/chained/<stamp>/check-gefei-kd/`
- words 发布：`words/root-[关键词根]-[YYYYMMDD-HHMMSS].xlsx`

## 标准词表契约（v1）

- 规范：`standard-word-analysis/spec/standard-word-table.v1.json`
- 当前导出 Excel 的 `keywords` sheet 严格对齐该契约
- v1 `keywords` sheet 列顺序：`keyword -> 对应域名 -> score -> volume(sim) -> kd(sim) -> cpc(sim) -> volume(sem) -> kd(sem) -> cpc(sem) -> gefeiKD -> group -> sourcePresence(SIM/SEM)`
- `word-from-root` 当前 `对应域名` 默认留空
- score 公式固定：`simWindowVolume * simCpc / simKd`
- `gefeiKD` 为后置 `check-gefei-kd` 回填结果（默认仅前 50 词参与分析）
- Excel 数值列（`score/sim*/sem*/gefeiKD`）按数字类型写入，避免“数字存为文本”
- `keywords` 数据区配色：SIM 列浅蓝、SEM 列浅紫

## 固定规则（MVP）

- SIM 默认：`latest=28d`、`country=999`、`sort=windowVolume`、`rowsPerPage=100`
- SIM 过滤：`rangeFilter=cpc,0.1,|difficulty,1,70`
- SEM 默认：`database=us`、`currency=USD`、`page.size=100`
- SEM 过滤：`cpc > 0.1`、`difficulty < 70`
- 分源近义合并：词序变化、空格/`-`、单复数、无意义重复
- 排序值只使用 SIM 指标：`simWindowVolume * simCpc / simKd`
- 若缺失完整 SIM 指标，则 `score` 为空并排在已评分结果之后
- `gefeiKD` 只作为补充字段，不参与排序
- Excel 的 `group` 列记录组内原词

## 失败策略

- token / gmitm 缺失：整次失败，不落任何新产物
- 任一 API 请求失败：整次失败，不落任何新产物
- 任一 AI 分组失败：整次失败，不落任何新产物
- 哥飞 KD 认证/全局额度错误：整次失败，不落任何新产物
- 单关键词哥飞 KD 查询失败：该行 `gefeiKD` 留空，并写入 snapshot 失败明细
- `rebuild-reports` 仅依赖 snapshot，不重新请求 API，不重新执行 AI 分组，不重新查询哥飞 KD
