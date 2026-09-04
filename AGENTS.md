# AGENTS.md

## Repository Overview

This repository is an **Antigravity Multi-Tool Monorepo**. It serves as the centralized workspace for utility tools, desktop widgets, CLI scripts, MCP servers, and background sidecars built with and for Google Antigravity.

All operational tools reside as independent subdirectories under `tools/` (e.g., `tools/<tool-name>/`).

---

## 🛡️ Sandbox & Scaffolding Rules (沙盒隔离与脚手架规范)

### 1. 零耦合独立沙盒 (Zero-Coupling Sandbox)
* **独立自治**：每个位于 `tools/<tool-name>/` 的工具必须保持自给自足，拥有独立的技术栈选型、依赖管理和启动脚本。
* **禁止跨工具依赖**：严禁在 `tools/A` 中直接相对引用或硬编码导入 `tools/B` 中的代码。若需共用库，未来需抽象为独立的公共包或通过标准协议（如 CLI/HTTP/MCP）解耦。
* **环境隔离**：Python 工具推荐在子目录下自建 `.venv`；Node 工具自建 `node_modules`。两者均由根目录 `.gitignore` 保护，严禁提交到版本库。

### 2. 工业级微工具四件套 (Standard 4-Piece Scaffolding)
当 Agent 创建或重构任何工具时，**必须强制配备**以下四件套：
1. **`README.md`**：工具功能介绍、核心技术原理、环境依赖、配置项与使用方法。
2. **依赖清单**：Python 项目提供 `requirements.txt`；Node 项目提供 `package.json`。
3. **一键启动脚本**：提供 Windows 免配置双击启动脚本（如 `start_<tool>.bat` 或 `run.ps1`）。脚本应优先检测并激活本地 `.venv`，不存在时优雅回退至全局解释器。
4. **明确执行入口**：提供标准入口文件（如 `main.py`、`index.js` 或 `cli.py`）。

### 3. 工具画廊同步登记 (Tool Gallery Registry)
每当新增工具或工具状态发生变化时，Agent **必须同步更新** 根目录 `README.md` 中的【工具画廊看板 (Tool Gallery)】表格。

---

## ⚙️ Environment & Platform Guidelines

* **操作系统**：Windows 10/11，默认终端为 PowerShell (`pwsh`)。
* **字符编码**：所有文件与脚本必须采用 `UTF-8` 无 BOM 编码，批处理脚本头部使用 `chcp 65001 >nul`。
* **GUI 开发规范**：桌面悬浮窗或托盘应用优先采用 `PySide6`，耗时数据采集与轮询必须置于非主线程或通过异步定时器处理，严禁阻塞 UI 事件循环。

---

## Agent skills

### Issue tracker

Issues and specs are tracked as local markdown files within each tool's `.scratch/` directory (e.g. `tools/<tool-name>/.scratch/<feature-slug>/`). See `docs/agents/issue-tracker.md`.

### Triage labels

Using standard five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Multi-context repository layout guided by root `CONTEXT-MAP.md`. Tool-scoped domain glossary lives in `tools/<tool-name>/CONTEXT.md`, tool-scoped ADRs live in `tools/<tool-name>/docs/adr/`, and repository-wide decisions live in root `docs/adr/`. See `docs/agents/domain.md`.
