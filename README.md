# 🧰 Antigravity Tools Monorepo

本仓库为 **Google Antigravity 多工具沙盒单体仓库**，集中管理所有通过 Antigravity 研发的桌面悬浮小组件、CLI 自动化脚本、MCP 协议服务及后台伴生应用（Sidecars）。

所有工具均位于 `tools/` 目录下，遵循**零耦合独立沙盒**原则与工业级四件套脚手架标准。

---

## 🎨 工具画廊看板 (Tool Gallery)

| 工具名称 | 形态分类 | 核心功能简介 | 一键启动命令 | 状态 | 详情文档 |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **`token-capsule`** | GUI 桌面悬浮窗 | 实时嗅探 Antigravity 会话 CDP 端口，无锁轮询展示 Token 5大分段构成与计费估算 | `.\tools\token-capsule\start_capsule.bat` | 🟢 Active | [文档](tools/token-capsule/README.md) |

*(注：新工具加入时，AI 代理或维护者必须在此表格中完成同步登记)*

---

## 🏛️ 仓库架构与核心规约

* **行为准则**：详见 [`AGENTS.md`](AGENTS.md)。
* **多上下文路由**：详见 [`CONTEXT-MAP.md`](CONTEXT-MAP.md)。
* **全局架构决策**：详见 [`docs/adr/`](docs/adr/)。
* **工程技能与工单流转**：详见 [`docs/agents/`](docs/agents/)。

---

## 🛠️ 新建工具标准规范 (Micro-Tool 4-Piece Standard)

任何在 `tools/` 下新建的工具，必须具备以下标准四件套：
1. **`README.md`**：工具功能说明、配置项与使用指南。
2. **依赖清单**：Python 项目配备 `requirements.txt`；Node 项目配备 `package.json`。
3. **一键启动脚本**：Windows 双击启动脚本（`start_<tool>.bat` 或 `run.ps1`，自动适配同目录 `.venv`）。
4. **独立程序入口**：标准的执行入口文件（如 `main.py`、`cli.py` 或 `index.js`）。
