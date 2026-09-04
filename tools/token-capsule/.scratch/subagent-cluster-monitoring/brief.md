# 🧭 施工行动方针与代码路标 (Implementation Brief)

> **特性目录**：`tools/token-capsule/.scratch/subagent-cluster-monitoring/`  
> **关联图纸**：[`spec.md`](./spec.md)  
> **设计决策**：[`docs/adr/0002-subagent-cluster-monitoring-and-hybrid-layout.md`](../../docs/adr/0002-subagent-cluster-monitoring-and-hybrid-layout.md)  
> **视觉原型**：[`prototype_subagent_ui.html`](../prototype_subagent_ui.html)  
> **使命**：消除施工 AI 冷启动探索成本，提供无二义性的代码靶点、测试参照与架构防坑指南。

---

## 1. 📍 必读源码与函数 (Must-Read Codebase)

* [`tools/token-capsule/data_engine.py#L119-L158`](file:///d:/agent/gemini/new/01/tools/token-capsule/data_engine.py#L119-L158)：
  * **角色与核心逻辑**：`_poll_updates(self)` 是整个监控的核心心脏，300ms 定时器无阻塞执行。目前只侦测单一主会话的 `db_path` 与 `wal_path` 的 `mtime` 和大小。
  * **必读原因**：在此处扩展子智能体发现机制（检测主会话 `transcript.jsonl` 更新）与动态轮询子智能体集合的增量 `mtime`。
* [`tools/token-capsule/data_engine.py#L208-L303`](file:///d:/agent/gemini/new/01/tools/token-capsule/data_engine.py#L208-L303)：
  * **角色与核心逻辑**：`get_convo_stats(self, conv_id)` 连接 SQLite 只读数据库 (`?mode=ro`)，提取 `gen_metadata` 中的二进制 Proto Usage Blob 并聚合。
  * **必读原因**：子智能体的数据提取逻辑与此完全同构！可将其核心逻辑提炼为可复用的 `_extract_session_metrics(self, conv_id)`，供主会话与各子智能体共享。
* [`tools/token-capsule/proto_decoder.py`](file:///d:/agent/gemini/new/01/tools/token-capsule/proto_decoder.py)：
  * **角色与核心逻辑**：纯 Python 独立实现的轻量 Protobuf 解码器，提供 `extract_usage_from_blob(blob: bytes) -> dict`。
  * **必读原因**：子智能体数据库中 `gen_metadata` 存储格式与主会话 100% 一致，直接复用此函数解码即可。
* [`tools/token-capsule/capsule_ui.py#L13-L94`](file:///d:/agent/gemini/new/01/tools/token-capsule/capsule_ui.py#L13-L94)：
  * **角色与核心逻辑**：`THEME_CONFIGS` 定义了 5 套官方主题的全部色值（Pure Light, Obsidian Dark, Frosted Aurora, Matrix Neon, Warm Paper）。
  * **必读原因**：新增的 Tab 标签、微仪表盘条、手风琴列表及双翼布局必须统一使用这些 Theme Token，严禁硬编码未知颜色。
* [`tools/token-capsule/main.py#L1-L150`](file:///d:/agent/gemini/new/01/tools/token-capsule/main.py#L1-L150)：
  * **角色与核心逻辑**：主入口，初始化 `QApplication`、`DataEngine`、`CapsuleWindow` 与 `TrayIcon` 系统托盘。
  * **必读原因**：需要在托盘中新增「📐 布局模式」二级菜单，支持在单卡与双翼之间热切并连接窗口槽函数。

---

## 2. 🎯 核心修改靶点 (Target Files & Interfaces)

### ① `tools/token-capsule/data_engine.py`
* **新增方法**：
  * `_discover_subagents(self, primary_conv_id: str) -> list[dict]`：从 `~/.gemini/antigravity/brain/<conv_id>/.system_generated/logs/transcript.jsonl` 中正则/JSON 提取由当前会话创建的子智能体列表（包含 `id`, `role`, `type`, `state`）。
  * `_get_subagent_stats(self, sub_id: str) -> dict`：轻量读取 `~/.gemini/antigravity/conversations/<sub_id>.db` 获取其累积 token 与性能。
* **接口变更**：
  * `session_updated` Signal 载荷中的字典新增 `"cluster"` 节点：
    ```python
    "cluster": {
        "totalTokens": 128500,
        "totalCostUsd": 0.154,
        "combinedCostUsd": 0.235,  # 主会话 + 集群
        "runningCount": 2,
        "doneCount": 1,
        "subagents": [
            {
                "id": "87330fc4-...",
                "role": "Explorer 1 (Backend & Assets)",
                "state": "running",
                "totalTokens": 52400,
                "costUsd": 0.063,
                "promptTokens": 48000,
                "candidateTokens": 4400,
                "thinkingTokens": 1200,
                "cachedTokens": 42000,
                "ttft": 0.38,
                "speed": 74.0,
                "lastAction": "正在执行 ripgrep 深度模式匹配..."
            }
        ]
    }
    ```

### ② `tools/token-capsule/capsule_ui.py`
* **新增与重构组件**：
  * **顶部分段 Tab 控制器**：在卡片顶部注入 `[ 💬 主会话 ]` / `[ 🤖 智能体集群 •N ]` 标签切换。
  * **微仪表盘横条 (Micro Dashboard)**：切到集群 Tab 时置顶渲染（总 Token、费用、运行/完成徽章）。
  * **手风琴子智能体列表 (`SubagentAccordionList`)**：渲染各智能体卡片，点击平滑展开/收起微型指标条。
  * **主会话双计费联动**：底部费用显示 `累计折算费用: $0.081 (含集群: $0.235)`。
  * **双翼雷达布局 (Dual-Wing Radar)**：支持将卡片扩展为左右双翼结构（总宽 680px），同时显示主会话与集群雷达。
  * **`set_layout_mode(mode: str)` 方法**：接收 `"compact"` 或 `"dual_wing"`，动态重设窗口尺寸与显示结构。

### ③ `tools/token-capsule/main.py`
* **设置与托盘**：
  * 将 `capsule_theme.json` 升级/兼容为 `capsule_settings.json`（持久化存储 `theme` 与 `layout_mode`）。
  * 在托盘菜单新增 `📐 布局模式` 单选子菜单（`● 紧凑单卡 (默认)` / `○ 展开双翼`）。

---

## 3. 🧪 既有轮子与测试参照 (Prior Art & Patterns)

* **已有工具复用（严禁重复造轮子）**：
  * **Protobuf 解码**：直接调用 [`proto_decoder.py`](file:///d:/agent/gemini/new/01/tools/token-capsule/proto_decoder.py) 的 `extract_usage_from_blob`，严禁引入 `google.protobuf` 或外部重量级包。
  * **Token 格式化**：直接复用 `data_engine.py` 中的 `fmt_tokens(n: int)`。
  * **主题 QSS 样式生成**：复用 `capsule_ui.py` 中的 `make_theme_qss(cfg)` 与 `THEME_CONFIGS`。
* **高保真交互参照**：
  * 直接打开并参照已跑通的原型：[`tools/token-capsule/.scratch/prototype_subagent_ui.html`](file:///d:/agent/gemini/new/01/tools/token-capsule/.scratch/prototype_subagent_ui.html)，其 CSS 变量、DOM 结构与交互细节已完全对齐 Antigravity 视觉标准。
* **测试写法范式**：
  * 编写针对 `DataEngine` 最高切缝的单元测试，模拟构造最小化临时 SQLite DB（建 `gen_metadata` 表并写入测试 blob）以及包含 `invoke_subagent` 的 `transcript.jsonl`，断言 `get_convo_stats()` 输出的 `cluster` 结构正确性。

---

## 4. ⚠️ 架构雷区与避坑指南 (Traps & Watchouts)

* **绝对保护代码（严禁破坏）**：
  * [`proto_decoder.py`](file:///d:/agent/gemini/new/01/tools/token-capsule/proto_decoder.py) 是经过严格验证的纯 Python 二进制解码器，严禁做无谓重构或破坏其签名。
* **SQLite 并发与锁安全**：
  * 读取任何主会话或子智能体数据库时，**必须且只能**使用 URI `file:{path}?mode=ro` 只读模式连接，并加上短 `timeout=0.5`，防止在 Antigravity 正在写库时引发 `database is locked` 异常。
* **UI 线程安全与 Signal 解耦**：
  * `DataEngine` 运行在定时器或后台轮询中，所有数据传递必须通过 Qt `Signal(dict)` 发送到 UI 线程，严禁在 `DataEngine` 中直接调用 UI 控件的 setter。
* **物理窗口语义严禁污染**：
  * 绝对不要把子智能体的 Token 累加进顶部 256k 主进度条中！256k 物理条只能反映主会话当前活跃轮次 `activeContext`，否则会导致用户产生模型上下文溢出的误判。
* **容错与静默降级**：
  * 当主会话尚未派发任何子智能体（或 `transcript.jsonl` 不存在）时，`cluster` 自动设置 `subagents = []`，UI 优雅保持为传统单会话模式或展示“暂无活跃子智能体”，绝对不能抛出任何未捕获异常。

---

## 5. 🔄 关键数据流图解 (Dataflow Synopsis)

```
[定时器 300ms 触发]
       │
       ▼
[读取主会话 transcript.jsonl] ──(捕获 invoke_subagent / UUID / Role / State)
       │
       ▼
[检查主会话及各子智能体 .db-wal mtime]
       │
       ├─(均无变化) ➔ 直接跳过（0% CPU 消耗）
       │
       └─(有变动)
             │
             ▼
       [只读连接 SQLite] ➔ [读取各会话 gen_metadata]
             │
             ▼
       [proto_decoder 解码] ➔ [计算 Turn/Cumulative/Breakdown]
             │
             ▼
       [组装主会话指标 + cluster 聚合指标]
             │
             ▼ (Qt Signal: session_updated.emit(full_data))
       [CapsuleWindow 响应]
             ├── 紧凑模式 (A)：更新 Tab 1 双费用 + Tab 2 微仪表盘 & 手风琴列表
             └── 双翼模式 (C)：左翼刷新主会话卡片 + 右翼刷新实时雷达
```
