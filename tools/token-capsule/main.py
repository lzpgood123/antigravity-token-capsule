import sys
import os
import time
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction, QPixmap, QColor, QPainter
from PySide6.QtCore import Qt

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from data_engine import DataEngine
from capsule_ui import CapsuleWindow

def create_tray_icon():
    """生成一个简单的纯色小图标用于托盘"""
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
    log_file = os.path.join(current_dir, "capsule.log")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"=== Starting at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
    except Exception:
        pass
    app = QApplication(sys.argv)
    app.setApplicationName("AntigravityTokenCapsule")
    app.setQuitOnLastWindowClosed(False)

    # 1. 实例化主窗口与数据引擎
    window = CapsuleWindow()
    engine = DataEngine()
    engine.session_updated.connect(window.update_data)
    engine.recent_list_updated.connect(window.update_recent_list)
    window.convo_selected.connect(engine.switch_to_conversation)

    # 2. 系统托盘图标
    tray = QSystemTrayIcon(create_tray_icon(), app)
    tray.setToolTip("Antigravity Token 监控胶囊")

    menu = QMenu()
    act_toggle = QAction("显示/隐藏", menu)
    act_toggle.triggered.connect(lambda: window.setVisible(not window.isVisible()))
    menu.addAction(act_toggle)

    act_reset = QAction("重置位置到右上角", menu)
    act_reset.triggered.connect(lambda: window.move(
        app.primaryScreen().availableGeometry().width() - 290, 60
    ))
    menu.addAction(act_reset)

    menu.addSeparator()
    act_quit = QAction("退出", menu)
    act_quit.triggered.connect(app.quit)
    menu.addAction(act_quit)

    tray.setContextMenu(menu)
    tray.show()

    # 3. 显示悬浮胶囊
    window.show()

    try:
        sys.exit(app.exec())
    except Exception as e:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"Exception in exec: {e}\n")

if __name__ == "__main__":
    main()
