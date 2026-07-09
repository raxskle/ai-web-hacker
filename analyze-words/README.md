# analyze-words

批量分析关键词可行性：调用本地服务 `Keyword Info（SEM · keywords.GetInfo）`，输出每个关键词的聚合指标（总流量、综合 CPC、综合 KD）。

## 快速开始

在仓库根目录执行：

```bash
# 方式一：直接传关键词（可重复 --keyword）
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --keyword "image to text" \
  --keyword "ocr online"

# 方式二：传关键词文件（每行一个关键词）
python3 analyze-words/_internal/scripts/analyze_words.py run \
  --keyword-file /absolute/path/keywords.txt
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
# 仅基于 snapshot 重建报告
python3 analyze-words/_internal/scripts/analyze_words.py rebuild-reports

# 校验 latest.md 报告结构
python3 analyze-words/_internal/scripts/analyze_words.py validate-report
```

## 默认参数（与接口文档示例保持一致）

- API Base：`http://127.0.0.1:17311`
- Endpoint：`/sem/kwogw/v2/webapi/keywords.GetInfo`
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

仅会按关键词动态修改 `params.phrase`（以及请求追踪 id）。

## 聚合口径

对于每个关键词，基于上游返回 `result.keywords[]` 计算：

- `globalVolume = sum(volume)`
- `globalCpcAvg = avg(cpc, 忽略 null)`
- `globalDifficultyAvg = avg(difficulty, 忽略 null)`

## 输入输出

- 本地服务文档：`analyze-words/local-service/API_REFERENCE.md`
- token 文件：`analyze-words/local-service/bridge_token.txt`
- gmitm 文件：`analyze-words/local-service/__gmitm.txt`
- 抓取归档：`analyze-words/data/fetch-YYYYMMDD-HHMMSS.json`
- 快照归档：`analyze-words/_internal/snapshots/snapshot-YYYYMMDD-HHMMSS.json`
- 历史报告：`analyze-words/report/history/report-YYYYMMDD-HHMMSS.md`
- 最新报告：`analyze-words/report/latest.md`

## 失败策略

- token/gmitm 缺失：直接失败
- 单关键词请求失败：最多重试 2 次（0.8s / 1.6s）
- 任一关键词最终失败：整次失败，不写入新产物
