# word-from-root

输入一个词根，调用 SIM Suggest 与 SEM Keyword Magic 两路接口，抓取相关关键词，合并成一张总表，并导出为 Excel。

## 功能概览

每次运行会执行：

1. 调用 SIM `KeywordGenerator/google/suggest`
2. 调用 SEM `ideas.GetKeywordsSummary` 与 `ideas.GetKeywords`
3. 标准化两路关键词结果
4. 分别对 SIM / SEM 做 AI 近义合并（词序、空格/`-`、单复数、无意义重复）
5. 按分组后的关键词进行两路合并并计算排序值
6. 先生成基础标准词表（history/latest）
7. 调用 `check-gefei-kd` 对标准词表执行后置分析（默认最多前 50 词）
8. 将 `gefeiKD` 回填到最终标准词表并重写 Markdown/Excel
9. 额外同步最终 Excel 到仓库根目录 `words/root-[关键词根]-[time].xlsx`

## 目录说明

- `data/`：每次抓取归档（`fetch-YYYYMMDD-HHMMSS.json`）
- `_internal/snapshots/`：标准化快照（`snapshot-YYYYMMDD-HHMMSS.json`）
- `report/history/`：历史 Markdown / Excel
- `report/latest.md`：最新 Markdown 报告
- `report/latest.xlsx`：最新 Excel 报表
- `local-service/`：本地服务接口文档、token 文件、gmitm 文件

## 运行前准备

1. 本地服务已启动
2. 浏览器扩展已安装并可用
3. 已登录 `https://sim.3ue.co` 与 `https://sem.3ue.co`
4. token 文件存在：`local-service/bridge_token.txt`
5. gmitm 文件存在：`local-service/__gmitm.txt`
6. 已安装导出依赖：

```bash
pip3 install -r word-from-root/requirements.txt
```

可先检查健康状态：

```bash
curl -s http://127.0.0.1:17311/health
```

## 使用方式

在仓库根目录执行：

```bash
# 执行一次完整抓取
python3 word-from-root/_internal/scripts/word_from_root.py run --keyword "image to text"
```

> 默认后置分析只处理标准词表前 50 个关键词，可用 `--gefei-kd-max-keywords` 调整（传 `0` 表示不限制）。

可选命令：

```bash
# 基于快照重建 Markdown / Excel
python3 word-from-root/_internal/scripts/word_from_root.py rebuild-reports

# 校验最新 Markdown / Excel
python3 word-from-root/_internal/scripts/word_from_root.py validate-report
```

## 当前规则（MVP）

### SIM

- `latest=28d`
- `country=999`
- `sort=windowVolume`
- `rowsPerPage=100`
- `rangeFilter=cpc,0.1,|difficulty,1,70`
- 最多抓取 300 个词

### SEM

- `database=us`
- `currency=USD`
- `page.size=100`
- `cpc > 0.1`
- `difficulty < 70`
- 最多抓取 300 个词

### 分源近义合并（AI）

- 在 SIM/SEM 各自内部先做 AI 近义分组，再进行跨源合并
- canonical 词：组内 `volume` 最大的词（并列按字典序）
- `group` 列：组内全部原词（` | ` 拼接）
- volume：组内求和
- CPC / KD：按各词 volume 占比加权平均
- 分组结果会缓存到 `word-from-root/_internal/grouping-cache/`

可通过参数控制分组调用：

```bash
python3 word-from-root/_internal/scripts/word_from_root.py run   --keyword "image to text"   --grouping-model ""   --grouping-temperature 0   --grouping-timeout-seconds 120
```

### 合并与排序

- 关键词 join key：source 内分组后的 `mergeKey`
- `sourcePresence`：`both / sim_only / sem_only`
- 排序值：`score = simWindowVolume * simCpc / simKd`
- 若缺失完整 SIM 指标，`score` 为空并排在已评分结果之后
- `gefeiKD` 只作为补充字段，不参与排序

## 标准词表（数据交换层）

`report/latest.xlsx` 对齐 `standard-word-analysis` 的 v1 标准词表：

- 规范路径：`standard-word-analysis/spec/standard-word-table.v1.json`
- `keywords` sheet 列顺序：`keyword -> 对应域名 -> score -> volume(sim) -> kd(sim) -> cpc(sim) -> volume(sem) -> kd(sem) -> cpc(sem) -> gefeiKD -> group -> sourcePresence(SIM/SEM)`
- 本版 score 公式：`simWindowVolume * simCpc / simKd`
- `word-from-root` 当前会输出 `对应域名` 空列，供其它 skill 保持统一表头
- `gefeiKD` 使用哥飞 KD API 返回的 `score`
- 文本列导出采用自动换行（wrap）+ 顶对齐，避免长内容遮挡相邻列
- `group` / `对应域名` 在展示层按多值分行（单元格内换行）以提升可读性
- Excel 数值列（`score/sim*/sem*/gefeiKD`）按数字类型写入，避免“数字存为文本”
- `keywords` 数据区配色：SIM 列浅蓝、SEM 列浅紫

因此 `word-from-root` 产物可直接作为后续 skill（如 analyze/check）的输入交换表。

### 后置 KD 分析与发布

- `check-gefei-kd` 后置分析默认仅处理标准词表前 50 个关键词（可通过 `--gefei-kd-max-keywords` 调整，`0` 表示不限制）。
- 最终标准词表 Excel 会额外同步到仓库根目录 `words/`。
- 命名规则：`root-[关键词根]-[YYYYMMDD-HHMMSS].xlsx`（关键词会做文件名安全清洗）。

### 常用新增参数

```bash
python3 word-from-root/_internal/scripts/word_from_root.py run \
  --keyword "image to text" \
  --gefei-kd-max-keywords 50 \
  --words-dir "$(pwd)/words" \
  --chain-work-dir "word-from-root/_internal/chained"
```

## 相关文件

- 外层 skill 入口：`.claude/skills/word-from-root/SKILL.md`
- 内部说明：`word-from-root/_internal/skill/SKILL.md`
- 快照结构：`word-from-root/_internal/docs/SNAPSHOT_SCHEMA.md`
- 标准词表规范：`standard-word-analysis/spec/standard-word-table.v1.json`
- 主脚本：`word-from-root/_internal/scripts/word_from_root.py`
