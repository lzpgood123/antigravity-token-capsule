# ADR 0001: Antigravity 活跃会话跟踪与 CDP 探针架构

## Status

Accepted

## Context

Google Antigravity 支持多窗口、后台子代理并发运行。原有的单日志轮询或全局数据库扫描机制存在严重的“会话跳变”问题——当后台有子智能体或定时任务运行时，监控窗口会频繁在不同会话之间闪烁，无法固定展示用户当前屏幕上正在专注查看的会话。

我们需要一种非侵入式、极低开销且能100%精准锁定“用户前台正视会话”的追踪方案。

## Decision

我们采用 **Chrome DevTools 协议 (CDP) 端口嗅探 + 只读 SQLite 无锁轮询** 架构：

1. **CDP 嗅探**：
   * 读取 Antigravity 运行生成的 `~/AppData/Roaming/Antigravity/DevToolsActivePort`。
   * 请求 `http://127.0.0.1:<port>/json`，过滤类型为 `page` 的活跃目标。
   * 从目标的 `url` 正则捕获会话 UUID（例如匹配 `/conversation/([a-f0-9\-]+)`）。
2. **只读轻量轮询**：
   * 在 `data_engine.py` 中以 300ms 定时器执行无阻塞探测。
   * 当检测到会话 UUID 变更或数据库修改时间（mtime）变化时，通过 URI `file:...sqlite?mode=ro` 只读连接并提取最新的 Proto Usage Blob。
3. **Qt Signal-Slot 解耦**：
   * 数据采集引擎与 UI 绘制完全解耦，计算完毕后通过 PySide6 `Signal(dict)` 推送至 `CapsuleWindow` 进行单帧重绘。

## Consequences

- **Positive**：
  * **零侵入性**：无需给 Antigravity 打补丁或挂载 DLL Hook，利用 Chromium 自带机制。
  * **完全杜绝跳变**：只跟踪当前用户鼠标/视野所在的活跃会话。
  * **极高刷新性能**：只读模式与 mtime 预检使得日常轮询的 CPU 开销趋近于 0%。
- **Trade-offs**：
  * 依赖 Antigravity 启动时暴露的 DevTools 调试端口文件；若端口文件因异常崩溃未生成，胶囊将进入重试等待状态。
