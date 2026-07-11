# analyze-words

批量分析关键词可行性：调用本地服务 `Keyword Info（SEM · keywords.GetInfo）` + `Keyword Generator Suggest（SIM）`，输出每个关键词的聚合指标，并生成标准词表结果文档（Excel + JSON）。

## 快速开始

在仓库根目录执行：

```bash
# 方式一：直接传关键词（可重复 --keyword；支持逗号/分号/中文标点分隔）
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --keyword "image to text, ocr online" \
  --keyword "pdf to text"

# 方式二：传关键词文件（每行一个关键词）
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --keyword-file /absolute/path/keywords.txt

# 方式三：CSV 关键词列表
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --keywords-csv "image to text,ocr online,pdf to text"

# 方式四：标准词表输入（json / xlsx）
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --input-table standard-word-analysis/sample/standard-word-table.v1.sample.json

python3 analyze-words/_internal/scripts/analyze_words.py run \
  --input-table standard-word-analysis/sample/standard-word-table.v1.sample.xlsx

# 方式五：混合输入（标准词表 + 新词）
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --input-table /absolute/path/existing-standard-table.xlsx \
  --keywords-csv "new keyword 1,new keyword 2"
```

关键词文件示例：

```text
# comment line
image to text
ocr online
pdf to text
```

## 可选命令

```bash
# 仅基于 snapshot 重建报告与标准词表
python3 analyze-words/_internal/scripts/analyze_words.py rebuild-reports

# 校验 latest.md + latest.xlsx + latest.json
python3 analyze-words/_internal/scripts/analyze_words.py validate-report
```

## 默认参数（与接口文档示例保持一致）

- API Base：`http://127.0.0.1:17311`
- Endpoint：`/sem/kwogw/v2/webapi/keywords.GetInfo`
- SIM Endpoint：`/sim/api/KeywordGenerator/google/suggest`
- JSON-RPC：
  - `method=keywords.GetInfo`
  - `device=0`
  - `currency=USD`
  - `database=us`
  - `locati0n=0`
  - `date=""`
- 本地服务附加参数：
  - `timeoutMs=45000`
  - `waitTimeoutMs=120000`
- SIM 固定请求参数：
  - `country=999`
  - `latest=28d`
  - `isWindow=true`
  - `webSource=Total`
  - `rowsPerPage=5`
  - `page=1`
  - `sort=score`
  - `asc=false`
  - `type=Related`

仅会按关键词动态修改 `params.phrase`（SEM）与 `keyword`（SIM，及请求追踪 id）。

## 聚合口径

对于每个关键词，基于上游返回 `result.keywords[]` 计算：

- `globalVolume = sum(volume)`
- `globalCpcAvg = avg(cpc, 忽略 null)`
- `globalDifficultyAvg = avg(difficulty, 忽略 null)`

## 标准词表补全规则（v1）

- 标准词表规范：`standard-word-analysis/spec/standard-word-table.v1.json`
- 当前流程会补以下字段：
  - SIM：`volume(sim)` / `kd(sim)` / `cpc(sim)`
  - SEM：`volume(sem)` / `kd(sem)` / `cpc(sem)`
- SIM 匹配规则：
  - 对每个输入关键词调用 Suggest（top 5）
  - 仅在返回 5 条中，按归一化后与输入词**精确相等**匹配对应关键词
  - 命中后使用该记录的 `windowVolume` / `difficulty` / `cpc` 回填 SIM 列
- `score(simWindowVolume*cpc/kd)` 只由 SIM 字段计算：
  - `score = simWindowVolume * simCpc / simKd`
  - 当 SIM 指标缺失或 <=0 时，`score` 为空
- `sourcePresence(SIM/SEM)` 按 SIM/SEM 是否存在自动重算：
  - `both` / `sim_only` / `sem_only`
- `keywords` sheet 列顺序固定为：`keyword -> 对应域名 -> score -> volume(sim) -> kd(sim) -> cpc(sim) -> volume(sem) -> kd(sem) -> cpc(sem) -> gefeiKD -> group -> sourcePresence(SIM/SEM)`
- Excel 数值列（`score/sim*/sem*/gefeiKD`）按数字类型写入，避免“数字存为文本”
- `keywords` 数据区配色：SIM 列浅蓝、SEM 列浅紫
- 文本列导出采用自动换行（wrap）+ 顶对齐，避免长内容遮挡相邻列
- `group` / `对应域名` 在展示层按多值分行（单元格内换行）以提升可读性

## 输入输出

- 本地服务文档：`analyze-words/local-service/API_REFERENCE.md`
- token 文件：`analyze-words/local-service/bridge_token.txt`
- gmitm 文件：`analyze-words/local-service/__gmitm.txt`
- 抓取归档：`analyze-words/data/fetch-YYYYMMDD-HHMMSS.json`
- 快照归档：`analyze-words/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史报告：`analyze-words/report/history/report-YYYYMMDD-HHMMSS.md`
- 历史标准词表 Excel：`analyze-words/report/history/keyword-table-YYYYMMDD-HHMMSS.xlsx`
- 历史标准词表 JSON：`analyze-words/report/history/keyword-table-YYYYMMDD-HHMMSS.json`
- 最新报告：`analyze-words/report/latest.md`
- 最新标准词表 Excel：`analyze-words/report/latest.xlsx`
- 最新标准词表 JSON：`analyze-words/report/latest.json`

## 失败策略

- token/gmitm 缺失：直接失败
- 单关键词 SEM 请求失败：最多重试 2 次（0.8s / 1.6s）
- 任一关键词 SEM 最终失败：整次失败，不写入新产物
- 单关键词 SIM 请求失败或 top5 未命中对应关键词：整次继续，该词 SIM 字段置空
