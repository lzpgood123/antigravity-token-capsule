# Issue 01: DataEngine 子智能体发现与用量聚合引擎

Status: ready-for-agent
Type: task

## Description
在 `data_engine.py` 中拓展子智能体发现与数据采集能力：
1. 解析主会话 `transcript.jsonl`，自动提取由当前活跃会话派生出的子智能体 UUID、角色名（Role）、类型（Type）及运行状态（`running` / `done`）。
2. 维护活跃子智能体轮询列表，在现有的 300ms 定时器中增量检测各子智能体 `.db` 与 `.db-wal` 的 `mtime` 和大小。
3. 利用 `proto_decoder` 提取各子智能体用量，并在 `session_updated` 信号中附加 `cluster` 聚合字段。

## Acceptance Criteria
- 当主会话有子智能体时，`session_updated` 发送的字典包含完整的 `cluster` 字段及各子智能体指标。
- 无子智能体时 `cluster` 字段优雅为空或默认值，不影响主会话逻辑。
- 轮询开销极低，未发生文件变动时不进行任何无用读取。
