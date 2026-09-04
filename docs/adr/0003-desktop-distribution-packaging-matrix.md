# ADR 0003: 桌面客户端三维分发矩阵选型 (Desktop Distribution Packaging Matrix)

## Status

Accepted

## Context

在为 Windows 桌面用户分发 **Antigravity Token Capsule** 时，我们在启动性能、便携度与用户交付体验上面临经典权衡：

1. **单文件版 (`--onefile`)**：
   * 优势：分发极其简便，仅单个独立 `.exe` 文件（约 44MB），即拷即用。
   * 痛点：每次双击运行时，必须在后台将数十兆的运行时与 Qt 依赖解压至系统临时目录（`AppData\Local\Temp\_MEIxxxxxx`），带来明显的 **2~3 秒启动延迟**，且频繁读写临时目录可能触发部分安全防护软件的拦截。
2. **多文件目录版 (`--onedir`)**：
   * 优势：直接读取邻近目录 DLL，拥有 **0.2 秒级瞬间秒开** 的极致响应体验。
   * 痛点：包含数百个散落文件及 `_internal/` 依赖子目录，无法作为单个直链文件直接提供给非专业用户下载。
3. **传统 MSI 安装包 (Windows Installer)**：
   * 优势：微软系统服务管理，支持企业组策略静默分发。
   * 痛点：构建门槛高（WiX Toolset 需编写复杂晦涩的 XML 与 GUID），向导界面传统僵化，针对轻量个人开发小工具过重。

## Decision

我们确立了以 **Inno Setup 免提权安装包为核心、便携 ZIP 与独立 EXE 为补充的三维分发矩阵**：

1. **主力旗舰分发：Inno Setup 专业安装包 (`token-capsule-Setup-vX.Y.Z.exe`)**：
   * **免 UAC 管理员提权**：默认安装路径采用 `{localappdata}\Programs\AntigravityTokenCapsule`，设置 `PrivilegesRequired=lowest`，普通用户无感静默安装，绝不弹出黄黑警告框。
   * **秒开底层封装**：安装包在安装时一次性释放高性能的 `onedir` 多文件结构，并在桌面与开始菜单创建高清图标快捷方式。用户日常双击桌面图标启动时，直接享受 **0.2 秒级毫秒秒开**。
   * **极致体积压缩**：使用 `lzma2/ultra64` 固实压缩算法，将 100MB+ 的目录打包压缩为仅 **~31.9 MB** 的小巧体积。
   * **标准生命周期**：在 Windows「设置 ➔ 已安装的应用」中注册干净的卸载程序（Uninstall），支持一键无残留彻底清除。

2. **极客免装分发：绿色便携 ZIP 包 (`token-capsule-vX.Y.Z-windows-x64.zip`)**：
   * 完整打包 `onedir` 目录，供偏好免安装向导的开发者下载后解压到任意工作区直接秒开运行。

3. **便携应急分发：单文件独立 EXE (`token-capsule.exe`)**：
   * 持续保留 PyInstaller `--onefile` 构建产物，作为即拷即用的便携式单文件分发方式。

4. **一键全流程自动化构建 (`build_exe.bat`)**：
   * 在编译脚本中顺序串联 `onedir ➔ onefile ➔ PowerShell Compress-Archive ➔ Inno Setup ISCC.exe`，实现一次执行、四种交付产物全自动输出。

## Consequences

- **Positive**：
  * **兼得便携与性能**：用户下载单文件安装包，安装后运行毫秒秒开的多文件程序，兼顾了下载体验与日常使用体验。
  * **零权限门槛**：安装在用户 AppData 目录，无需管理员权限，兼容企业严格权限受控电脑。
  * **完备工程闭环**：提供了正规的卸载程序与快捷方式管理，显著提升开源工具的专业度与可靠感。
- **Trade-offs**：
  * 构建机环境需可选配置 Inno Setup 编译器（若本地未安装 `ISCC.exe`，构建脚本会自动打印提示并优雅跳过安装包编译，不影响其他产物生成）。
