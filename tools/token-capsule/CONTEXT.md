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

### 5. Proto Usage 二进制块 (Proto Usage Blob)
* **定义**：Google Antigravity 内部存储在 SQLite 数据库中的 Protocol Buffers 序列化用量统计数据块，由 `proto_decoder` 解码为结构化字典。
* _Avoid_：不要称作 "JSON 日志" 或 "纯文本统计"。

---

## 🏛️ 领域关系映射

```
[CDP Port Sniffer] ──(捕获当前焦点)──> [Active Session (UUID)]
                                           │
                                           ▼ (读取对应会话 SQLite)
[Capsule Window (UI)] <──(Signal 更新)── [Proto Usage Blob] ──> [5-Segment Breakdown]
```
