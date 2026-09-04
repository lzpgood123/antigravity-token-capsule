# 💊 Antigravity Token 监控胶囊 (Token Capsule)

专为 **Google Antigravity** 打造的实时桌面悬浮 Token 监控伴生工具。通过 Chrome DevTools 协议 (CDP) 毫秒级锁定用户正在浏览的活跃会话，实时统计并图形化展示上下文的 5 大分段构成、当前 Token 消耗以及财务计费估算。

---

## 🌟 核心特性

1. **会话精准锁定 (CDP Sniffing)**：
   * 自动探测 `DevToolsActivePort` 并与 Antigravity 前端通信，仅跟踪当前前台活跃会话，杜绝后台多智能体干扰。
2. **5 大分段精准透视 (Token Breakdown)**：
   * 系统提示词 (System Prompt)
   * 原生工具声明 (Native Tools)
   * 对话历史消息 (Chat Messages)
   * 外部 MCP 服务 (Model Context Protocol)
   * 专有 Agent Skills
3. **原生 Windows 桌面极简交互**：
   * 无边框半透明悬浮药丸造型，支持鼠标自由拖拽。
   * 支持一键切换最近会话或开启/关闭自动跟随。
   * 系统托盘常驻，支持位置重置（右上角）与静默后台运行。

---

## 🚀 快速启动

### 方式 1：标准控制台启动（推荐初次运行或调试）
双击根目录脚本或在终端中执行：
```bat
start_capsule.bat
```
*(脚本会自动检测同目录 `.venv`，若不存在则调用系统 Python)*

### 方式 2：无黑框静默后台运行
双击：
```
start_capsule_silent.vbs
```

---

## 📦 环境依赖与安装

推荐在当前目录下创建独立虚拟环境：
```powershell
cd tools/token-capsule
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🏗️ 核心代码架构

* [`main.py`](main.py)：Qt 应用程序主入口，初始化托盘菜单与主窗口。
* [`capsule_ui.py`](capsule_ui.py)：PySide6 悬浮窗口绘制，支持拖拽、展开详情折叠卡片及会话下拉切换。
* [`data_engine.py`](data_engine.py)：CDP 端口探针、SQLite 活跃会话监测与 Proto Usage 数据解码引擎。
* [`CONTEXT.md`](CONTEXT.md)：该工具专属的领域概念定义与统一语言。
* [`docs/adr/`](docs/adr/)：工具关键技术选型决策记录。
