# word-from-root

输入一个词根，调用 SIM Suggest 与 SEM Keyword Magic 两路接口，抓取相关关键词，合并成一张总表，并导出为 Excel。

## 功能概览

每次运行会执行：

1. 调用 SIM `KeywordGenerator/google/suggest`
2. 调用 SEM `ideas.GetKeywordsSummary` 与 `ideas.GetKeywords`
3. 标准化两路关键词结果
4. 按关键词合并并计算排序值
5. 归档原始抓取结果与标准化快照
6. 生成 Markdown 摘要与 Excel 明细

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
- `rangeFilter=cpc,0.1,|difficulty,1,80`
- 最多抓取 300 个词

### SEM

- `database=us`
- `currency=USD`
- `page.size=100`
- `cpc > 0.1`
- `difficulty < 90`
- 最多抓取 300 个词

### 合并与排序

- 关键词 join key：小写 + trim + 压缩空格
- `sourcePresence`：`both / sim_only / sem_only`
- 排序值：`score = semVolume * semCpc / semKd`
- 若缺失完整 SEM 指标，`score` 为空并排在已评分结果之后

## 报告说明

- Markdown 只展示摘要与 Top 关键词预览
- Excel 为完整结果表
- 建议在 Excel 中按 `sourcePresence` 过滤查看两路差异

## 相关文件

- 外层 skill 入口：`.claude/skills/word-from-root/SKILL.md`
- 内部说明：`word-from-root/_internal/skill/SKILL.md`
- 快照结构：`word-from-root/_internal/docs/SNAPSHOT_SCHEMA.md`
- 主脚本：`word-from-root/_internal/scripts/word_from_root.py`
