# Issue 02: UI 方案 A（紧凑单卡 Tab 与手风琴折叠展开）实现

Status: ready-for-agent
Type: task

## Description
在 `capsule_ui.py` 中实现方案 A 的紧凑标签页与手风琴折叠卡片：
1. 顶部增加现代分段 Tab 切换组件：`[ 💬 主会话 ]` / `[ 🤖 智能体集群 •N ]`。
2. 主会话 Tab：底部折算费用支持双计费展示：`$0.081 (含集群: $0.235)`。
3. 集群 Tab：顶部渲染微仪表盘横条（总 Token、总费用、运行/完成分布），下方为子智能体列表。
4. 子智能体单项交互：显示语义化角色名、状态呼吸灯/徽章、Token 与费用，点击整行就地平滑展开详细物理指标（Prompt、Output、Thinking、TTFT、速度）。
5. 适配 5 套主题配色（Light, Dark, Glass, Cyberpunk, Warm）。

## Acceptance Criteria
- 默认在 320px 紧凑宽度下自如操作，双 Tab 切换流畅。
- 子智能体行点击展开/收起手风琴动画平滑，展示完整的各维度指标。
