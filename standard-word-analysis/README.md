# standard-word-analysis

用于定义“找词/研究词”流程之间的数据交换层（标准词表）。

## 目标

- 给所有 skill 一个统一可读写的词表契约。
- 让不同 skill 产物可以直接串联（先填关键词，再逐步补列）。
- 保持与当前 `word-from-root` 的 Excel 产物兼容。

## 当前版本

- 版本：`v1`
- 规范文件：`spec/standard-word-table.v1.json`
- 样例数据：`sample/standard-word-table.v1.sample.json`
- 样例表格：`sample/standard-word-table.v1.sample.xlsx`

## v1 列定义（严格顺序）

1. `keyword`
2. `group`
3. `sourcePresence(SIM/SEM)`
4. `score(simWindowVolume*cpc/kd)`
5. `volume(sim)`
6. `kd(sim)`
7. `cpc(sim)`
8. `volume(sem)`
9. `kd(sem)`
10. `cpc(sem)`

## 规则说明（v1）

- `score` 公式固定为：`simWindowVolume * simCpc / simKd`
- 当缺失完整 SIM 指标时（任一缺失或<=0），`score` 允许为空
- `sourcePresence` 取值：`both` / `sim_only` / `sem_only`
- v1 阶段禁止修改列名和顺序（可在后续版本扩展）

## 范围声明

- 本版本不包含 `gefeiKD` 列
- `gefeiKD` 在后续版本通过增量字段扩展，不影响 v1 兼容性

## 与 word-from-root 的关系

`word-from-root` 当前输出即对齐本标准（v1）：

- 产物：`word-from-root/report/latest.xlsx`
- 代码入口：`word-from-root/_internal/scripts/word_from_root.py`
- 校验命令：

```bash
python3 word-from-root/_internal/scripts/word_from_root.py validate-report
```
