from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import (
    QColor, QCursor, QGuiApplication, QPainter, QPainterPath
)
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QApplication
)
from data_engine import fmt_tokens

LIGHT_CARD_STYLE = """
QWidget#CardRoot {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
}

QWidget#PillRoot {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
}

QLabel {
    font-family: 'Segoe UI', -apple-system, system-ui, sans-serif;
}

QLabel#TitleLabel {
    color: #0f172a;
    font-size: 15px;
    font-weight: 700;
}

QLabel#HeroPct {
    color: #0f172a;
    font-size: 26px;
    font-weight: 800;
}

QLabel#HeroSub {
    color: #64748b;
    font-size: 13px;
    font-weight: 500;
    padding-bottom: 2px;
}

QPushButton#CloseBtn {
    background: transparent;
    color: #64748b;
    border: none;
    font-size: 14px;
    font-weight: bold;
    padding: 2px 6px;
    border-radius: 4px;
}
QPushButton#CloseBtn:hover {
    color: #0f172a;
    background-color: #f1f5f9;
}

QComboBox#ConvPicker {
    background-color: #f8fafc;
    color: #2563eb;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: 600;
}
QComboBox#ConvPicker::drop-down {
    border: none;
    width: 14px;
}
QComboBox#ConvPicker QAbstractItemView {
    background-color: #ffffff;
    color: #1e293b;
    selection-background-color: #eff6ff;
    selection-color: #2563eb;
    border: 1px solid #e2e8f0;
    outline: none;
    font-size: 11px;
}

QLabel.ItemLabel {
    color: #334155;
    font-size: 13px;
    font-weight: 500;
}
QLabel.ItemVal {
    color: #64748b;
    font-size: 13px;
    font-weight: 600;
}

QLabel#PillText {
    color: #0f172a;
    font-size: 12px;
    font-weight: 600;
}
QLabel#PillCost {
    color: #d97706;
    font-size: 12px;
    font-weight: 700;
}
"""

class SegmentedProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(8)
        self.segments = []

    def set_segments(self, segments):
        self.segments = segments
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()

        painter.setBrush(QColor("#f1f5f9"))
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

class CapsuleWindow(QWidget):
    convo_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_expanded = True
        self.drag_position = QPoint()
        self.max_context = 256_000  # 固定回 256K 压缩红线，视觉饱满清晰
        self.latest_data = {}

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.init_ui()
        self.setStyleSheet(LIGHT_CARD_STYLE)

        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen.width() - 330, 50)

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ================= A. 展开态：用量卡片 (256.0K 黄金基准) =================
        self.card_frame = QFrame(self)
        self.card_frame.setObjectName("CardRoot")
        card_l = QVBoxLayout(self.card_frame)
        card_l.setContentsMargins(18, 14, 18, 16)
        card_l.setSpacing(10)

        # 1. 标题栏
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

        card_l.addLayout(top_bar)

        # 2. 核心大指标行 (e.g. 39.0% 已使用 99.9k/ 256.0K)
        hero_box = QHBoxLayout()
        hero_box.setContentsMargins(0, 2, 0, 0)
        hero_box.setSpacing(8)

        self.lbl_hero_pct = QLabel("0.0%", self)
        self.lbl_hero_pct.setObjectName("HeroPct")
        hero_box.addWidget(self.lbl_hero_pct)

        self.lbl_hero_sub = QLabel("已使用 0K/ 256.0K", self)
        self.lbl_hero_sub.setObjectName("HeroSub")
        hero_box.addWidget(self.lbl_hero_sub)
        hero_box.addStretch()

        card_l.addLayout(hero_box)

        # 3. 分段彩色进度条 (绿/橙/紫/青/蓝)
        self.prog_bar = SegmentedProgressBar(self)
        card_l.addWidget(self.prog_bar)

        # 4. 参考图对应的 5 大构成指标列表
        self.breakdown_layout = QVBoxLayout()
        self.breakdown_layout.setContentsMargins(0, 4, 0, 0)
        self.breakdown_layout.setSpacing(8)

        # 🟢 系统提示词
        self.r_sys, self.val_sys = self.create_list_row("#10b981", "系统提示词")
        self.breakdown_layout.addLayout(self.r_sys)

        # 🟠 工具及子智能体
        self.r_tools, self.val_tools = self.create_list_row("#f59e0b", "工具及子智能体")
        self.breakdown_layout.addLayout(self.r_tools)

        # 🟣 对话消息
        self.r_msg, self.val_msg = self.create_list_row("#8b5cf6", "对话消息")
        self.breakdown_layout.addLayout(self.r_msg)

        # 🔵 连接器及MCP
        self.r_mcp, self.val_mcp = self.create_list_row("#06b6d4", "连接器及MCP")
        self.breakdown_layout.addLayout(self.r_mcp)

        # 🔵 技能
        self.r_skills, self.val_skills = self.create_list_row("#3b82f6", "技能")
        self.breakdown_layout.addLayout(self.r_skills)

        card_l.addLayout(self.breakdown_layout)

        # 5. 分割线
        sep_line = QFrame(self)
        sep_line.setFrameShape(QFrame.Shape.HLine)
        sep_line.setStyleSheet("background-color: #f1f5f9; max-height: 1px;")
        card_l.addWidget(sep_line)

        # 6. 会话计费与输出指标 (融合保留)
        summary_box = QVBoxLayout()
        summary_box.setSpacing(6)

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

        card_l.addLayout(summary_box)
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

        sep = QLabel("│", self)
        sep.setStyleSheet("color: #e2e8f0; font-size: 11px;")
        pill_l.addWidget(sep)

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

        self.setFixedWidth(310)
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

        # 1. 核心大字号百分比 (基于 256k 平台截断基准计算)
        ctx_pct = (active_ctx / self.max_context * 100) if self.max_context > 0 else 0.0
        self.lbl_hero_pct.setText(f"{ctx_pct:.1f}%")
        if ctx_pct >= 100.0:
            self.lbl_hero_pct.setStyleSheet("color: #ef4444; font-size: 24px; font-weight: 800;")
            self.lbl_hero_sub.setText(f"已使用 {fmt_tokens(active_ctx)} / 256k ⚠️ (待压缩)")
        else:
            self.lbl_hero_pct.setStyleSheet("color: #0f172a; font-size: 24px; font-weight: 800;")
            self.lbl_hero_sub.setText(f"已使用 {fmt_tokens(active_ctx)} / 256k")

        # 2. 分段多彩进度条 (基于 256.0K 饱满比例)
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

        # 4. 会话财务与产出
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

        self.val_cost.setText(f"${cum_cost:.3f} (计费 {fmt_tokens(cum_billed)})")

        # 5. 收起药丸态
        self.pill_info.setText(f"{ctx_pct:.1f}% 上下文")
        if turn_ttft > 0 and turn_speed > 0:
            self.pill_perf.setText(f"{turn_ttft:.1f}s · {turn_speed:.0f}t/s")
            self.pill_perf.setVisible(True)
            self.pill_sep2.setVisible(True)
        else:
            self.pill_perf.setVisible(False)
            self.pill_sep2.setVisible(False)
        self.pill_cost_lbl.setText(f"${cum_cost:.2f}")

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
        self.card_frame.setVisible(self.is_expanded)
        self.pill_frame.setVisible(not self.is_expanded)
        self.adjustSize()

    # --- 鼠标手势与边缘吸附 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = QPoint()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        pos = self.pos()
        snap_distance = 30

        new_x = pos.x()
        if pos.x() < screen.left() + snap_distance:
            new_x = screen.left() + 10
        elif pos.x() + self.width() > screen.right() - snap_distance:
            new_x = screen.right() - self.width() - 10

        new_y = max(screen.top() + 10, min(pos.y(), screen.bottom() - self.height() - 10))
        self.move(new_x, new_y)

    def mouseDoubleClickEvent(self, event):
        self.toggle_mode()
