# Issue 04: 托盘菜单布局切换与设置持久化

Status: ready-for-agent
Type: task

## Description
在 `main.py` 及配置文件中落地布局模式控制：
1. 系统托盘右键菜单中新增「📐 布局模式 (Layout Mode)」子菜单：
   - `● 紧凑单卡 (方案 A · 默认)`
   - `○ 展开双翼 (方案 C · 雷达)`
2. 与主窗口连接，点击菜单项时实时切换 Capsule 窗口布局模式。
3. 扩展设置管理模块，支持将 `layout_mode` 持久化保存至 `~/.gemini/antigravity/capsule_settings.json`，在启动时自动读取并应用。

## Acceptance Criteria
- 右键点击托盘菜单可即时无缝切换单卡 / 双翼布局。
- 关闭或重启应用后，布局模式设置不丢失。
