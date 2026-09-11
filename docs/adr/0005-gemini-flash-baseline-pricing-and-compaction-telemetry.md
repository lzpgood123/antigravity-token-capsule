# ADR 0005: Gemini 3.8 Flash 基准计费与上下文自动压缩遥测

## Status

Accepted

## Context

Token Capsule 在展示折算美元消耗与上下文容量时面临两个关键的产品认知与工程决策问题：

1. **计费模型透明度**：此前数据引擎直接按每百万 Token 费率（输入 $0.75、输出 $3.75、缓存 $0.075）计算会话美元花费，但客户端 UI 与文档均未显式声明基准模型，导致开发者无法确认折算依据，容易误判为 Claude 3.5 Sonnet 等高价模型或与官方账单发生认知脱节。
2. **长上下文记忆修剪感知缺失**：在长耗时会话或多轮复杂工程任务中，Antigravity 会自动对过长上下文触发截断压缩（写入 `transcript.jsonl` 的 `type: "CHECKPOINT"` 检查点）。一旦压缩发生，早期消息被替换为摘要，智能体的精确细节记忆有所衰减。此前开发者无法感知当前会话是否经历过自动压缩以及压缩了多少次。

## Decision

我们做出如下两项核心设计与技术决策：

1. **确立 Gemini 3.8 Flash 为全局基准计费模型 (Baseline Pricing Model)**：
   * **标准化费率**：输入 \$0.75/1M tokens、输出 \$3.75/1M tokens、Prompt 缓存命中 \$0.075/1M tokens。
   * **UI 显式透视**：在卡片指标行明确标注 `累计折算费用 (Gemini 3.8 Flash)`，悬停 Tooltip 呈现完整单价计算公式。
   * **双语与文档统一**：在 `README.md`、`README_EN.md` 与领域字典 `CONTEXT.md` 中全面公开计费模型定义。
2. **基于 Checkpoint 的上下文自动压缩遥测机制 (Compaction Telemetry)**：
   * **数据源**：`data_engine.py` 在嗅探会话日志时，毫秒级统计当前活跃会话 `transcript.jsonl` 中 `type: "CHECKPOINT"` 的出现次数，并在会话数据载荷中输出 `compactCount`。
   * **Hero 头部预警 Badge + Summary 明细联动**：
     * 当 `compactCount == 0` 时保持隐蔽，不产生视觉噪音。
     * 当 `compactCount >= 1` 时，在 Hero 核心进度百分比旁亮起橙黄色警示 Badge（如 `⚡ 压缩 2 次`），鼠标悬停提示上下文截断详情；并在 Summary 列表中渲染独立的 `上下文自动压缩` 状态行。
     * 保持会话粒度隔离，主会话与各级 Subagents 分开统计。

## Consequences

- **Positive**：
  * **财务透明**：彻底消除折算费用认知歧义，与 Antigravity 默认主流驱动引擎 Gemini 3.8 Flash 保持一致。
  * **状态透明**：开发者一目了然得知当前会话记忆是否经历了精简压缩，便于及时 `/compact`、清空或分派子智能体以保持推理敏锐度。
  * **零额外负担**：复用现有的 `transcript.jsonl` 嗅探管道，不引入额外 I/O 开销。
- **Trade-offs**：
  * 仅基于 Gemini 3.8 Flash 作为基准定价，若用户手工切换到其他大模型（如 Gemini Pro 或 Claude），当前折算为相对等价的 Flash 算力成本参考，未来可扩展多模型切换配置。
