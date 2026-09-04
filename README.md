# 💊 Antigravity Token 监控胶囊 (Token Capsule)

> 📖 **官方完整双语文档**：[中文版主文档 (README.md)](../../README.md) | [English Documentation (README_EN.md)](../../README_EN.md)

专为 **Google Antigravity** 打造的实时桌面悬浮 Token 监控伴生工具。通过 Chrome DevTools 协议 (CDP) 毫秒级锁定用户正在浏览的活跃会话，实时统计并图形化展示上下文的 5 大分段构成、当前 Token 消耗以及财务计费估算。

---

## 🌟 核心特性

1. **会话精准锁定 (CDP Sniffing)**：
   * 自动探测 `DevToolsActivePort` 并与 Antigravity 前端通信，仅跟踪当前前台活跃会话，杜绝后台多智能体干扰。
2. **5 大分段精准透视 (Token Breakdown)**：
   * 系统提示词 (System Prompt)、原生工具声明 (Native Tools)、对话历史消息 (Chat Messages)、外部 MCP 服务 (Model Context Protocol)、专有 Agent Skills。
3. **真实物理性能指标 (Real-time Performance)**：
   * 原生解码 Protobuf 毫秒级 TTFT（首 token 耗时）与推理输出速度（`tok/s`），提供当轮数据与全会话历史均值。
4. **子智能体集群监控与双计费联动 (Subagent Cluster Monitoring)**：
   * 自动解析会话执行轨迹（`transcript.jsonl`），动态捕获派生的子智能体（Subagents）及其业务角色。
   * 业界率先支持 **L1 ➔ L2 ➔ L3 多层级嵌套树形级联监控**，节点自身计费独立核算，派生子任务自动级联向上汇总。
   * 毫秒级增量轮询各子智能体的 SQLite / WAL 数据库，聚合计算集群总 Token 与财务花费。
   * 支持双计费联动透视：主会话计费卡片同步展示 `主会话费用 (含集群: $X.XXX)`。
   * 手风琴卡片状态智能记忆防抖，轮询重绘不回弹、不抖动，消除历史日志干扰。
   * 迷你药丸收起态支持实时后台活跃智能体感知（如 `· 🤖2`）。
5. **混合双布局体系 (Hybrid Layout Modes)**：
   * **紧凑单卡 (Compact Tabbed / 方案 A)**：320px 宽度，顶部分段 Tab 切换「💬 主会话」与「🤖 智能体集群 • N」，支持子智能体手风琴卡片平滑展开查看输入/生成/思考/首字响应与速度细项。
   * **展开双翼 (Dual-Wing Radar / 方案 C)**：680px 宽度，左右分屏并列展示主会话物理卡片与集群实时雷达，底部配备全局双计费总额条。
6. **原生 Windows 桌面极简交互与独立 EXE**：
   * 无边框半透明悬浮药丸造型，支持鼠标自由拖拽与收起/展开。
   * 支持一键切换最近会话或开启/关闭自动跟随。
   * 专属高清彩色胶囊应用图标（`capsule.ico`）。
   * **5 套精美主题实时热切**：支持极简明亮、深邃暗夜、磨砂极光、赛博黑客、暖阳纸墨 5 大主题风格，配置持久化记忆。
   * **功能丰富的系统托盘**：系统右下角小图标右键菜单支持 **「📐 布局模式」**（单卡/双翼）、**「🎨 主题风格」**、**「开机自动启动」**、**「窗口总在最前」** 勾选切换、位置重置（右上角）与静默退出。配置自动持久化保存于 `capsule_settings.json`。

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

工具配备了全自动化编译脚本，支持一键完成高清图标生成、单文件、多文件、绿色 ZIP 及 Inno Setup 安装包的四合一构建：
```bat
build_exe.bat
```
编译产物输出位置：
* 👑 **Windows 安装包**：`dist\installer\token-capsule-Setup-v1.1.0.exe`（自动关联桌面与开始菜单图标，免管理员权限）
* 🧰 **绿色免安装 ZIP**：`dist\zip\token-capsule-v1.1.0-windows-x64.zip`（解压即用，毫秒秒开）
* ⚡ **单文件独立版**：`dist\onefile\token-capsule.exe`（单文件拷走即用，含临时解压）
* 📂 **绿色目录调试版**：`dist\onedir\token-capsule\`（本地开发测试秒开目录）

> 💡 **提示**：安装包构建基于 Inno Setup 6 脚本 [`installer.iss`](installer.iss)。若本地已安装 Inno Setup，脚本会自动检测并编译生成安装包；未安装时会自动跳过安装包步骤，不影响其他产物。

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
