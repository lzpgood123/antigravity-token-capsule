# Specification: Subagent Cluster Monitoring & Hybrid Layout

Status: ready-for-agent

> 🧭 **施工行动方针 (Implementation Brief)**:  
> 本特性的代码物理路标、既有测试参照与避坑指南已提炼至 [brief.md](./brief.md)。请施工 Agent 优先参阅！

## Problem Statement

When using Google Antigravity on complex programming tasks, the primary agent frequently invokes autonomous subagents (such as Explorers, Code Reviewers, or Background Workers) to perform parallel exploration, validation, or implementation. 

Currently, Token Capsule strictly monitors only the active primary conversation. While this accurately tracks the primary session's 256k context window, it leaves a significant blind spot regarding the total compute and financial expenditure:
1. **Compute & Cost Invisibility**: Users have no visibility into how many tokens or how much money background subagents are consuming during a task.
2. **Subagent Status Blindness**: Users cannot tell whether dispatched subagents are actively running or finished, nor their individual throughput and latency metrics.
3. **Desktop Form-Factor Dilemma**: Users need both a distraction-free, ultra-compact floating widget during normal single-agent coding, and a comprehensive, simultaneous multi-agent overview when running concurrent agent teams.

## Solution

Extend Token Capsule with **Subagent Cluster Monitoring** and a **Dual-Mode Hybrid Layout**:
1. **Decoupled Metric Model**: Preserve the primary session's physical 256k context window bar while rolling up all dispatched subagent tokens and financial costs into a unified cluster view.
2. **Hybrid Layout System**:
   - **Compact Tabbed Mode (Default / Variant A)**: Maintain the classic 320px width card. Provide a top tab switcher (`[ 💬 主会话 ]` and `[ 🤖 智能体集群 •N ]`). The Cluster tab features a micro-dashboard rollup bar and an interactive subagent list with smooth accordion expansion to view detailed prompt/output/thinking/speed metrics. The Primary tab features dual-cost linkage (`$0.081 (含集群: $0.235)`).
   - **Dual-Wing Radar Mode (Variant C)**: A wide 680px dual-wing card with side-by-side live monitoring of both the primary session (left) and the real-time subagent cluster radar (right).
   - **Tray Switcher**: Allow instantaneous hot-switching between Compact Single Card and Dual-Wing Radar via the system tray menu (`📐 布局模式`), persisting user preference across restarts.
3. **Zero-Overhead Incremental Sniffing**: The data engine dynamically discovers subagents derived from the active conversation via local logs, monitoring SQLite WAL modification timestamps (`mtime`) with 300ms polling to deliver near-instant updates with near-zero CPU footprint.

## User Stories

1. As a developer using Antigravity multi-agent mode, I want to see the total token usage and financial cost of all dispatched subagents alongside the primary conversation, so that I have complete transparency over the total cost of my task.
2. As a developer monitoring my prompt budget, I want the primary 256k context progress bar to reflect strictly the primary session's physical window, so that subagent usage does not distort my context window overflow warnings.
3. As a user working on a single screen, I want the default expanded view to stay in a compact 320px card with tabs, so that the widget does not occlude my IDE code editor.
4. As a developer in the Primary Session tab, I want to see a dual-cost readout (e.g., `$0.081 (含集群: $0.235)`), so that I am always aware of background cluster spending without having to constantly switch tabs.
5. As a developer switching to the Agent Cluster tab, I want to see a top micro-dashboard summary of total cluster tokens, total cluster cost, and the count of running versus finished subagents, so that I can immediately assess cluster-wide status.
6. As a developer observing parallel subagents, I want each subagent in the cluster list to display a clear status indicator (pulsing green for running, solid gray for finished), so that I know at a glance which subagents are still doing work.
7. As a developer reviewing subagent tasks, I want subagent list items to display human-readable semantic role names (e.g., "Explorer 1 (Backend & Assets)") rather than raw machine UUIDs, so that I can immediately identify which subagent is which.
8. As a developer diagnosing a slow or expensive subagent, I want to click on its row to smoothly expand an inline accordion showing its prompt tokens, output tokens, thinking tokens, TTFT latency, and generation speed, so that I can pinpoint performance bottlenecks.
9. As a developer monitoring multiple subagents simultaneously on a wide monitor, I want to switch to a Dual-Wing Radar layout, so that I can watch the primary session and all active subagents side by side without clicking between tabs.
10. As a user preferring different layouts for different monitors or workflows, I want to toggle between Compact Single Card and Dual-Wing Radar directly from the system tray context menu, so that changing layout is fast and accessible from anywhere.
11. As a user who configures a preferred layout, I want my layout choice to be remembered across application restarts, so that I do not need to reconfigure it every time the tool boots.
12. As a developer running high-frequency subagents, I want the data engine to use lightweight timestamp (`mtime`) checks on SQLite WAL files, so that subagent monitoring does not induce CPU lag or battery drain.
13. As a developer whose session has not dispatched any subagents, I want the widget to gracefully hide or grey out the cluster tab / dual cost badge, so that the interface remains clean and distraction-free when only a single session exists.
14. As a developer collapsing the widget to its 36px floating pill, I want the pill text to include a compact indicator of active cluster agents when present, so that I know background work is progressing even when minimized.

## Implementation Decisions

### 1. Data Schema & Signal Contract
The data engine will extend the existing `session_updated` dictionary with a dedicated `cluster` key containing:
- `totalTokens`: Integer cumulative billed tokens across all subagents.
- `totalCostUsd`: Float cumulative financial cost across all subagents.
- `activeCount`: Integer number of subagents currently in `running` state.
- `completedCount`: Integer number of subagents in `idle` or `done` state.
- `combinedCostUsd`: Float sum of primary session cost and cluster cost.
- `subagents`: List of subagent objects, each containing:
  - `id`: Subagent conversation UUID.
  - `role`: Human-readable semantic role name.
  - `type`: System type identifier.
  - `state`: `"running"` or `"done"`.
  - `promptTokens`, `candidateTokens`, `thinkingTokens`, `cachedTokens`.
  - `ttft`: Float time to first token in seconds.
  - `speed`: Float tokens per second.
  - `costUsd`: Float estimated cost in USD.

### 2. Subagent Discovery & Polling Mechanism
- Parse the active session's local transcript (`.system_generated/logs/transcript.jsonl`) to detect `invoke_subagent` calls, extracting the subagent UUIDs, semantic roles, and lifecycle states.
- Maintain a dynamic subagent watchlist for the currently active primary conversation.
- In the existing 300ms non-blocking polling timer, inspect the `mtime` and file size of each watched subagent's SQLite database and WAL file.
- Query and decode usage blobs from `gen_metadata` in read-only mode (`mode=ro`) using the zero-dependency `proto_decoder`.

### 3. UI Presentation & Layout Modes
- **Layout Mode 1: Compact Tabbed (Default)**:
  - Card width fixed at 320px.
  - Header displays a modern segmented tab control: `[ 💬 主会话 ]` / `[ 🤖 智能体集群 •N ]`.
  - Primary tab preserves the existing 5-segment hero card, updating the bottom cost row to show primary cost with combined total in parentheses.
  - Cluster tab displays the micro-dashboard bar on top, followed by a vertically scrollable list of subagent cards with accordion expand/collapse toggles.
- **Layout Mode 2: Dual-Wing Radar**:
  - Card width expands to 680px with a subtle divider separating the left wing (Primary Session card) and right wing (Cluster Radar card).
  - Provides simultaneous real-time visual feedback for multi-agent workflows.

### 4. Configuration & Tray Menu
- Add a `"layout_mode": "compact" | "dual_wing"` setting to the persistent configuration file alongside theme preferences.
- Add a new submenu `📐 布局模式 (Layout Mode)` to the system tray context menu with mutually exclusive radio actions:
  - `● 紧凑单卡 (Compact Tabbed / 方案 A)`
  - `○ 展开双翼 (Dual-Wing Radar / 方案 C)`
- Dynamically adjust window constraints and geometry upon mode switching without disrupting screen placement.

## Testing Decisions

### Seam Selection
The highest testable seam is the **DataEngine Output & Signal Seam**:
- **Seam**: `DataEngine.get_convo_stats(conv_id)` and the payload emitted by `DataEngine.session_updated`.
- **Rationale**: Verifies end-to-end integration across transcript discovery, SQLite connection pooling, Protobuf extraction, rollup aggregation, and schema adherence without coupling to Qt rendering internals.
- **Secondary Seam**: Layout and configuration state round-tripping (`load_saved_settings()`, `save_settings()`), verifying that layout mode transitions persist and load cleanly.

### What Makes a Good Test
- Tests must operate against isolated, synthetic test fixture files (transcript JSONL samples and temporary SQLite databases) rather than live production state.
- Tests must verify external contract behavior (correct rollup calculations, proper status mapping, correct cost linkage) rather than internal helper implementation details.

## Out of Scope

1. **Subagent Control Actions**: Pausing, killing, or messaging subagents from the Token Capsule UI is out of scope (Capsule is strictly an observability and monitoring tool, not an orchestrator).
2. **Infinite Historical Retention**: Storing multi-month historical timeseries of subagent execution traces inside Capsule's memory.
3. **Cross-Project Global Dashboard**: Aggregating subagents from completely unrelated workspace projects that are not part of the active session's lineage.

## Further Notes

- All UI components must adhere to the 5 official theme color tokens defined in `THEME_CONFIGS` (Pure Light, Obsidian Dark, Frosted Aurora, Matrix Neon, Warm Paper).
- Accordion animations and width transitions should remain snappy (<150ms) to ensure lightweight desktop responsiveness.
