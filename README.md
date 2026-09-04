# 💊 Antigravity Token 监控胶囊 (Token Capsule)

专为 **Google Antigravity** 打造的实时桌面悬浮 Token 监控伴生工具。通过 Chrome DevTools 协议 (CDP) 毫秒级锁定用户正在浏览的活跃会话，实时统计并图形化展示上下文的 5 大分段构成、当前 Token 消耗以及财务计费估算。

---

## 🌟 核心特性

1. **会话精准锁定 (CDP Sniffing)**：
   * 自动探测 `DevToolsActivePort` 并与 Antigravity 前端通信，仅跟踪当前前台活跃会话，杜绝后台多智能体干扰。
2. **5 大分段精准透视 (Token Breakdown)**：
   * 系统提示词 (System Prompt)、原生工具声明 (Native Tools)、对话历史消息 (Chat Messages)、外部 MCP 服务 (Model Context Protocol)、专有 Agent Skills。
3. **真实物理性能指标 (Real-time Performance)**：
   * 原生解码 Protobuf 毫秒级 TTFT（首 token 耗时）与推理输出速度（`tok/s`），提供当轮数据与全会话历史均值。
4. **原生 Windows 桌面极简交互与独立 EXE**：
   * 无边框半透明悬浮药丸造型，支持鼠标自由拖拽。
   * 支持一键切换最近会话或开启/关闭自动跟随。
   * 专属高清彩色胶囊应用图标（`capsule.ico`）。
   * 系统托盘常驻，支持 **「开机自动启动」**、**「窗口总在最前」** 勾选切换、位置重置（右上角）与静默后台运行。

---

## 🚀 运行与启动方式

### 方式 1：独立编译可执行文件（推荐日常使用，无需 Python）
* **单文件版（即拷即用）**：直接运行 `dist\onefile\token-capsule.exe`。
* **绿色文件夹版（毫秒秒开）**：直接运行 `dist\onedir\token-capsule\token-capsule.exe`。

### 方式 2：Python 源码无黑框后台运行
双击：
```
start_capsule_silent.vbs
```

### 方式 3：标准控制台启动（开发者调试）
双击：
```bat
start_capsule.bat
```

---

## 🔨 一键编译打包为 EXE (Build)

工具配备了全自动化编译脚本，支持一键生成专属图标与双模式 EXE：
```bat
build_exe.bat
```
编译产物输出位置：
* 单文件版：`dist\onefile\token-capsule.exe`
* 目录版：`dist\onedir\token-capsule\token-capsule.exe`

---

## 📦 环境依赖与安装（源码开发）

推荐在当前目录下创建独立虚拟环境：
```powershell
cd tools/token-capsule
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🏗️ 核心代码架构

* [`main.py`](main.py)：Qt 应用程序主入口，初始化托盘菜单、开机自启注册表管理与主窗口。
* [`capsule_ui.py`](capsule_ui.py)：PySide6 悬浮窗口绘制，支持拖拽、展开详情折叠卡片及会话下拉切换。
* [`data_engine.py`](data_engine.py)：CDP 端口探针、SQLite 预写日志（`.db-wal`）毫秒级轮询与 Proto Usage 数据解码引擎。
* [`proto_decoder.py`](proto_decoder.py)：纯 Python 独立 Protobuf 解码模块，实现零耦合沙盒自给自足。
* [`generate_icon.py`](generate_icon.py)：自动生成高清胶囊图标（`capsule.ico`）。
* [`build_exe.bat`](build_exe.bat)：Windows 一键自动化打包脚本。
* [`CONTEXT.md`](CONTEXT.md)：该工具专属的领域概念定义与统一语言。
* [`docs/adr/`](docs/adr/)：工具关键技术选型决策记录。
