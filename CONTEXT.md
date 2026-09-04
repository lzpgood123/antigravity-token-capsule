# Domain Model: Token Capsule (Antigravity 监控胶囊)

本文件定义 `tools/token-capsule` 边界上下文内的统一领域语言与核心概念。任何针对此工具的工单、规格书或代码，必须使用本字典中的标准术语。

---

## 📖 核心概念与统一语言 (Glossary)

### 1. 活跃会话 (Active Session)
* **定义**：当前正在 Antigravity 前端窗口中处于活动焦点并被用户正在浏览查看的对话会话。
* **判定机制**：通过 CDP 探针获取当前活跃的 `target.url`，从中正则匹配截取会话 UUID。
* _Avoid_：不要称作 "最新会话" (Latest Session) 或 "后台任务" (Background Task)。即使后台有其他 Agent 在跑，监控胶囊也严格只跟随用户视野所在的 Active Session。

### 2. CDP 嗅探器 (CDP Port Sniffer)
* **定义**：通过读取本地 `DevToolsActivePort` 端口文件，向 Chrome DevTools 协议端点 `/json` 发起 HTTP 请求以捕获当前界面状态的探针模块。
* _Avoid_：不要称作 "网络爬虫" (Web Scraper) 或 "内存注入" (Memory Injector)。

### 3. 五大 Token 分段构成 (5-Segment Token Breakdown)
* **定义**：将一个对话交互轮次向大模型发送的完整上下文 Token 拆解为 5 项互不重叠的核心计量维度：
  1. **系统提示词 (System)**：系统内置指令与基础行为提示。
  2. **原生工具 (Tools)**：内置核心 API 与原生工具参数定义。
  3. **对话消息 (Messages)**：用户与助手之间的历史交互文本与结果。
  4. **MCP 扩展 (MCP)**：通过 Model Context Protocol 挂载的外部服务工具声明。
  5. **工程技能 (Skills)**：通过 Agent Skills 框架注入的上下文。
* _Avoid_：不要含糊统称为 "总 Token" (Total Tokens)，在分析和 UI 上必须区分分段构成。

### 4. 悬浮胶囊窗 (Capsule Window)
* **定义**：基于 PySide6 构建的置顶、半透明、无边框微型桌面小部件。支持鼠标无缝拖拽与展开详情面板。
* _Avoid_：不要称作 "主控制面板" (Dashboard) 或 "全屏窗口" (Full Window)。

### 5. 布局模式 (Layout Mode)
* **定义**：卡片展开状态下的双形态呈现策略，由托盘菜单提供实时切换与记忆：
  1. **紧凑单卡 (Compact Tabbed / 方案 A)**：默认 320px 宽度，通过「主会话」与「智能体集群」Tab 标签页切换。
  2. **展开双翼 (Dual-Wing Radar / 方案 C)**：680px 宽度左右并排，左翼为主会话，右翼为智能体集群实时雷达。
* _Avoid_：不要硬编码单一尺寸或破坏单卡紧凑性。

### 6. Proto Usage 二进制块 (Proto Usage Blob)
* **定义**：Google Antigravity 内部存储在 SQLite 数据库中的 Protocol Buffers 序列化用量统计数据块，由 `proto_decoder` 解码为结构化字典。
* _Avoid_：不要称作 "JSON 日志" 或 "纯文本统计"。

### 7. 主会话 (Primary Session)
* **定义**：用户直接交互并正视的核心会话，拥有独立的物理上下文窗口（如 256k 限制）。
* _Avoid_：不要与派生出的子任务混同。

### 8. 子智能体会话 (Subagent Session)
* **定义**：由主会话派生出的独立子任务会话，具备独立的全局唯一 UUID、独立的 SQLite 数据库文件及独立的物理上下文。
* _Avoid_：不要误认为是主会话上下文的一部分；Subagent 不挤占主会话的物理 256k 窗口。

### 9. 智能体集群 (Agent Cluster)
* **定义**：当前主会话在全生命周期内派生出的全部子智能体的逻辑集合，包含运行中（`running`）与已结束（`idle` / `done`）两个明确状态。
* _Avoid_：不要只计算活跃态而丢失已结束智能体的消耗历史。

### 10. 集群汇总用量 (Cluster Rollup Usage)
* **定义**：跨主会话及所有子智能体的累计 Token 与财务折算费用的全局聚合指标。
* _Avoid_：严禁将集群汇总 Token 直接代入主会话 256k 物理进度条计算百分比。

---

## 🏛️ 领域关系映射

```
[CDP Port Sniffer] ──(捕获当前焦点)──> [Primary Session (UUID)]
                                           │
                                           ├───────(派生/日志关联)──────┐
                                           │                          ▼
                                           ▼                  [Agent Cluster]
                             [Primary Session SQLite]        [Subagent SQLite * N]
                                           │                          │
                                           ▼                          ▼
                                   [Proto Usage Blob]        [Proto Usage Blob * N]
                                           │                          │
                                           ▼                          ▼
                                   [5-Segment Context]       [Subagent Metrics]
                                           │                          │
                                           └───────────┬──────────────┘
                                                       ▼
                                            [Cluster Rollup Usage]
                                                       │
                                                       ▼
                                     [Capsule Window (Tab View)]
                                     ├── Tab 1: 主会话 (物理窗口)
                                     └── Tab 2: 智能体集群 (列表与汇总)
```

