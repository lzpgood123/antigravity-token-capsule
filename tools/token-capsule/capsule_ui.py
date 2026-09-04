import json
import os
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import (
    QColor, QCursor, QGuiApplication, QPainter, QPainterPath
)
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QApplication, QScrollArea, QSizePolicy
)
from data_engine import fmt_tokens

THEME_CONFIGS = {
    "light": {
        "name": "极简明亮 (Pure Light)",
        "card_bg": "#ffffff",
        "pill_bg": "#ffffff",
        "border": "#e2e8f0",
        "text_main": "#0f172a",
        "text_sub": "#64748b",
        "item_label": "#334155",
        "item_val": "#64748b",
        "accent": "#2563eb",
        "hover_bg": "#f1f5f9",
        "combo_bg": "#f8fafc",
        "cost_color": "#d97706",
        "bar_bg": "#f1f5f9",
        "sep_bg": "#f1f5f9",
        "badge_bg": "#eff6ff",
    },
    "dark": {
        "name": "深邃暗夜 (Obsidian Dark)",
        "card_bg": "#0f172a",
        "pill_bg": "#0f172a",
        "border": "#334155",
        "text_main": "#f8fafc",
        "text_sub": "#94a3b8",
        "item_label": "#cbd5e1",
        "item_val": "#94a3b8",
        "accent": "#60a5fa",
        "hover_bg": "#1e293b",
        "combo_bg": "#1e293b",
        "cost_color": "#fbbf24",
        "bar_bg": "#1e293b",
        "sep_bg": "#334155",
        "badge_bg": "#1e293b",
    },
    "glass": {
        "name": "磨砂极光 (Frosted Aurora)",
        "card_bg": "rgba(240, 249, 255, 0.94)",
        "pill_bg": "rgba(240, 249, 255, 0.94)",
        "border": "rgba(186, 230, 253, 0.9)",
        "text_main": "#0369a1",
        "text_sub": "#0284c7",
        "item_label": "#0f172a",
        "item_val": "#0369a1",
        "accent": "#0284c7",
        "hover_bg": "rgba(224, 242, 254, 0.8)",
        "combo_bg": "rgba(255, 255, 255, 0.9)",
        "cost_color": "#d97706",
        "bar_bg": "rgba(224, 242, 254, 0.8)",
        "sep_bg": "rgba(186, 230, 253, 0.7)",
        "badge_bg": "rgba(224, 242, 254, 0.8)",
    },
    "cyberpunk": {
        "name": "赛博黑客 (Matrix Neon)",
        "card_bg": "#080c14",
        "pill_bg": "#080c14",
        "border": "#00f0ff",
        "text_main": "#00ff9d",
        "text_sub": "#00f0ff",
        "item_label": "#c7d2fe",
        "item_val": "#00f0ff",
        "accent": "#00ff9d",
        "hover_bg": "#142238",
        "combo_bg": "#0f1a2e",
        "cost_color": "#facc15",
        "bar_bg": "#16233b",
        "sep_bg": "rgba(0, 240, 255, 0.4)",
        "badge_bg": "#0f1a2e",
    },
    "warm": {
        "name": "暖阳纸墨 (Warm Paper)",
        "card_bg": "#faf7f2",
        "pill_bg": "#faf7f2",
        "border": "#e7dfd5",
        "text_main": "#292524",
        "text_sub": "#78716c",
        "item_label": "#44403c",
        "item_val": "#78716c",
        "accent": "#b45309",
        "hover_bg": "#eee5d8",
        "combo_bg": "#f5efe6",
        "cost_color": "#d97706",
        "bar_bg": "#eee5d8",
        "sep_bg": "#e7dfd5",
        "badge_bg": "#f5efe6",
    }
}

def get_settings_file_path():
    app_dir = os.path.expanduser("~/.gemini/antigravity")
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, "capsule_settings.json")

def get_theme_file_path():
    app_dir = os.path.expanduser("~/.gemini/antigravity")
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, "capsule_theme.json")

def load_saved_settings() -> dict:
    settings_path = get_settings_file_path()
    theme_path = get_theme_file_path()
    settings = {"theme": "light", "layout_mode": "compact"}

    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("theme") in THEME_CONFIGS:
                    settings["theme"] = data["theme"]
                if data.get("layout_mode") in ("compact", "dual_wing"):
                    settings["layout_mode"] = data["layout_mode"]
                return settings
        except Exception:
            pass
    elif os.path.exists(theme_path):
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("theme") in THEME_CONFIGS:
                    settings["theme"] = data["theme"]
        except Exception:
            pass
    return settings

def save_settings(settings: dict):
    path = get_settings_file_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception:
        pass

def load_saved_theme() -> str:
    return load_saved_settings().get("theme", "light")

def save_theme(theme_name: str):
    st = load_saved_settings()
    st["theme"] = theme_name
    save_settings(st)

def make_theme_qss(cfg):
    return f"""
QWidget#CardRoot {{
    background-color: {cfg['card_bg']};
    border: 1px solid {cfg['border']};
    border-radius: 16px;
}}

QWidget#PillRoot {{
    background-color: {cfg['pill_bg']};
    border: 1px solid {cfg['border']};
    border-radius: 18px;
}}

QLabel {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'SF Pro Text', Roboto, sans-serif;
    color: {cfg['text_main']};
}}

QLabel#TitleLabel {{
    color: {cfg['text_main']};
    font-size: 15px;
    font-weight: 700;
}}

QLabel#HeroPct {{
    color: {cfg['text_main']};
    font-size: 26px;
    font-weight: 800;
}}

QLabel#HeroSub {{
    color: {cfg['text_sub']};
    font-size: 13px;
    font-weight: 500;
    padding-bottom: 2px;
}}

QPushButton#CloseBtn {{
    background: transparent;
    color: {cfg['text_sub']};
    border: none;
    font-size: 14px;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 4px;
}}
QPushButton#CloseBtn:hover {{
    color: {cfg['text_main']};
    background-color: {cfg['hover_bg']};
}}

QComboBox#ConvPicker {{
    background-color: {cfg['combo_bg']};
    color: {cfg['accent']};
    border: 1px solid {cfg['border']};
    border-radius: 6px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: 600;
}}
QComboBox#ConvPicker::drop-down {{
    border: none;
    width: 14px;
}}
QComboBox#ConvPicker QAbstractItemView {{
    background-color: {cfg['card_bg']};
    color: {cfg['text_main']};
    selection-background-color: {cfg['hover_bg']};
    selection-color: {cfg['accent']};
    border: 1px solid {cfg['border']};
    outline: none;
    font-size: 11px;
}}

/* Segmented Tab Bar */
QFrame#TabBar {{
    background-color: {cfg['combo_bg']};
    border: 1px solid {cfg['border']};
    border-radius: 8px;
    padding: 2px;
}}

QPushButton.TabBtn {{
    background-color: transparent;
    color: {cfg['text_sub']};
    border: none;
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 11px;
    font-weight: 600;
}}

QPushButton.TabBtn[active="true"] {{
    background-color: {cfg['card_bg']};
    color: {cfg['text_main']};
}}

QPushButton.TabBtn:hover {{
    color: {cfg['text_main']};
}}

QPushButton.TabBtn:disabled {{
    color: {cfg['border']};
}}

/* Micro Dashboard Banner */
QFrame#MicroDashboard {{
    background-color: {cfg['combo_bg']};
    border: 1px solid {cfg['border']};
    border-radius: 10px;
    padding: 6px 10px;
}}

/* Subagent Cards & Accordion */
QFrame.SubagentCard {{
    background-color: {cfg['combo_bg']};
    border: 1px solid {cfg['border']};
    border-radius: 9px;
}}

QFrame.SubagentCard:hover {{
    border: 1px solid {cfg['accent']};
    background-color: {cfg['hover_bg']};
}}

QFrame#SubagentDetail {{
    background-color: {cfg['card_bg']};
    border-top: 1px solid {cfg['border']};
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
    padding: 6px;
}}

QScrollArea#SubagentScrollArea {{
    background: transparent;
    border: none;
}}

QScrollArea#SubagentScrollArea > QWidget > QWidget {{
    background: transparent;
}}

QLabel.SubagentSub {{
    font-size: 9px;
    color: {cfg['text_sub']};
}}

QLabel.SubagentDetailLabel {{
    font-size: 10px;
    color: {cfg['text_sub']};
}}

QLabel.SubagentDetailVal {{
    font-size: 10px;
    font-weight: 600;
    color: {cfg['text_main']};
}}

QLabel.SubagentAction {{
    font-size: 9px;
    color: {cfg['text_sub']};
    margin-top: 2px;
}}

QLabel#SubagentCost {{
    font-size: 10px;
    font-weight: 600;
    color: {cfg['cost_color']};
}}

QLabel.ItemLabel, QLabel[class="ItemLabel"] {{
    color: {cfg['item_label']};
    font-size: 13px;
    font-weight: 500;
}}
QLabel.ItemVal, QLabel[class="ItemVal"] {{
    color: {cfg['item_val']};
    font-size: 13px;
    font-weight: 600;
}}

QLabel#PillText {{
    color: {cfg['text_main']};
    font-size: 12px;
    font-weight: 600;
}}
QLabel#PillCost {{
    color: {cfg['cost_color']};
    font-size: 12px;
    font-weight: 700;
}}
"""

class SegmentedProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(8)
        self.segments = []
        self.bg_color = QColor("#f1f5f9")

    def set_bg_color(self, color_str):
        self.bg_color = QColor(color_str)
        self.update()

    def set_segments(self, segments):
        self.segments = segments
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        painter.setBrush(self.bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 4, 4)

        path = QPainterPath()
        path.addRoundedRect(rect, 4, 4)
        painter.setClipPath(path)

        total_w = rect.width()
        current_x = 0
        for frac, color in self.segments:
            seg_w = max(int(frac * total_w), 2 if frac > 0.002 else 0)
            if seg_w > 0:
                painter.fillRect(current_x, 0, seg_w, rect.height(), color)
                current_x += seg_w

class SubagentCardWidget(QFrame):
    def __init__(self, agent_data: dict, parent=None):
        super().__init__(parent)
        self.agent_data = agent_data
        self.setObjectName("SubagentCard")
        self.setProperty("class", "SubagentCard")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.init_ui()

    def init_ui(self):
        card_l = QVBoxLayout(self)
        card_l.setContentsMargins(8, 7, 8, 7)
        card_l.setSpacing(4)

        # 1. Summary row
        summary_row = QHBoxLayout()
        summary_row.setContentsMargins(0, 0, 0, 0)
        summary_row.setSpacing(7)

        # Status dot
        is_running = self.agent_data.get("state") == "running"
        dot_color = "#10b981" if is_running else "#94a3b8"
        self.status_dot = QLabel(self)
        self.status_dot.setFixedSize(7, 7)
        self.status_dot.setStyleSheet(f"background-color: {dot_color}; border-radius: 3px;")
        summary_row.addWidget(self.status_dot)

        # Role & type
        name_box = QVBoxLayout()
        name_box.setContentsMargins(0, 0, 0, 0)
        name_box.setSpacing(1)

        role = self.agent_data.get("role") or "Subagent"
        self.lbl_role = QLabel(role, self)
        self.lbl_role.setStyleSheet("font-size: 11px; font-weight: 700;")
        name_box.addWidget(self.lbl_role)

        sub_type = self.agent_data.get("type") or "子智能体"
        state_str = "运行中" if is_running else "已完成"
        self.lbl_sub = QLabel(f"{sub_type} · {state_str}", self)
        self.lbl_sub.setProperty("class", "SubagentSub")
        name_box.addWidget(self.lbl_sub)
        summary_row.addLayout(name_box, 1)

        # Right metric
        tot_tok = self.agent_data.get("totalTokens", 0)
        cost = self.agent_data.get("costUsd", 0.0)

        self.lbl_tok = QLabel(fmt_tokens(tot_tok), self)
        self.lbl_tok.setStyleSheet("font-size: 11px; font-weight: 700;")
        summary_row.addWidget(self.lbl_tok)

        self.lbl_cost = QLabel(f"${cost:.3f}", self)
        self.lbl_cost.setObjectName("SubagentCost")
        summary_row.addWidget(self.lbl_cost)

        self.lbl_chevron = QLabel("▼", self)
        self.lbl_chevron.setProperty("class", "SubagentSub")
        summary_row.addWidget(self.lbl_chevron)

        card_l.addLayout(summary_row)

        # 2. Detail body (initially hidden)
        self.detail_frame = QFrame(self)
        self.detail_frame.setObjectName("SubagentDetail")
        self.detail_frame.setVisible(False)
        detail_l = QVBoxLayout(self.detail_frame)
        detail_l.setContentsMargins(4, 4, 4, 4)
        detail_l.setSpacing(4)

        grid = QVBoxLayout()
        grid.setSpacing(2)

        p_tok = self.agent_data.get("promptTokens", 0)
        c_tok = self.agent_data.get("candidateTokens", 0)
        th_tok = self.agent_data.get("thinkingTokens", 0)
        ca_tok = self.agent_data.get("cachedTokens", 0)
        ttft = self.agent_data.get("ttft", 0.0)
        speed = self.agent_data.get("speed", 0.0)

        row1 = QHBoxLayout()
        row1.addWidget(self._make_label("输入 / 缓存:"))
        row1.addWidget(self._make_val(f"{fmt_tokens(p_tok)} / {fmt_tokens(ca_tok)}"))
        grid.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(self._make_label("生成 / 思考:"))
        row2.addWidget(self._make_val(f"{fmt_tokens(c_tok)} / {fmt_tokens(th_tok)}"))
        grid.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(self._make_label("首字 / 速度:"))
        row3.addWidget(self._make_val(f"{ttft:.2f}s · {speed:.0f}t/s" if speed > 0 else f"{ttft:.2f}s"))
        grid.addLayout(row3)

        detail_l.addLayout(grid)

        # Action note
        last_action = self.agent_data.get("lastAction") or ("运行中..." if is_running else "已完成任务")
        self.lbl_action = QLabel(f"⚡ {last_action}", self)
        self.lbl_action.setWordWrap(True)
        self.lbl_action.setProperty("class", "SubagentAction")
        detail_l.addWidget(self.lbl_action)

        card_l.addWidget(self.detail_frame)

    def _make_label(self, text: str) -> QLabel:
        lbl = QLabel(text, self)
        lbl.setProperty("class", "SubagentDetailLabel")
        return lbl

    def _make_val(self, text: str) -> QLabel:
        lbl = QLabel(text, self)
        lbl.setProperty("class", "SubagentDetailVal")
        return lbl

    def toggle_accordion(self):
        new_v = not self.detail_frame.isVisible()
        self.detail_frame.setVisible(new_v)
        self.lbl_chevron.setText("▲" if new_v else "▼")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_accordion()
            event.accept()
        else:
            super().mousePressEvent(event)

class CapsuleWindow(QWidget):
    convo_selected = Signal(str)

    def __init__(self, parent=None, default_layout_mode=None):
        super().__init__(parent)
        self.is_expanded = True
        self.drag_position = QPoint()
        self.max_context = 256_000
        self.latest_data = {}

        # 加载设置：主题与布局模式
        saved_settings = load_saved_settings()
        self.current_theme = saved_settings.get("theme", "light")
        self.layout_mode = default_layout_mode if default_layout_mode else saved_settings.get("layout_mode", "compact")
        self.active_tab = "primary"  # "primary" or "cluster"
        self.subagent_cards = []

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.init_ui()
        self.set_layout_mode(self.layout_mode, save=False)
        self.set_theme(self.current_theme, save=False)

        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen.width() - 350, 50)

    def get_current_theme(self) -> str:
        return self.current_theme

    def set_theme(self, theme_name: str, save: bool = True):
        if theme_name not in THEME_CONFIGS:
            theme_name = "light"
        self.current_theme = theme_name
        cfg = THEME_CONFIGS[theme_name]

        self.setStyleSheet(make_theme_qss(cfg))
        if hasattr(self, 'prog_bar'):
            self.prog_bar.set_bg_color(cfg['bar_bg'])
        if hasattr(self, 'sep_line'):
            self.sep_line.setStyleSheet(f"background-color: {cfg['sep_bg']}; max-height: 1px;")
        if hasattr(self, 'pill_sep'):
            self.pill_sep.setStyleSheet(f"color: {cfg['border']}; font-size: 11px;")
        if hasattr(self, 'pill_sep2'):
            self.pill_sep2.setStyleSheet(f"color: {cfg['border']}; font-size: 11px;")
        if hasattr(self, 'wing_divider'):
            self.wing_divider.setStyleSheet(f"background-color: {cfg['sep_bg']}; width: 1px;")
        if hasattr(self, 'lbl_wing_primary'):
            self.lbl_wing_primary.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {cfg['accent']};")
        if hasattr(self, 'lbl_wing_cluster'):
            self.lbl_wing_cluster.setStyleSheet(f"font-size: 11px; font-weight: 700; color: {cfg['accent']};")
        if hasattr(self, 'lbl_wing_count'):
            self.lbl_wing_count.setStyleSheet(f"font-size: 10px; color: {cfg['text_sub']};")
        if hasattr(self, 'empty_cluster_lbl'):
            self.empty_cluster_lbl.setStyleSheet(f"font-size: 11px; color: {cfg['text_sub']}; padding: 20px 0;")
        if hasattr(self, 'lbl_global_title'):
            self.lbl_global_title.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {cfg['text_sub']};")
        if hasattr(self, 'lbl_global_val'):
            self.lbl_global_val.setStyleSheet(f"font-size: 12px; font-weight: 800; color: {cfg['cost_color']};")

        if hasattr(self, 'lbl_hero_pct') and hasattr(self, 'latest_data'):
            ctx = self.latest_data.get("activeContext", 0)
            if (ctx / self.max_context * 100) < 100.0:
                self.lbl_hero_pct.setStyleSheet("")

        if save:
            save_theme(theme_name)

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ================= A. 展开态：主卡片 =================
        self.card_frame = QFrame(self)
        self.card_frame.setObjectName("CardRoot")
        self.card_layout = QVBoxLayout(self.card_frame)
        self.card_layout.setContentsMargins(16, 12, 16, 14)
        self.card_layout.setSpacing(8)

        # 1. 窗口标题栏
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.setSpacing(8)

        lbl_title = QLabel("上下文用量", self)
        lbl_title.setObjectName("TitleLabel")
        top_bar.addWidget(lbl_title)

        self.combo_conv = QComboBox(self)
        self.combo_conv.setObjectName("ConvPicker")
        self.combo_conv.addItem("🔄 自动跟随", "__AUTO__")
        self.combo_conv.currentIndexChanged.connect(self._on_combo_changed)
        top_bar.addWidget(self.combo_conv, 1)

        btn_close = QPushButton("✕", self)
        btn_close.setObjectName("CloseBtn")
        btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_close.clicked.connect(self.toggle_mode)
        top_bar.addWidget(btn_close)

        self.card_layout.addLayout(top_bar)

        # 2. 顶部分段 Tab 切换组件 (方案 A 紧凑模式下呈现，方案 C 双翼模式下隐藏)
        self.tab_bar = QFrame(self)
        self.tab_bar.setObjectName("TabBar")
        tab_l = QHBoxLayout(self.tab_bar)
        tab_l.setContentsMargins(2, 2, 2, 2)
        tab_l.setSpacing(2)

        self.btn_tab_primary = QPushButton("💬 主会话", self.tab_bar)
        self.btn_tab_primary.setProperty("class", "TabBtn")
        self.btn_tab_primary.setProperty("active", "true")
        self.btn_tab_primary.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_tab_primary.clicked.connect(lambda: self.switch_tab("primary"))
        tab_l.addWidget(self.btn_tab_primary)

        self.btn_tab_cluster = QPushButton("🤖 智能体集群", self.tab_bar)
        self.btn_tab_cluster.setProperty("class", "TabBtn")
        self.btn_tab_cluster.setProperty("active", "false")
        self.btn_tab_cluster.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_tab_cluster.clicked.connect(lambda: self.switch_tab("cluster"))
        tab_l.addWidget(self.btn_tab_cluster)

        self.card_layout.addWidget(self.tab_bar)

        # 3. 核心内容区域容器 (支持紧凑单卡垂直与双翼模式水平排列)
        self.content_container = QWidget(self)
        self.content_layout = QHBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(14)

        # --- 左翼 / 主会话视图 (view_primary) ---
        self.view_primary = QWidget(self.content_container)
        v_primary_l = QVBoxLayout(self.view_primary)
        v_primary_l.setContentsMargins(0, 0, 0, 0)
        v_primary_l.setSpacing(8)

        # 双翼模式下的左翼标识
        self.lbl_wing_primary = QLabel("💬 主会话物理窗口", self.view_primary)
        self.lbl_wing_primary.setStyleSheet("font-size: 11px; font-weight: 700; color: #2563eb;")
        self.lbl_wing_primary.setVisible(False)
        v_primary_l.addWidget(self.lbl_wing_primary)

        # 核心指标
        hero_box = QHBoxLayout()
        hero_box.setContentsMargins(0, 0, 0, 0)
        hero_box.setSpacing(8)

        self.lbl_hero_pct = QLabel("0.0%", self.view_primary)
        self.lbl_hero_pct.setObjectName("HeroPct")
        hero_box.addWidget(self.lbl_hero_pct)

        self.lbl_hero_sub = QLabel("已使用 0K/ 256.0K", self.view_primary)
        self.lbl_hero_sub.setObjectName("HeroSub")
        hero_box.addWidget(self.lbl_hero_sub)
        hero_box.addStretch()

        v_primary_l.addLayout(hero_box)

        # 进度条
        self.prog_bar = SegmentedProgressBar(self.view_primary)
        v_primary_l.addWidget(self.prog_bar)

        # 5 大构成
        self.breakdown_layout = QVBoxLayout()
        self.breakdown_layout.setContentsMargins(0, 2, 0, 0)
        self.breakdown_layout.setSpacing(6)

        self.r_sys, self.val_sys = self.create_list_row("#10b981", "系统提示词")
        self.breakdown_layout.addLayout(self.r_sys)

        self.r_tools, self.val_tools = self.create_list_row("#f59e0b", "工具及子智能体")
        self.breakdown_layout.addLayout(self.r_tools)

        self.r_msg, self.val_msg = self.create_list_row("#8b5cf6", "对话消息")
        self.breakdown_layout.addLayout(self.r_msg)

        self.r_mcp, self.val_mcp = self.create_list_row("#06b6d4", "连接器及MCP")
        self.breakdown_layout.addLayout(self.r_mcp)

        self.r_skills, self.val_skills = self.create_list_row("#3b82f6", "技能")
        self.breakdown_layout.addLayout(self.r_skills)

        v_primary_l.addLayout(self.breakdown_layout)

        # 分割线
        self.sep_line = QFrame(self.view_primary)
        self.sep_line.setFrameShape(QFrame.Shape.HLine)
        self.sep_line.setStyleSheet("background-color: #f1f5f9; max-height: 1px;")
        v_primary_l.addWidget(self.sep_line)

        # 会话计费与输出指标
        summary_box = QVBoxLayout()
        summary_box.setSpacing(5)

        self.r_cache, self.val_cache = self.create_list_row("#10b981", "Prompt 缓存命中")
        summary_box.addLayout(self.r_cache)

        self.r_out, self.val_out = self.create_list_row("#8b5cf6", "模型生成输出")
        summary_box.addLayout(self.r_out)

        self.r_ttft, self.val_ttft = self.create_list_row("#0284c7", "首 token 响应")
        summary_box.addLayout(self.r_ttft)

        self.r_speed, self.val_speed = self.create_list_row("#f59e0b", "模型生成速度")
        summary_box.addLayout(self.r_speed)

        self.r_cost, self.val_cost = self.create_list_row("#d97706", "累计折算费用")
        summary_box.addLayout(self.r_cost)

        v_primary_l.addLayout(summary_box)
        self.content_layout.addWidget(self.view_primary, 1)

        # --- 双翼模式中缝分割线 (wing_divider) ---
        self.wing_divider = QFrame(self.content_container)
        self.wing_divider.setObjectName("WingDivider")
        self.wing_divider.setFrameShape(QFrame.Shape.VLine)
        self.wing_divider.setStyleSheet("background-color: #e2e8f0; width: 1px;")
        self.wing_divider.setVisible(False)
        self.content_layout.addWidget(self.wing_divider)

        # --- 右翼 / 集群雷达视图 (view_cluster) ---
        self.view_cluster = QWidget(self.content_container)
        v_cluster_l = QVBoxLayout(self.view_cluster)
        v_cluster_l.setContentsMargins(0, 0, 0, 0)
        v_cluster_l.setSpacing(8)

        # 双翼模式下的右翼头部标题
        self.wing_header_box = QHBoxLayout()
        self.lbl_wing_cluster = QLabel("🤖 智能体集群雷达", self.view_cluster)
        self.lbl_wing_cluster.setStyleSheet("font-size: 11px; font-weight: 700; color: #2563eb;")
        self.wing_header_box.addWidget(self.lbl_wing_cluster)
        self.lbl_wing_count = QLabel("共 0 个智能体", self.view_cluster)
        self.lbl_wing_count.setStyleSheet("font-size: 10px; color: #64748b;")
        self.wing_header_box.addWidget(self.lbl_wing_count, 0, Qt.AlignmentFlag.AlignRight)
        self.lbl_wing_cluster.setVisible(False)
        self.lbl_wing_count.setVisible(False)
        v_cluster_l.addLayout(self.wing_header_box)

        # 微仪表盘横条 (Micro-Dashboard)
        self.micro_dashboard = QFrame(self.view_cluster)
        self.micro_dashboard.setObjectName("MicroDashboard")
        micro_l = QHBoxLayout(self.micro_dashboard)
        micro_l.setContentsMargins(8, 6, 8, 6)
        micro_l.setSpacing(6)

        m_metric_box = QVBoxLayout()
        m_metric_box.setSpacing(1)
        lbl_m_title = QLabel("集群总消耗", self.micro_dashboard)
        lbl_m_title.setStyleSheet("font-size: 9px; color: #64748b; font-weight: 700;")
        m_metric_box.addWidget(lbl_m_title)

        self.micro_metric_val = QLabel("0 tok · $0.000", self.micro_dashboard)
        self.micro_metric_val.setStyleSheet("font-size: 11px; font-weight: 700;")
        m_metric_box.addWidget(self.micro_metric_val)
        micro_l.addLayout(m_metric_box, 1)

        self.micro_status_pill = QLabel("0 运行 · 0 完成", self.micro_dashboard)
        self.micro_status_pill.setStyleSheet("font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 8px;")
        micro_l.addWidget(self.micro_status_pill)

        v_cluster_l.addWidget(self.micro_dashboard)

        # 子智能体滚动列表
        self.scroll_area = QScrollArea(self.view_cluster)
        self.scroll_area.setObjectName("SubagentScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.scroll_content = QWidget()
        self.subagent_list_layout = QVBoxLayout(self.scroll_content)
        self.subagent_list_layout.setContentsMargins(0, 0, 0, 0)
        self.subagent_list_layout.setSpacing(6)
        self.subagent_list_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        v_cluster_l.addWidget(self.scroll_area, 1)

        # 暂无子智能体空态展示
        self.empty_cluster_lbl = QLabel("当前主会话暂无派生的子智能体\n派发后将自动实时呈现于此", self.view_cluster)
        self.empty_cluster_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_cluster_lbl.setStyleSheet("font-size: 11px; color: #64748b; padding: 20px 0;")
        v_cluster_l.addWidget(self.empty_cluster_lbl)

        # 全局双计费总额条 (在双翼雷达模式底部展示)
        self.global_rollup_box = QFrame(self.view_cluster)
        self.global_rollup_box.setStyleSheet("border-radius: 6px; padding: 4px 8px;")
        g_box_l = QHBoxLayout(self.global_rollup_box)
        g_box_l.setContentsMargins(4, 3, 4, 3)
        self.lbl_global_title = QLabel("全局总计 (主会话 + 集群):", self.global_rollup_box)
        self.lbl_global_title.setStyleSheet("font-size: 11px; font-weight: 600; color: #64748b;")
        g_box_l.addWidget(self.lbl_global_title)
        self.lbl_global_val = QLabel("$0.000", self.global_rollup_box)
        self.lbl_global_val.setStyleSheet("font-size: 12px; font-weight: 800; color: #d97706;")
        g_box_l.addWidget(self.lbl_global_val, 0, Qt.AlignmentFlag.AlignRight)
        self.global_rollup_box.setVisible(False)
        v_cluster_l.addWidget(self.global_rollup_box)

        self.content_layout.addWidget(self.view_cluster, 1)
        self.card_layout.addWidget(self.content_container)
        self.main_layout.addWidget(self.card_frame)

        # ================= B. 收起态：迷你悬浮小胶囊 =================
        self.pill_frame = QFrame(self)
        self.pill_frame.setObjectName("PillRoot")
        pill_l = QHBoxLayout(self.pill_frame)
        pill_l.setContentsMargins(12, 6, 12, 6)
        pill_l.setSpacing(8)

        self.pill_dot = QLabel(self)
        self.pill_dot.setFixedSize(8, 8)
        self.pill_dot.setStyleSheet("background-color: #10b981; border-radius: 4px;")
        pill_l.addWidget(self.pill_dot)

        self.pill_info = QLabel("0.0% 上下文", self)
        self.pill_info.setObjectName("PillText")
        pill_l.addWidget(self.pill_info)

        self.pill_sep = QLabel("│", self)
        self.pill_sep.setStyleSheet("color: #e2e8f0; font-size: 11px;")
        pill_l.addWidget(self.pill_sep)

        self.pill_perf = QLabel("", self)
        self.pill_perf.setStyleSheet("color: #0284c7; font-size: 11px; font-weight: 600;")
        pill_l.addWidget(self.pill_perf)

        self.pill_sep2 = QLabel("│", self)
        self.pill_sep2.setStyleSheet("color: #e2e8f0; font-size: 11px;")
        pill_l.addWidget(self.pill_sep2)

        self.pill_cost_lbl = QLabel("$0.00", self)
        self.pill_cost_lbl.setObjectName("PillCost")
        pill_l.addWidget(self.pill_cost_lbl)

        btn_expand = QPushButton("▲", self)
        btn_expand.setObjectName("CloseBtn")
        btn_expand.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_expand.clicked.connect(self.toggle_mode)
        pill_l.addWidget(btn_expand)

        self.pill_frame.setVisible(False)
        self.main_layout.addWidget(self.pill_frame)

    def set_layout_mode(self, mode: str, save: bool = True):
        """动态切换紧凑单卡 (compact, 320px) 或展开双翼 (dual_wing, 680px) 模式"""
        if mode not in ("compact", "dual_wing"):
            mode = "compact"
        self.layout_mode = mode

        if mode == "compact":
            self.setFixedWidth(320)
            self.card_frame.setFixedWidth(320)
            self.tab_bar.setVisible(True)
            self.wing_divider.setVisible(False)
            self.lbl_wing_primary.setVisible(False)
            self.lbl_wing_cluster.setVisible(False)
            self.lbl_wing_count.setVisible(False)
            self.global_rollup_box.setVisible(False)
            self.switch_tab(self.active_tab)
        else:  # dual_wing
            screen = QGuiApplication.primaryScreen().availableGeometry() if QGuiApplication.primaryScreen() else None
            if screen:
                curr_pos = self.pos()
                if curr_pos.x() + 680 > screen.right():
                    new_x = max(screen.left() + 20, screen.right() - 690)
                    self.move(new_x, curr_pos.y())

            self.setFixedWidth(680)
            self.card_frame.setFixedWidth(680)
            self.tab_bar.setVisible(False)
            self.wing_divider.setVisible(True)
            self.lbl_wing_primary.setVisible(True)
            self.lbl_wing_cluster.setVisible(True)
            self.lbl_wing_count.setVisible(True)
            self.global_rollup_box.setVisible(True)
            self.view_primary.setVisible(True)
            self.view_cluster.setVisible(True)

        if save:
            save_settings({"theme": self.current_theme, "layout_mode": self.layout_mode})
        self.adjustSize()

    def switch_tab(self, tab_name: str):
        """紧凑单卡模式下切换主会话与集群标签页"""
        self.active_tab = tab_name
        is_primary = (tab_name == "primary")

        self.btn_tab_primary.setProperty("active", "true" if is_primary else "false")
        self.btn_tab_cluster.setProperty("active", "false" if is_primary else "true")

        self.btn_tab_primary.style().unpolish(self.btn_tab_primary)
        self.btn_tab_primary.style().polish(self.btn_tab_primary)
        self.btn_tab_cluster.style().unpolish(self.btn_tab_cluster)
        self.btn_tab_cluster.style().polish(self.btn_tab_cluster)

        if self.layout_mode == "compact":
            self.view_primary.setVisible(is_primary)
            self.view_cluster.setVisible(not is_primary)
            self.adjustSize()

    def create_list_row(self, color_hex: str, label_text: str):
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        dot = QLabel(self)
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background-color: {color_hex}; border-radius: 4px;")
        h.addWidget(dot)

        lbl = QLabel(label_text, self)
        lbl.setProperty("class", "ItemLabel")
        h.addWidget(lbl)

        h.addStretch()

        val = QLabel("-", self)
        val.setProperty("class", "ItemVal")
        h.addWidget(val)

        return h, val

    def update_data(self, data: dict):
        if not data:
            return
        self.latest_data = data

        active_ctx = data.get("activeContext", 0)
        breakdown = data.get("breakdown", {})
        cum = data.get("cumulative", {})
        cluster = data.get("cluster", {})
        subagents = cluster.get("subagents", [])

        # 1. 核心大字号百分比 (基于 256k 截断基准)
        ctx_pct = (active_ctx / self.max_context * 100) if self.max_context > 0 else 0.0
        self.lbl_hero_pct.setText(f"{ctx_pct:.1f}%")
        if ctx_pct >= 100.0:
            self.lbl_hero_pct.setStyleSheet("color: #ef4444; font-size: 26px; font-weight: 800;")
            self.lbl_hero_sub.setText(f"已使用 {fmt_tokens(active_ctx)} / 256k ⚠️ (待压缩)")
        else:
            self.lbl_hero_pct.setStyleSheet("")
            self.lbl_hero_sub.setText(f"已使用 {fmt_tokens(active_ctx)} / 256k")

        # 2. 分段多彩进度条
        b_sys = breakdown.get("system", {}).get("tokens", 0)
        b_tools = breakdown.get("tools", {}).get("tokens", 0)
        b_msg = breakdown.get("messages", {}).get("tokens", 0)
        b_mcp = breakdown.get("mcp", {}).get("tokens", 0)
        b_skills = breakdown.get("skills", {}).get("tokens", 0)

        self.prog_bar.set_segments([
            (b_sys / self.max_context, QColor("#10b981")),
            (b_tools / self.max_context, QColor("#f59e0b")),
            (b_msg / self.max_context, QColor("#8b5cf6")),
            (b_mcp / self.max_context, QColor("#06b6d4")),
            (b_skills / self.max_context, QColor("#3b82f6")),
        ])

        # 3. 5 大构成细项数值
        self.val_sys.setText(f"{breakdown.get('system', {}).get('pct', 0.0):.1f}% ({fmt_tokens(b_sys)})")
        self.val_tools.setText(f"{breakdown.get('tools', {}).get('pct', 0.0):.1f}% ({fmt_tokens(b_tools)})")
        self.val_msg.setText(f"{breakdown.get('messages', {}).get('pct', 0.0):.1f}% ({fmt_tokens(b_msg)})")
        self.val_mcp.setText(f"{breakdown.get('mcp', {}).get('pct', 0.0):.1f}% ({fmt_tokens(b_mcp)})")
        self.val_skills.setText(f"{breakdown.get('skills', {}).get('pct', 0.0):.1f}% ({fmt_tokens(b_skills)})")

        # 4. 会话财务与产出 + 双计费联动 (Q3)
        cum_ca = cum.get("cachedTokens", 0)
        cum_ratio = cum.get("cacheRatio", 0.0)
        cum_c = cum.get("candidateTokens", 0)
        cum_th = cum.get("thinkingTokens", 0)
        cum_billed = cum.get("billedTokens", 0)
        cum_cost = cum.get("costUsd", 0.0)

        self.val_cache.setText(f"{fmt_tokens(cum_ca)} ({cum_ratio:.1f}%)")
        th_str = f" (思考 {fmt_tokens(cum_th)})" if cum_th > 0 else ""
        self.val_out.setText(f"{fmt_tokens(cum_c)}{th_str}")

        # 性能指标
        turn_data = data.get("turn", {})
        turn_ttft = turn_data.get("ttft", 0.0)
        turn_speed = turn_data.get("speed", 0.0)
        avg_ttft = cum.get("avgTtft", 0.0)
        avg_speed = cum.get("avgSpeed", 0.0)

        if turn_ttft > 0 and avg_ttft > 0:
            self.val_ttft.setText(f"{turn_ttft:.1f}s (均值 {avg_ttft:.1f}s)")
        elif avg_ttft > 0:
            self.val_ttft.setText(f"均值 {avg_ttft:.1f}s")
        else:
            self.val_ttft.setText("-")

        if turn_speed > 0 and avg_speed > 0:
            self.val_speed.setText(f"{turn_speed:.0f} tok/s (均速 {avg_speed:.0f})")
        elif turn_speed > 0:
            self.val_speed.setText(f"{turn_speed:.0f} tok/s")
        elif avg_speed > 0:
            self.val_speed.setText(f"均速 {avg_speed:.0f} tok/s")
        else:
            self.val_speed.setText("-")

        # 双计费联动展示: $0.081 (含集群: $0.235)
        combined_cost = cluster.get("combinedCostUsd", cum_cost)
        cluster_cost = cluster.get("totalCostUsd", 0.0)
        if cluster_cost > 0:
            self.val_cost.setText(f"${cum_cost:.3f} (含集群: ${combined_cost:.3f})")
        else:
            self.val_cost.setText(f"${cum_cost:.3f} (计费 {fmt_tokens(cum_billed)})")

        # 5. 更新智能体集群 Tab 徽章与微仪表盘
        sub_count = len(subagents)
        running_cnt = cluster.get("runningCount", cluster.get("activeCount", 0))
        done_cnt = cluster.get("doneCount", cluster.get("completedCount", 0))
        cluster_tokens = cluster.get("totalTokens", 0)

        if sub_count > 0:
            self.btn_tab_cluster.setText(f"🤖 智能体集群 • {sub_count}")
            self.btn_tab_cluster.setEnabled(True)
        else:
            self.btn_tab_cluster.setText("🤖 智能体集群")
            self.btn_tab_cluster.setEnabled(False)
            if self.active_tab == "cluster":
                self.switch_tab("primary")

        self.micro_metric_val.setText(f"{fmt_tokens(cluster_tokens)} · ${cluster_cost:.3f}")
        self.micro_status_pill.setText(f"🟢 {running_cnt} 运行 · ⚪ {done_cnt} 完成")

        self.lbl_wing_count.setText(f"共 {sub_count} 个智能体")
        self.lbl_global_val.setText(f"${combined_cost:.3f}")

        # 6. 渲染子智能体列表
        # 清除旧卡片
        for card in self.subagent_cards:
            self.subagent_list_layout.removeWidget(card)
            card.deleteLater()
        self.subagent_cards.clear()

        if sub_count == 0:
            self.empty_cluster_lbl.setVisible(True)
            self.scroll_area.setVisible(False)
        else:
            self.empty_cluster_lbl.setVisible(False)
            self.scroll_area.setVisible(True)
            for s in subagents:
                card = SubagentCardWidget(s, self.scroll_content)
                self.subagent_cards.append(card)
                # 插入在 stretch 之前
                self.subagent_list_layout.insertWidget(self.subagent_list_layout.count() - 1, card)

        # 7. 收起迷你药丸态
        pill_text = f"{ctx_pct:.1f}% 上下文"
        if running_cnt > 0:
            pill_text += f" · 🤖{running_cnt}"
        self.pill_info.setText(pill_text)
        if turn_ttft > 0 and turn_speed > 0:
            self.pill_perf.setText(f"{turn_ttft:.1f}s · {turn_speed:.0f}t/s")
            self.pill_perf.setVisible(True)
            self.pill_sep2.setVisible(True)
        else:
            self.pill_perf.setVisible(False)
            self.pill_sep2.setVisible(False)
        self.pill_cost_lbl.setText(f"${combined_cost:.2f}" if cluster_cost > 0 else f"${cum_cost:.2f}")

        title = data.get("title", "")
        cid = data.get("conversationId", "")
        tip = f"会话: {title}\nID: {cid}" if title else f"ID: {cid}"
        self.card_frame.setToolTip(tip)

    def update_recent_list(self, recent: list):
        current_selected = self.combo_conv.currentData()
        self.combo_conv.blockSignals(True)
        self.combo_conv.clear()
        self.combo_conv.addItem("🔄 自动跟随", "__AUTO__")

        for item in recent:
            cid = item["id"]
            name = item.get("name") or f"📌 [{item['time']}] {item['shortId']}"
            self.combo_conv.addItem(name, cid)

        if current_selected:
            idx = self.combo_conv.findData(current_selected)
            if idx >= 0:
                self.combo_conv.setCurrentIndex(idx)
        self.combo_conv.blockSignals(False)

    def _on_combo_changed(self, idx):
        target_id = self.combo_conv.currentData()
        if target_id:
            self.convo_selected.emit(target_id)

    def toggle_mode(self):
        self.is_expanded = not self.is_expanded
        if not self.is_expanded:
            self.card_frame.setVisible(False)
            self.pill_frame.setVisible(True)
            self.setMinimumWidth(0)
            self.setMaximumWidth(16777215)
        else:
            self.card_frame.setVisible(True)
            self.pill_frame.setVisible(False)
            target_w = 680 if self.layout_mode == "dual_wing" else 320
            self.setFixedWidth(target_w)
            self.card_frame.setFixedWidth(target_w)
        self.adjustSize()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
