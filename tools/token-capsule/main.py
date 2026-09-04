import sys
import os
import time
import winreg
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction, QPixmap, QColor, QPainter
from PySide6.QtCore import Qt

# 处理 PyInstaller 打包环境与开发环境路径
if getattr(sys, 'frozen', False):
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    app_exe = sys.executable
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_exe = f'"{sys.executable}" "{os.path.abspath(__file__)}"'

if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from data_engine import DataEngine
from capsule_ui import CapsuleWindow

class StartupManager:
    """管理 Windows 开机自启注册表项 (HKCU)"""
    REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "AntigravityTokenCapsule"

    @classmethod
    def is_enabled(cls) -> bool:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, cls.APP_NAME)
                return True
        except Exception:
            return False

    @classmethod
    def set_enabled(cls, enable: bool) -> bool:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, cls.REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
                if enable:
                    winreg.SetValueEx(key, cls.APP_NAME, 0, winreg.REG_SZ, app_exe)
                else:
                    try:
                        winreg.DeleteValue(key, cls.APP_NAME)
                    except FileNotFoundError:
                        pass
            return True
        except Exception:
            return False

def get_app_icon():
    ico_path = os.path.join(base_dir, "capsule.ico")
    if os.path.exists(ico_path):
        return QIcon(ico_path)
    # 回退纯色绘制
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#10b981"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 12, 12)
    painter.end()
    return QIcon(pixmap)

def main():
    log_dir = os.path.dirname(app_exe.strip('"')) if getattr(sys, 'frozen', False) else base_dir
    log_file = os.path.join(log_dir, "capsule.log")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"=== Starting at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName("AntigravityTokenCapsule")
    app.setQuitOnLastWindowClosed(False)

    icon = get_app_icon()
    app.setWindowIcon(icon)

    window = CapsuleWindow()
    engine = DataEngine()
    engine.session_updated.connect(window.update_data)
    engine.recent_list_updated.connect(window.update_recent_list)
    window.convo_selected.connect(engine.switch_to_conversation)

    tray = QSystemTrayIcon(icon, app)
    tray.setToolTip("Antigravity Token 监控胶囊")

    menu = QMenu()

    act_toggle = QAction("显示/隐藏", menu)
    act_toggle.triggered.connect(lambda: window.setVisible(not window.isVisible()))
    menu.addAction(act_toggle)

    act_ontop = QAction("窗口总在最前", menu, checkable=True)
    act_ontop.setChecked(True)
    def toggle_ontop(checked):
        window.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, checked)
        window.show()
    act_ontop.toggled.connect(toggle_ontop)
    menu.addAction(act_ontop)

    act_autostart = QAction("开机自动启动", menu, checkable=True)
    act_autostart.setChecked(StartupManager.is_enabled())
    act_autostart.toggled.connect(lambda checked: StartupManager.set_enabled(checked))
    menu.addAction(act_autostart)

    act_reset = QAction("重置位置到右上角", menu)
    def reset_pos():
        screen = app.primaryScreen().availableGeometry()
        window.move(screen.width() - 330, 50)
        window.show()
    act_reset.triggered.connect(reset_pos)
    menu.addAction(act_reset)

    menu.addSeparator()
    act_quit = QAction("退出", menu)
    act_quit.triggered.connect(app.quit)
    menu.addAction(act_quit)

    tray.setContextMenu(menu)
    tray.show()

    window.show()

    try:
        sys.exit(app.exec())
    except Exception as e:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"Exception in exec: {e}\n")

if __name__ == "__main__":
    main()
