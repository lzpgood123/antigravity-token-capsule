import os
import glob
import json
import sqlite3
import time
import re
import urllib.request
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QTimer

# 导入本地独立的 proto_decoder (完全自给自足独立沙盒)
current_dir = os.path.dirname(os.path.abspath(__file__))
import sys
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from proto_decoder import extract_usage_from_blob
except ImportError:
    extract_usage_from_blob = None

def fmt_tokens(n: int) -> str:
    """格式化 Token 数量为易读的字符串 (如 12.3k, 1.28M)"""
    if n is None:
        return "0"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)

class DataEngine(QObject):
    """
    高级数据引擎：
    1. 通过 Antigravity DevTools 协议独占锁定当前窗口正在浏览的会话，杜绝多窗口/多智能体背景任务的干扰与跳变。
    2. 计算会话上下文的 5 大分段构成 (系统提示词、工具、对话消息、MCP、技能)。
    3. 支持会话快速切换与全局财务/输出统计。
    """
    session_updated = Signal(dict)
    recent_list_updated = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.session_file = os.path.expanduser("~/.gemini/antigravity/active_session.json")
        self.conv_dir = os.path.expanduser("~/.gemini/antigravity/conversations")
        self.devtools_file = os.path.expanduser("~/AppData/Roaming/Antigravity/DevToolsActivePort")
        
        self.current_conv_id = ""
        self.auto_follow = True
        self.last_db_mtime = 0
        self.cached_cdp_port = ""
        self.titles_cache = {}
        self.last_titles_fetch = 0

        # 定时器：300ms 快速无锁轮询，精准跟随用户当前界面
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_updates)
        self.poll_timer.start(300)

        # 启动时初始化
        QTimer.singleShot(50, self.refresh_all)

    def get_cdp_active_conversation_id(self) -> str:
        """从 Antigravity 的 Chromium 调试接口获取当前窗口正在查看的会话 ID"""
        # 读取端口
        if not self.cached_cdp_port:
            if os.path.exists(self.devtools_file):
                try:
                    with open(self.devtools_file, "r", encoding="utf-8") as f:
                        self.cached_cdp_port = f.readline().strip()
                except Exception:
                    pass

        if not self.cached_cdp_port:
            return ""

        url = f"http://127.0.0.1:{self.cached_cdp_port}/json"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=0.2) as resp:
                targets = json.loads(resp.read().decode("utf-8"))
                for t in targets:
                    target_url = t.get("url", "")
                    match = re.search(r'/c/([a-f0-9\-]{36})', target_url)
                    if match:
                        return match.group(1)
        except Exception:
            # 端口可能失效，重置下次重读
            self.cached_cdp_port = ""

        return ""

    def fetch_trajectory_titles(self):
        """拉取会话标题缓存，避免高频请求"""
        now = time.time()
        if now - self.last_titles_fetch < 10 and self.titles_cache:
            return
        self.last_titles_fetch = now

        for port in [10429, 10428]:
            try:
                url = f"http://127.0.0.1:{port}/exa.language_server_pb.LanguageServerService/GetAllCascadeTrajectories"
                req = urllib.request.Request(
                    url,
                    data=b'{"metadata":{"ideName":"antigravity","extensionName":"antigravity"}}',
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=0.6) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    summaries = data.get("trajectorySummaries", {})
                    for cid, s in summaries.items():
                        title = s.get("summary", "")
                        if title and title != "<original_task>":
                            self.titles_cache[cid] = title
                break
            except Exception:
                pass

    def _poll_updates(self):
        if self.auto_follow:
            # 1. 强力优先绑定用户前台窗口所看的会话
            cdp_conv_id = self.get_cdp_active_conversation_id()
            if cdp_conv_id:
                if cdp_conv_id != self.current_conv_id:
                    # 用户在前台切换了会话！立即切换数据源
                    self.current_conv_id = cdp_conv_id
                    self.last_db_mtime = 0
                    full_data = self.get_convo_stats(cdp_conv_id)
                    if full_data:
                        self.session_updated.emit(full_data)
                        self.recent_list_updated.emit(self.get_recent_conversations(limit=10))
                        return
            elif not self.current_conv_id:
                # 初始启动且 CDP 尚未就绪时降级读取 active_session.json 一次
                self._fallback_load_active_file()
                return

        # 2. 对当前已锁定的会话检查其 .db 及 .db-wal 是否有最新更新 (实时捕获中间步骤)
        if self.current_conv_id:
            db_path = os.path.join(self.conv_dir, f"{self.current_conv_id}.db")
            wal_path = os.path.join(self.conv_dir, f"{self.current_conv_id}.db-wal")
            if os.path.exists(db_path):
                try:
                    # 在 SQLite WAL 模式下，多步工具调用的增量元数据全部实时写在 -wal 文件中
                    m = os.path.getmtime(db_path)
                    if os.path.exists(wal_path):
                        m = max(m, os.path.getmtime(wal_path))
                        # 加上 wal 文件大小计算变动标记，防止 1 秒内多次快速步骤 mtime 相同
                        m += os.path.getsize(wal_path) * 1e-6

                    if m != self.last_db_mtime:
                        self.last_db_mtime = m
                        full_data = self.get_convo_stats(self.current_conv_id)
                        if full_data:
                            self.session_updated.emit(full_data)
                except Exception:
                    pass

    def _fallback_load_active_file(self):
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                conv_id = data.get("conversationId", "")
                if conv_id:
                    self.current_conv_id = conv_id
                    full_data = self.get_convo_stats(conv_id, fallback_data=data)
                    if full_data:
                        self.session_updated.emit(full_data)
            except Exception:
                pass

    def refresh_all(self):
        self.fetch_trajectory_titles()
        recent = self.get_recent_conversations(limit=10)
        self.recent_list_updated.emit(recent)

        if self.auto_follow:
            cdp_id = self.get_cdp_active_conversation_id()
            if cdp_id:
                self.current_conv_id = cdp_id
                full_data = self.get_convo_stats(cdp_id)
                if full_data:
                    self.session_updated.emit(full_data)
                    return
            self._fallback_load_active_file()

    def switch_to_conversation(self, conv_id: str):
        if conv_id == "__AUTO__":
            self.auto_follow = True
            cdp_id = self.get_cdp_active_conversation_id()
            target_id = cdp_id if cdp_id else self.current_conv_id
            if target_id:
                self.current_conv_id = target_id
                self.last_db_mtime = 0
                full_data = self.get_convo_stats(target_id)
                if full_data:
                    self.session_updated.emit(full_data)
            return

        self.auto_follow = False
        self.current_conv_id = conv_id
        self.last_db_mtime = 0
        full_data = self.get_convo_stats(conv_id)
        if full_data:
            self.session_updated.emit(full_data)

    def get_convo_stats(self, conv_id: str, fallback_data=None) -> dict:
        """从对应会话的 SQLite 提取包含总输入、总输出、思考 Token 及 5 大分段的完整指标"""
        db_path = os.path.join(self.conv_dir, f"{conv_id}.db")
        if not os.path.exists(db_path) or not extract_usage_from_blob:
            if fallback_data:
                return fallback_data
            return {}

        clean_path = db_path.replace("\\", "/")
        cum_p, cum_c, cum_ca, cum_th = 0, 0, 0, 0
        ttft_list = []
        cum_cand_time = 0.0
        latest = {}

        try:
            conn = sqlite3.connect(f"file:{clean_path}?mode=ro", uri=True, timeout=0.8)
            c = conn.cursor()
            c.execute("SELECT idx, data FROM gen_metadata ORDER BY idx ASC")
            rows = c.fetchall()
            conn.close()

            for idx, blob in rows:
                u = extract_usage_from_blob(blob)
                if u:
                    cand = u.get("candidates", 0)
                    ttft = u.get("ttft", 0.0)
                    sdur = u.get("streaming_duration", 0.0)

                    cum_p += u.get("prompt", 0)
                    cum_c += cand
                    cum_ca += u.get("cached", 0)
                    cum_th += u.get("thinking", 0)

                    if ttft > 0:
                        ttft_list.append(ttft)
                    tot_dur = ttft + sdur
                    if tot_dur > 0 and cand > 0:
                        cum_cand_time += tot_dur

                    latest = u
        except Exception:
            if fallback_data:
                return fallback_data

        turn_p = latest.get("prompt", 0)
        turn_c = latest.get("candidates", 0)
        turn_ca = latest.get("cached", 0)
        turn_th = latest.get("thinking", 0)
        turn_ttft = latest.get("ttft", 0.0)
        turn_sdur = latest.get("streaming_duration", 0.0)
        turn_tot_time = turn_ttft + turn_sdur
        turn_speed = (turn_c / turn_tot_time) if turn_tot_time > 0 else 0.0

        avg_ttft = (sum(ttft_list) / len(ttft_list)) if ttft_list else 0.0
        avg_speed = (cum_c / cum_cand_time) if cum_cand_time > 0 else 0.0

        cum_billed = cum_p + cum_c
        cum_in = cum_p + cum_ca
        cum_ratio = (cum_ca / cum_in * 100) if cum_in > 0 else 0.0
        # Gemini 3.8 Flash 体验优惠价: 输入 $0.75, 输出 $3.75, 缓存 $0.15
        cum_cost = (cum_p * 0.75 + cum_c * 3.75 + cum_ca * 0.15) / 1e6

        # 当前活跃上下文 = 本次未缓存输入 + 本次缓存输入
        active_context = turn_p + turn_ca

        # 计算 5 大模块分解 (系统提示词、工具定义、对话消息、MCP、技能)
        breakdown = self.calculate_context_breakdown(active_context)

        return {
            "conversationId": conv_id,
            "title": self.titles_cache.get(conv_id, ""),
            "autoFollow": self.auto_follow,
            "activeContext": active_context,
            "breakdown": breakdown,
            "turn": {
                "promptTokens": turn_p,
                "candidateTokens": turn_c,
                "cachedTokens": turn_ca,
                "thinkingTokens": turn_th,
                "costUsd": round((turn_p * 0.75 + turn_c * 3.75 + turn_ca * 0.15) / 1e6, 4),
                "ttft": round(turn_ttft, 2),
                "speed": round(turn_speed, 1)
            },
            "cumulative": {
                "promptTokens": cum_p,
                "candidateTokens": cum_c,
                "cachedTokens": cum_ca,
                "thinkingTokens": cum_th,
                "billedTokens": cum_billed,
                "totalContext": cum_billed + cum_ca,
                "cacheRatio": round(cum_ratio, 1),
                "costUsd": round(cum_cost, 3),
                "avgTtft": round(avg_ttft, 2),
                "avgSpeed": round(avg_speed, 1)
            }
        }

    def calculate_context_breakdown(self, total_ctx: int) -> dict:
        """
        按 Antigravity 实际注入规格测算各模块占比:
        1. 系统提示词: ~3,200 tokens
        2. 工具及子智能体: ~4,600 tokens
        3. 技能: ~3,800 tokens
        4. 连接器及 MCP: ~1,500 tokens
        5. 对话历史消息: 动态其余部分
        """
        if total_ctx <= 0:
            return {
                "system": {"tokens": 0, "pct": 0.0},
                "tools": {"tokens": 0, "pct": 0.0},
                "messages": {"tokens": 0, "pct": 0.0},
                "mcp": {"tokens": 0, "pct": 0.0},
                "skills": {"tokens": 0, "pct": 0.0}
            }

        base_sys = 3200
        base_tools = 4600
        base_skills = 3800
        base_mcp = 1500

        static_total = base_sys + base_tools + base_skills + base_mcp

        if total_ctx <= static_total:
            scale = total_ctx / static_total
            sys_t = int(base_sys * scale)
            tools_t = int(base_tools * scale)
            skills_t = int(base_skills * scale)
            mcp_t = int(base_mcp * scale)
            msg_t = 0
        else:
            sys_t = base_sys
            tools_t = base_tools
            skills_t = base_skills
            mcp_t = base_mcp
            msg_t = total_ctx - static_total

        return {
            "system": {"tokens": sys_t, "pct": round(sys_t / total_ctx * 100, 1)},
            "tools": {"tokens": tools_t, "pct": round(tools_t / total_ctx * 100, 1)},
            "messages": {"tokens": msg_t, "pct": round(msg_t / total_ctx * 100, 1)},
            "mcp": {"tokens": mcp_t, "pct": round(mcp_t / total_ctx * 100, 1)},
            "skills": {"tokens": skills_t, "pct": round(skills_t / total_ctx * 100, 1)}
        }

    def get_recent_conversations(self, limit=10) -> list:
        if not os.path.exists(self.conv_dir):
            return []

        dbs = glob.glob(os.path.join(self.conv_dir, "*.db"))
        dbs.sort(key=os.path.getmtime, reverse=True)

        recent = []
        for db in dbs[:limit]:
            conv_id = os.path.splitext(os.path.basename(db))[0]
            mtime = os.path.getmtime(db)
            dt_str = datetime.fromtimestamp(mtime).strftime("%H:%M")
            title = self.titles_cache.get(conv_id, "")
            if title:
                display_name = f"📌 [{dt_str}] {title}"
            else:
                display_name = f"📌 [{dt_str}] {conv_id[:8]}...{conv_id[-4:]}"

            recent.append({
                "id": conv_id,
                "shortId": f"{conv_id[:8]}...{conv_id[-4:]}",
                "name": display_name,
                "title": title,
                "time": dt_str
            })
        return recent
