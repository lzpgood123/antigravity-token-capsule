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

## 📝 Git 提交规范 (Git Commit Guidelines)

所有提交必须严格遵循 **作用域式约定式提交 (Conventional Commits with Scope)**，以确保 Monorepo 内各工具的演进历史清晰可追溯：

### 1. 提交消息格式
```
<type>(<scope>): <subject>
```

* **`<type>`（必填）**：
  * `feat`: 新增工具或功能特性
  * `fix`: 修复缺陷或异常
  * `docs`: 仅文档更新（如 `README.md`, `CONTEXT.md`, ADR）
  * `refactor`: 代码重构（不改变功能也不修 Bug）
  * `perf`: 性能优化
  * `test`: 测试用例新增或调整
  * `chore`: 依赖更新、构建脚本、全局规范调整
* **`<scope>`（强制规范）**：
  * **工具级别变更**：必须使用具体工具目录名作为 scope，如 `token-capsule`、`<future-tool>`。
  * **全局或架构变更**：使用 `root`、`repo` 或 `gallery`。
* **`<subject>`（必填）**：简要说明改动内容，祈使句，不超过 72 个字符。

### 2. 常见场景范例
| 场景 | 推荐 Commit 示例 |
| :--- | :--- |
| 为特定工具新增特性 | `feat(token-capsule): 新增 Token 历史趋势折线图` |
| 修复特定工具的缺陷 | `fix(token-capsule): 修复 CDP 端口断开导致的闪退` |
| 调整特定工具的文档 | `docs(token-capsule): 补充启动参数说明与快捷键配置` |
| 新增一个独立工具 | `feat(clipboard-sync): 初始化剪贴板同步小工具四件套` |
| 更新全局规范与配置 | `chore(repo): 在 AGENTS.md 中增加 Git 提交规范` |
| 更新根目录画廊看板 | `docs(gallery): 登记新工具至 README.md 画廊表格` |

### 3. 原子提交准则 (Atomic Commits)
* **禁止跨工具混合提交**：一次 Commit 应当只聚焦于一个具体的工具或单一意图。严禁在同一提交中混入两个不相关工具的代码。
* **工单关联（可选）**：完成 `.scratch/` 工单时，可在消息中注明工单号，如 `feat(token-capsule): 优化托盘交互 (#01)`。

---

## Agent skills

### Issue tracker

Issues and specs are tracked as local markdown files within each tool's `.scratch/` directory (e.g. `tools/<tool-name>/.scratch/<feature-slug>/`). See `docs/agents/issue-tracker.md`.

### Triage labels

Using standard five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Multi-context repository layout guided by root `CONTEXT-MAP.md`. Tool-scoped domain glossary lives in `tools/<tool-name>/CONTEXT.md`, tool-scoped ADRs live in `tools/<tool-name>/docs/adr/`, and repository-wide decisions live in root `docs/adr/`. See `docs/agents/domain.md`.

---

## 🚫 流程规范：禁用内置 Planning 机制与启用 Spec-Driven Dev

### 1. 禁用 IDE 内置轻量级 Planning 机制
* **严禁生成内置 Plan 工件**：Agent 严禁自动创建或请求用户批准 `<planning_mode>` 自带的 `implementation_plan.md` 与 `walkthrough.md` 伪计划工件，禁止以此类轻量级文件替代严谨的工程设计。
* **禁止无谓阻塞挂起**：严禁在未触发正式 Spec 流程时擅自挂起并等待用户点击 "Proceed/Approve"。

### 2. 正式功能开发严格遵循 `/spec-driven-dev`
当用户启动新工具研发、重大功能迭代、或显式要求规范流程时，**必须 100% 严格执行** [`spec-driven-dev`](file:///C:/Users/lzpgood/.gemini/config/skills/spec-driven-dev/SKILL.md) 六阶段门禁体系：
* **Phase 0 (Bootstrap)**：维护 `.specify/memory/constitution.md`、`AGENTS.md` 与 `CONTEXT.md` 领域字典；
* **Phase 1 (Requirements Discovery)**：通过 `/grill-me` 深度对抗对齐需求，运行 `/speckit-specify` 产出 `specs/<feature>/spec.md`（仅限 WHAT/WHY，不涉及技术实现）；
* **Phase 2 (Design Exploration)**：若有技术不确定性先做 `/prototype` 原型，随后产出 `specs/<feature>/plan.md` 并通过宪法审查；
* **Phase 3 (Task Engineering)**：通过 `/speckit-tasks` 产出具备依赖排序的 `specs/<feature>/tasks.md`，运行 `/speckit-analyze` 进行跨工件一致性校验；
* **Phase 4 (TDD Implementation)**：对每个原子任务严格贯彻 **RED**（先写失败单测） $\to$ **GREEN**（最小代码通过） $\to$ **REFACTOR**（重构保持绿色）；
* **Phase 5 (Verify & Converge)**：两轴（规范与规格）并行 Review，并通过 `/speckit-converge` 闭环核验；
* **Phase 6 (Commit & Handoff)**：遵循作用域约定式提交并生成交接文档。

### 3. 日常指令快速通道 (Direct / Fast Path)
对于轻量缺陷修复、代码/日志诊断、说明文档编写、样式微调等单点指令，直接执行，迅速交付，不强加繁重仪式。
