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
        self.brain_dir = os.path.expanduser("~/.gemini/antigravity/brain")
        self.devtools_file = os.path.expanduser("~/AppData/Roaming/Antigravity/DevToolsActivePort")
        
        self.current_conv_id = ""
        self.auto_follow = True
        self.last_db_mtime = 0
        self.last_transcript_mtime = 0
        self.cached_cdp_port = ""
        self.titles_cache = {}
        self.last_titles_fetch = 0

        # 子智能体发现缓存与文件监听状态
        self.discovered_subagents = {}  # conv_id -> dict of subagent info
        self.subagent_db_mtimes = {}   # sub_id -> float mtime
        self.subagent_t_mtimes = {}    # sub_id -> float transcript mtime

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
                    self.last_transcript_mtime = 0
                    self.discovered_subagents.clear()
                    self.subagent_db_mtimes.clear()
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
            t_path = os.path.join(self.brain_dir, self.current_conv_id, ".system_generated", "logs", "transcript.jsonl")
            has_changes = False

            # (1) 主会话数据库
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
                        has_changes = True
                except Exception:
                    pass

            # (2) 主会话日志（子智能体派生与生命周期变动）
            if os.path.exists(t_path):
                try:
                    tm = os.path.getmtime(t_path) + os.path.getsize(t_path) * 1e-6
                    if tm != self.last_transcript_mtime:
                        self.last_transcript_mtime = tm
                        has_changes = True
                except Exception:
                    pass

            # (3) 各子智能体的数据库与日志（捕获新派生与步骤）
            for sub_id in list(self.discovered_subagents.keys()):
                s_db = os.path.join(self.conv_dir, f"{sub_id}.db")
                s_wal = os.path.join(self.conv_dir, f"{sub_id}.db-wal")
                s_t = os.path.join(self.brain_dir, sub_id, ".system_generated", "logs", "transcript.jsonl")
                if os.path.exists(s_db):
                    try:
                        sm = os.path.getmtime(s_db)
                        if os.path.exists(s_wal):
                            sm = max(sm, os.path.getmtime(s_wal))
                            sm += os.path.getsize(s_wal) * 1e-6
                        if sm != self.subagent_db_mtimes.get(sub_id, 0):
                            self.subagent_db_mtimes[sub_id] = sm
                            has_changes = True
                    except Exception:
                        pass
                if os.path.exists(s_t):
                    try:
                        stm = os.path.getmtime(s_t) + os.path.getsize(s_t) * 1e-6
                        if stm != self.subagent_t_mtimes.get(sub_id, 0):
                            self.subagent_t_mtimes[sub_id] = stm
                            has_changes = True
                    except Exception:
                        pass

            if has_changes:
                full_data = self.get_convo_stats(self.current_conv_id)
                if full_data:
                    self.session_updated.emit(full_data)

    def _fallback_load_active_file(self):
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                conv_id = data.get("conversationId", "")
                if conv_id:
                    self.current_conv_id = conv_id
                    self.discovered_subagents.clear()
                    self.subagent_db_mtimes.clear()
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
                self.discovered_subagents.clear()
                self.subagent_db_mtimes.clear()
                full_data = self.get_convo_stats(cdp_id)
                if full_data:
                    self.session_updated.emit(full_data)
                    return
            self._fallback_load_active_file()

    def _record_current_mtimes(self):
        """记录当前会话及其子智能体当前的 db / wal / transcript mtime，防止轮询初次误判"""
        if not self.current_conv_id:
            return
        db_path = os.path.join(self.conv_dir, f"{self.current_conv_id}.db")
        wal_path = os.path.join(self.conv_dir, f"{self.current_conv_id}.db-wal")
        t_path = os.path.join(self.brain_dir, self.current_conv_id, ".system_generated", "logs", "transcript.jsonl")

        m = 0.0
        if os.path.exists(db_path):
            try:
                m = os.path.getmtime(db_path)
                if os.path.exists(wal_path):
                    m = max(m, os.path.getmtime(wal_path)) + os.path.getsize(wal_path) * 1e-6
            except Exception:
                pass
        self.last_db_mtime = m

        tm = 0.0
        if os.path.exists(t_path):
            try:
                tm = os.path.getmtime(t_path) + os.path.getsize(t_path) * 1e-6
            except Exception:
                pass
        self.last_transcript_mtime = tm

        for sub_id in list(self.discovered_subagents.keys()):
            s_db = os.path.join(self.conv_dir, f"{sub_id}.db")
            s_wal = os.path.join(self.conv_dir, f"{sub_id}.db-wal")
            s_t = os.path.join(self.brain_dir, sub_id, ".system_generated", "logs", "transcript.jsonl")
            if os.path.exists(s_db):
                try:
                    sm = os.path.getmtime(s_db)
                    if os.path.exists(s_wal):
                        sm = max(sm, os.path.getmtime(s_wal)) + os.path.getsize(s_wal) * 1e-6
                    self.subagent_db_mtimes[sub_id] = sm
                except Exception:
                    pass
            if os.path.exists(s_t):
                try:
                    stm = os.path.getmtime(s_t) + os.path.getsize(s_t) * 1e-6
                    self.subagent_t_mtimes[sub_id] = stm
                except Exception:
                    pass

    def switch_to_conversation(self, conv_id: str):
        if conv_id == "__AUTO__":
            self.auto_follow = True
            cdp_id = self.get_cdp_active_conversation_id()
            target_id = cdp_id if cdp_id else self.current_conv_id
            if target_id:
                self.current_conv_id = target_id
                self.discovered_subagents.clear()
                self.subagent_db_mtimes.clear()
                full_data = self.get_convo_stats(target_id)
                self._record_current_mtimes()
                if full_data:
                    self.session_updated.emit(full_data)
            return

        self.auto_follow = False
        self.current_conv_id = conv_id
        self.discovered_subagents.clear()
        self.subagent_db_mtimes.clear()
        full_data = self.get_convo_stats(conv_id)
        self._record_current_mtimes()
        if full_data:
            self.session_updated.emit(full_data)

    def _scan_single_transcript_for_subagents(self, conv_id: str) -> dict:
        """从特定会话的 transcript.jsonl (及 transcript_full.jsonl) 中提取直接派生的子智能体"""
        if not conv_id:
            return {}

        logs_dir = os.path.join(self.brain_dir, conv_id, ".system_generated", "logs")
        transcript_path = os.path.join(logs_dir, "transcript.jsonl")
        transcript_full_path = os.path.join(logs_dir, "transcript_full.jsonl")

        if not os.path.exists(transcript_path):
            return {}

        pending_subagents = []

        # 优先从 transcript_full.jsonl 读取未截断的 invoke_subagent 参数，若无则从 transcript.jsonl 读取
        invoke_scan_path = transcript_full_path if os.path.exists(transcript_full_path) else transcript_path
        try:
            with open(invoke_scan_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "invoke_subagent" not in line:
                        continue
                    try:
                        data = json.loads(line)
                    except Exception:
                        continue
                    tool_calls = data.get("tool_calls") or []
                    for tc in tool_calls:
                        if tc.get("name") == "invoke_subagent":
                            args = tc.get("args", {})
                            raw_subs = args.get("Subagents", [])
                            if isinstance(raw_subs, str):
                                try:
                                    raw_subs = json.loads(raw_subs)
                                except Exception:
                                    roles = re.findall(r'"[Rr]ole":\s*"([^"]+)"', raw_subs)
                                    types = re.findall(r'"(?:TypeName|type)":\s*"([^"]+)"', raw_subs)
                                    raw_subs = [{"Role": r, "TypeName": t} for r, t in zip(roles, types)]
                            if isinstance(raw_subs, list):
                                for s in raw_subs:
                                    if isinstance(s, dict):
                                        pending_subagents.append({
                                            "role": s.get("Role") or s.get("role") or "Subagent",
                                            "type": s.get("TypeName") or s.get("type") or "subagent"
                                        })
        except Exception:
            pass

        found_map = {}
        try:
            with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except Exception:
                        continue

                    content = data.get("content", "")
                    if not content:
                        continue

                    # 过滤终端命令输出、工具改动或异常堆栈等可能包含虚假或旧智能体日志的回显噪音
                    if "The command exited with code" in content or "Output:\n" in content or "The following changes were made by the" in content:
                        continue

                    # 1. 子智能体创建返回
                    if "Created the following subagents:" in content:
                        raw_cids = re.findall(r'"conversationId":\s*"([^"]+)"', content)
                        cids = []
                        for c in raw_cids:
                            if c != conv_id and not c.startswith("{") and (re.match(r'^[0-9a-fA-F-]{36}$', c) or "sub" in c.lower() or c.startswith("agent-")):
                                if c not in cids:
                                    cids.append(c)

                        for cid in cids:
                            info = pending_subagents.pop(0) if pending_subagents else {"role": "Subagent", "type": "subagent"}
                            if cid not in found_map:
                                found_map[cid] = {
                                    "id": cid,
                                    "role": info["role"],
                                    "type": info["type"],
                                    "state": "running",
                                    "lastAction": "运行中..."
                                }

                    # 2. active subagent(s) 状态与最新动作
                    if "active subagent(s):" in content:
                        b1 = content.find("[")
                        b2 = content.rfind("]")
                        if b1 != -1 and b2 != -1:
                            try:
                                active_list = json.loads(content[b1:b2+1], strict=False)
                                for item in active_list:
                                    cid = item.get("conversationId")
                                    if cid and cid != conv_id and not cid.startswith("{"):
                                        st = item.get("state", "running")
                                        mapped_state = "done" if st in ("idle", "done", "errored") else "running"
                                        role = item.get("role")
                                        sub_type = item.get("type")
                                        state_detail = item.get("stateDetail")
                                        if cid not in found_map:
                                            found_map[cid] = {
                                                "id": cid,
                                                "role": role or "Subagent",
                                                "type": sub_type or "subagent",
                                                "state": mapped_state,
                                                "lastAction": state_detail or ("已完成" if mapped_state == "done" else "运行中...")
                                            }
                                        else:
                                            if mapped_state == "done":
                                                found_map[cid]["state"] = "done"
                                            if role and (found_map[cid]["role"] == "Subagent" or not found_map[cid]["role"]):
                                                found_map[cid]["role"] = role
                                            if sub_type and (found_map[cid]["type"] == "subagent" or not found_map[cid]["type"]):
                                                found_map[cid]["type"] = sub_type
                                            if state_detail:
                                                found_map[cid]["lastAction"] = state_detail
                            except Exception:
                                pass

                    # 3. 子智能体向本级发送回执消息（标记为完成）
                    if "sender=" in content:
                        for cid in list(found_map.keys()):
                            if f"sender={cid}" in content:
                                found_map[cid]["state"] = "done"
                                found_map[cid]["lastAction"] = "已完成任务并交付"

            # 4. 补充检查子智能体独立的执行日志，判定是否已调用 send_message 交付任务
            for cid in list(found_map.keys()):
                if found_map[cid]["state"] != "done":
                    sub_t_path = os.path.join(self.brain_dir, cid, ".system_generated", "logs", "transcript.jsonl")
                    if os.path.exists(sub_t_path):
                        try:
                            with open(sub_t_path, "r", encoding="utf-8", errors="ignore") as sf:
                                for s_line in sf:
                                    if '"name": "send_message"' in s_line or '"name":"send_message"' in s_line:
                                        found_map[cid]["state"] = "done"
                                        found_map[cid]["lastAction"] = "已完成任务并交付"
                                        break
                        except Exception:
                            pass
        except Exception:
            pass

        return found_map

    def _discover_subagents(self, primary_conv_id: str) -> list[dict]:
        """从 primary_conv_id 开始，采用 BFS 广度优先递归遍历所有层级的子智能体 (支持 L1, L2, L3... 任意嵌套)"""
        if not primary_conv_id:
            return []

        queue = [(primary_conv_id, 0)]
        visited = {primary_conv_id}
        all_discovered = {}

        while queue:
            curr_id, depth = queue.pop(0)
            children_map = self._scan_single_transcript_for_subagents(curr_id)
            for ch_id, ch_info in children_map.items():
                if ch_id not in all_discovered:
                    ch_info["id"] = ch_id
                    ch_info["parentId"] = curr_id
                    ch_info["depth"] = depth + 1
                    all_discovered[ch_id] = ch_info
                    if ch_id not in visited:
                        visited.add(ch_id)
                        queue.append((ch_id, depth + 1))
                else:
                    if ch_info.get("state") == "done":
                        all_discovered[ch_id]["state"] = "done"
                    if ch_info.get("role") and all_discovered[ch_id]["role"] == "Subagent":
                        all_discovered[ch_id]["role"] = ch_info["role"]
                    if ch_info.get("type") and all_discovered[ch_id]["type"] == "subagent":
                        all_discovered[ch_id]["type"] = ch_info["type"]
                    if ch_info.get("lastAction"):
                        all_discovered[ch_id]["lastAction"] = ch_info["lastAction"]

        # 仅保留本地实际存在物理目录或数据库的合法子智能体
        valid_subagents = []
        for cid, sub in all_discovered.items():
            db_file = os.path.join(self.conv_dir, f"{cid}.db")
            brain_folder = os.path.join(self.brain_dir, cid)
            if os.path.exists(db_file) or os.path.exists(brain_folder) or "sub" in cid.lower() or cid.startswith("agent-"):
                valid_subagents.append(sub)

        # 同步更新本地已发现字典，方便定时器轮询监听 mtime
        self.discovered_subagents = {s["id"]: s for s in valid_subagents}
        return valid_subagents

    def _extract_session_metrics(self, conv_id: str) -> dict:
        """从对应会话的 SQLite 提取用量统计（主会话与子智能体共用）"""
        db_path = os.path.join(self.conv_dir, f"{conv_id}.db")
        if not os.path.exists(db_path) or not extract_usage_from_blob:
            return {
                "promptTokens": 0,
                "candidateTokens": 0,
                "cachedTokens": 0,
                "thinkingTokens": 0,
                "billedTokens": 0,
                "costUsd": 0.0,
                "avgTtft": 0.0,
                "avgSpeed": 0.0,
                "latest": {},
                "has_data": False
            }

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
            return {
                "promptTokens": 0,
                "candidateTokens": 0,
                "cachedTokens": 0,
                "thinkingTokens": 0,
                "billedTokens": 0,
                "costUsd": 0.0,
                "avgTtft": 0.0,
                "avgSpeed": 0.0,
                "latest": {},
                "has_data": False
            }

        avg_ttft = (sum(ttft_list) / len(ttft_list)) if ttft_list else 0.0
        avg_speed = (cum_c / cum_cand_time) if cum_cand_time > 0 else 0.0
        cum_billed = cum_p + cum_c
        # Gemini 3.8 Flash 体验优惠价: 输入 $0.75/M, 输出 $3.75/M, 缓存 $0.15/M
        cum_cost = (cum_p * 0.75 + cum_c * 3.75 + cum_ca * 0.15) / 1e6

        return {
            "promptTokens": cum_p,
            "candidateTokens": cum_c,
            "cachedTokens": cum_ca,
            "thinkingTokens": cum_th,
            "billedTokens": cum_billed,
            "costUsd": round(cum_cost, 4),
            "avgTtft": round(avg_ttft, 2),
            "avgSpeed": round(avg_speed, 1),
            "latest": latest,
            "has_data": bool(rows)
        }

    def _get_cluster_stats(self, primary_conv_id: str) -> dict:
        """递归聚合由 primary_conv_id 派生的全层级子智能体 (含 L1, L2, L3...) 的 Token、费用与树形结构"""
        subagents = self._discover_subagents(primary_conv_id)
        if not subagents:
            return {
                "totalTokens": 0,
                "totalCostUsd": 0.0,
                "combinedCostUsd": 0.0,
                "totalCount": 0,
                "runningCount": 0,
                "doneCount": 0,
                "activeCount": 0,
                "completedCount": 0,
                "subagents": [],
                "allSubagents": []
            }

        cluster_tokens = 0
        cluster_cost = 0.0
        running_cnt = 0
        done_cnt = 0
        all_items = []

        for s in subagents:
            cid = s["id"]
            m = self._extract_session_metrics(cid)
            state = s.get("state", "running")
            if state == "running":
                running_cnt += 1
            else:
                done_cnt += 1

            total_tok = m["billedTokens"]
            cost = m["costUsd"]
            cluster_tokens += total_tok
            cluster_cost += cost

            speed = m["avgSpeed"]
            if speed == 0.0 and m.get("latest"):
                lat = m["latest"]
                dur = lat.get("ttft", 0.0) + lat.get("streaming_duration", 0.0)
                if dur > 0:
                    speed = round(lat.get("candidates", 0) / dur, 1)

            ttft = m["avgTtft"]
            if ttft == 0.0 and m.get("latest"):
                ttft = round(m["latest"].get("ttft", 0.0), 2)

            all_items.append({
                "id": cid,
                "parentId": s.get("parentId", primary_conv_id),
                "depth": s.get("depth", 1),
                "role": s.get("role") or "Subagent",
                "type": s.get("type") or "subagent",
                "state": state,
                "totalTokens": total_tok,
                "costUsd": round(cost, 3),
                "promptTokens": m["promptTokens"],
                "candidateTokens": m["candidateTokens"],
                "thinkingTokens": m["thinkingTokens"],
                "cachedTokens": m["cachedTokens"],
                "ttft": ttft,
                "speed": speed,
                "lastAction": s.get("lastAction") or ("执行中..." if state == "running" else "已完成任务"),
                "children": []
            })

        # 组装树形级联结构
        items_by_id = {item["id"]: item for item in all_items}
        root_items = []
        for item in all_items:
            pid = item.get("parentId")
            if pid and pid in items_by_id:
                items_by_id[pid]["children"].append(item)
            else:
                root_items.append(item)

        return {
            "totalTokens": cluster_tokens,
            "totalCostUsd": round(cluster_cost, 3),
            "combinedCostUsd": 0.0,
            "totalCount": len(all_items),
            "runningCount": running_cnt,
            "doneCount": done_cnt,
            "activeCount": running_cnt,
            "completedCount": done_cnt,
            "subagents": root_items,
            "allSubagents": all_items
        }

    def get_convo_stats(self, conv_id: str, fallback_data=None) -> dict:
        """从对应会话的 SQLite 提取包含总输入、总输出、思考 Token 及 5 大分段的完整指标"""
        metrics = self._extract_session_metrics(conv_id)
        if not metrics.get("has_data"):
            if fallback_data:
                return fallback_data
            return {}

        latest = metrics.get("latest", {})
        turn_p = latest.get("prompt", 0)
        turn_c = latest.get("candidates", 0)
        turn_ca = latest.get("cached", 0)
        turn_th = latest.get("thinking", 0)
        turn_ttft = latest.get("ttft", 0.0)
        turn_sdur = latest.get("streaming_duration", 0.0)
        turn_tot_time = turn_ttft + turn_sdur
        turn_speed = (turn_c / turn_tot_time) if turn_tot_time > 0 else 0.0

        cum_p = metrics["promptTokens"]
        cum_c = metrics["candidateTokens"]
        cum_ca = metrics["cachedTokens"]
        cum_th = metrics["thinkingTokens"]
        cum_billed = metrics["billedTokens"]
        cum_in = cum_p + cum_ca
        cum_ratio = (cum_ca / cum_in * 100) if cum_in > 0 else 0.0
        cum_cost = metrics["costUsd"]
        avg_ttft = metrics["avgTtft"]
        avg_speed = metrics["avgSpeed"]

        # 当前活跃上下文 = 本次未缓存输入 + 本次缓存输入
        active_context = turn_p + turn_ca

        # 计算 5 大模块分解 (系统提示词、工具定义、对话消息、MCP、技能)
        breakdown = self.calculate_context_breakdown(active_context)

        # 计算派生的子智能体集群用量
        cluster = self._get_cluster_stats(conv_id)
        cluster["combinedCostUsd"] = round(cum_cost + cluster["totalCostUsd"], 3)

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
            },
            "cluster": cluster
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
