---
name: word-from-root
version: 0.2.2
description: "输入一个词根，调用 SIM Suggest 与 SEM Keyword Magic，先做分源 AI 近义合并，再通过 check-gefei-kd（默认前50词）回填 gefeiKD 并导出标准词表 Excel。"
---

# word-from-root

根据你提供的词根，抓取两路关键词数据：

1. SIM：`/sim/api/KeywordGenerator/google/suggest`
2. SEM：`ideas.GetKeywordsSummary` + `ideas.GetKeywords`

然后按以下顺序处理：

1. 标准化关键词
2. 分别对 SIM / SEM 进行 AI 近义分组（词序、空格/`-`、单复数、无意义重复）
3. 在分组结果基础上做跨源合并
4. 先生成基础 Markdown 与标准词表 Excel
5. 调用 `check-gefei-kd` 对标准词表做后置分析（默认最多前 50 词）
6. 回填最终 `gefeiKD`，重写最终 Markdown / Excel
7. 将最终 xlsx 额外同步到仓库根目录 `words/root-[关键词根]-[time].xlsx`

## 执行方式

```bash
python3 word-from-root/_internal/scripts/word_from_root.py run --keyword "image to text"
```

可选命令：

```bash
# 基于快照重建 Markdown / Excel
python3 word-from-root/_internal/scripts/word_from_root.py rebuild-reports

# 校验 latest.md 与 latest.xlsx
python3 word-from-root/_internal/scripts/word_from_root.py validate-report
```

## 常用参数

```bash
python3 word-from-root/_internal/scripts/word_from_root.py run \
  --keyword "image to text" \
  --grouping-model "" \
  --grouping-temperature 0 \
  --grouping-timeout-seconds 120 \
  --gefei-kd-max-keywords 50 \
  --words-dir "$(pwd)/words" \
  --chain-work-dir "word-from-root/_internal/chained"
```

## 输入输出

- 本地服务文档：`word-from-root/local-service/API_REFERENCE.md`
- token 文件：`word-from-root/local-service/bridge_token.txt`
- gmitm 文件：`word-from-root/local-service/__gmitm.txt`
- 抓取归档：`word-from-root/data/fetch-YYYYMMDD-HHMMSS.json`
- 快照归档：`word-from-root/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 分组缓存：`word-from-root/_internal/grouping-cache/`
- 后置 stage：`word-from-root/_internal/chained/<stamp>/check-gefei-kd/`
- 历史 Markdown：`word-from-root/report/history/report-YYYYMMDD-HHMMSS.md`
- 历史 Excel：`word-from-root/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx`
- 最新 Markdown：`word-from-root/report/latest.md`
- 最新 Excel：`word-from-root/report/latest.xlsx`
- words 发布：`words/root-[关键词根]-[YYYYMMDD-HHMMSS].xlsx`

## 标准词表契约（v1）

- 规范：`standard-word-analysis/spec/standard-word-table.v1.json`
- 当前导出 Excel 与该契约严格对齐
- v1 `keywords` sheet 列顺序：`keyword -> 对应域名 -> score -> volume(sim) -> kd(sim) -> cpc(sim) -> volume(sem) -> kd(sem) -> cpc(sem) -> gefeiKD -> group -> sourcePresence(SIM/SEM)`
- `word-from-root` 当前 `对应域名` 默认留空
- 排序公式：`simWindowVolume * simCpc / simKd`
- `gefeiKD` 为后置 `check-gefei-kd` 回填结果（默认仅前 50 词参与分析）
- Excel 数值列（`score/sim*/sem*/gefeiKD`）按数字类型写入，避免“数字存为文本”
- `keywords` 数据区配色：SIM 列浅蓝、SEM 列浅紫

## 规则摘要（MVP）

- SIM 固定过滤：`cpc,0.1,|difficulty,1,70`
- SEM 固定过滤：`cpc > 0.1`、`difficulty < 70`
- 两路各自最多抓 300 个词
- 先分源 AI 近义合并，再跨源 merge
- 组内 canonical = 最大 volume 词
- 组内 volume = 求和；CPC/KD = volume 加权平均
- 合并后按 `simWindowVolume * simCpc / simKd` 降序排序
- `gefeiKD` 只作为补充字段，不参与排序
- Excel 是完整结果，Markdown 仅做预览
