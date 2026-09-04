import os
import sys
import json
import sqlite3
import tempfile
import shutil
import pytest

# Ensure tools/token-capsule is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from data_engine import DataEngine
from proto_decoder import extract_usage_from_blob

def make_test_proto_blob(prompt=1000, candidates=200, cached=500, thinking=50, ttft=0.25, duration=1.0):
    """
    Constructs a protobuf binary blob matching Google Antigravity Usage format:
    outer_fields: field 1 (bytes)
      inner_fields:
        field 4 (bytes): varints (2: prompt, 3: candidates, 5: cached, 9: thinking)
        field 11 (bytes): varints (1: seconds, 2: nanos)
        field 12 (bytes): varints (1: seconds, 2: nanos)
    """
    def encode_varint(value):
        buf = bytearray()
        while True:
            b = value & 0x7F
            value >>= 7
            if value:
                buf.append(b | 0x80)
            else:
                buf.append(b)
                break
        return bytes(buf)

    def field_varint(field_num, value):
        tag = (field_num << 3) | 0
        return encode_varint(tag) + encode_varint(value)

    def field_bytes(field_num, data):
        tag = (field_num << 3) | 2
        return encode_varint(tag) + encode_varint(len(data)) + data

    u_buf = bytearray()
    u_buf += field_varint(2, prompt)
    u_buf += field_varint(3, candidates)
    u_buf += field_varint(5, cached)
    u_buf += field_varint(9, thinking)

    ttft_sec = int(ttft)
    ttft_nano = int((ttft - ttft_sec) * 1e9)
    ttft_buf = field_varint(1, ttft_sec) + field_varint(2, ttft_nano)

    dur_sec = int(duration)
    dur_nano = int((duration - dur_sec) * 1e9)
    dur_buf = field_varint(1, dur_sec) + field_varint(2, dur_nano)

    inner_buf = bytearray()
    inner_buf += field_bytes(4, bytes(u_buf))
    inner_buf += field_bytes(11, bytes(ttft_buf))
    inner_buf += field_bytes(12, bytes(dur_buf))

    return bytes(field_bytes(1, bytes(inner_buf)))

def create_mock_db(db_path, blobs):
    """Creates a mock SQLite conversation database with gen_metadata table."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("CREATE TABLE gen_metadata (idx INTEGER PRIMARY KEY, data BLOB)")
    for idx, b in enumerate(blobs):
        c.execute("INSERT INTO gen_metadata (idx, data) VALUES (?, ?)", (idx, b))
    conn.commit()
    conn.close()

@pytest.fixture
def mock_antigravity_env():
    """Sets up a temporary sandboxed environment mimicking ~/.gemini/antigravity."""
    tmp_root = tempfile.mkdtemp(prefix="agy_test_")
    conv_dir = os.path.join(tmp_root, "conversations")
    brain_dir = os.path.join(tmp_root, "brain")
    os.makedirs(conv_dir, exist_ok=True)
    os.makedirs(brain_dir, exist_ok=True)

    yield {
        "root": tmp_root,
        "conv_dir": conv_dir,
        "brain_dir": brain_dir
    }

    shutil.rmtree(tmp_root, ignore_errors=True)

def test_single_session_without_subagents(mock_antigravity_env):
    """Tests that a single conversation without subagents returns proper cluster defaults."""
    env = mock_antigravity_env
    engine = DataEngine()
    engine.conv_dir = env["conv_dir"]
    engine.brain_dir = env["brain_dir"]

    # Create a primary conversation DB
    primary_id = "11111111-2222-3333-4444-555555555555"
    primary_db = os.path.join(env["conv_dir"], f"{primary_id}.db")
    blob1 = make_test_proto_blob(prompt=10000, candidates=1000, cached=5000, thinking=100, ttft=0.4, duration=0.8)
    create_mock_db(primary_db, [blob1])

    stats = engine.get_convo_stats(primary_id)
    assert stats is not None
    assert stats["conversationId"] == primary_id
    assert "cluster" in stats

    cluster = stats["cluster"]
    assert cluster["totalTokens"] == 0
    assert cluster["totalCostUsd"] == 0.0
    assert cluster["combinedCostUsd"] == stats["cumulative"]["costUsd"]
    assert cluster["runningCount"] == 0
    assert cluster["doneCount"] == 0
    assert cluster["activeCount"] == 0
    assert cluster["completedCount"] == 0
    assert cluster["subagents"] == []

def test_session_with_discovered_subagents(mock_antigravity_env):
    """Tests discovery and metric rollup of subagents from transcript.jsonl and subagent DBs."""
    env = mock_antigravity_env
    engine = DataEngine()
    engine.conv_dir = env["conv_dir"]
    engine.brain_dir = env["brain_dir"]

    primary_id = "primary-0001-0002-0003-000000000001"
    sub1_id = "subagent-0001-0001-0001-000000000001"
    sub2_id = "subagent-0002-0002-0002-000000000002"

    # 1. Create primary DB
    primary_db = os.path.join(env["conv_dir"], f"{primary_id}.db")
    p_blob = make_test_proto_blob(prompt=20000, candidates=2000, cached=10000, thinking=200, ttft=0.5, duration=1.0)
    create_mock_db(primary_db, [p_blob])

    # 2. Create subagents DBs
    sub1_db = os.path.join(env["conv_dir"], f"{sub1_id}.db")
    sub1_blob = make_test_proto_blob(prompt=40000, candidates=4000, cached=30000, thinking=500, ttft=0.3, duration=1.2)
    create_mock_db(sub1_db, [sub1_blob])

    sub2_db = os.path.join(env["conv_dir"], f"{sub2_id}.db")
    sub2_blob = make_test_proto_blob(prompt=15000, candidates=1500, cached=5000, thinking=150, ttft=0.2, duration=0.5)
    create_mock_db(sub2_db, [sub2_blob])

    # 3. Create primary transcript.jsonl recording subagent invocation and active list
    logs_dir = os.path.join(env["brain_dir"], primary_id, ".system_generated", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    transcript_file = os.path.join(logs_dir, "transcript.jsonl")

    lines = [
        # Call invoke_subagent
        json.dumps({
            "step_index": 1,
            "source": "MODEL",
            "type": "PLANNER_RESPONSE",
            "tool_calls": [{
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {"Role": "Explorer 1 (Backend)", "TypeName": "explorer"},
                        {"Role": "Reviewer (Quality)", "TypeName": "reviewer"}
                    ]
                }
            }]
        }),
        # Tool response creating subagents
        json.dumps({
            "step_index": 2,
            "source": "MODEL",
            "type": "GENERIC",
            "content": f'Created the following subagents:\n{{\n  "conversationId":  "{sub1_id}",\n  "logAbsoluteUri":  "..."\n}}\n{{\n  "conversationId":  "{sub2_id}",\n  "logAbsoluteUri":  "..."\n}}'
        }),
        # Active subagents state update: sub1 is running, sub2 is idle/done
        json.dumps({
            "step_index": 3,
            "source": "MODEL",
            "type": "GENERIC",
            "content": f'You have 2 active subagent(s):\n[{{\n  "conversationId": "{sub1_id}",\n  "role": "Explorer 1 (Backend)",\n  "type": "explorer",\n  "state": "running",\n  "stateDetail": "正在执行搜索..."\n}},{{\n  "conversationId": "{sub2_id}",\n  "role": "Reviewer (Quality)",\n  "type": "reviewer",\n  "state": "idle",\n  "stateDetail": "已完成"\n}}]'
        })
    ]
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    # Discover and compute stats
    stats = engine.get_convo_stats(primary_id)
    assert stats is not None
    cluster = stats["cluster"]

    assert len(cluster["subagents"]) == 2
    assert cluster["runningCount"] == 1
    assert cluster["doneCount"] == 1
    assert cluster["activeCount"] == 1
    assert cluster["completedCount"] == 1

    # Check subagent 1 metrics
    s1 = next(s for s in cluster["subagents"] if s["id"] == sub1_id)
    assert s1["role"] == "Explorer 1 (Backend)"
    assert s1["state"] == "running"
    assert s1["totalTokens"] == 40000 + 4000
    assert s1["promptTokens"] == 40000
    assert s1["candidateTokens"] == 4000
    assert s1["cachedTokens"] == 30000
    assert s1["lastAction"] == "正在执行搜索..."

    # Check subagent 2 metrics
    s2 = next(s for s in cluster["subagents"] if s["id"] == sub2_id)
    assert s2["role"] == "Reviewer (Quality)"
    assert s2["state"] == "done"
    assert s2["totalTokens"] == 15000 + 1500

    # Check rollups
    expected_sub_tokens = (40000 + 4000) + (15000 + 1500)
    assert cluster["totalTokens"] == expected_sub_tokens
    assert cluster["totalCostUsd"] > 0
    assert cluster["combinedCostUsd"] == round(stats["cumulative"]["costUsd"] + cluster["totalCostUsd"], 3)

def test_polling_incremental_subagent_updates(mock_antigravity_env):
    """Tests that _poll_updates emits session_updated when subagent DB changes and skips when unchanged."""
    env = mock_antigravity_env
    engine = DataEngine()
    engine.conv_dir = env["conv_dir"]
    engine.brain_dir = env["brain_dir"]
    engine.auto_follow = False

    primary_id = "primary-poll-0001"
    sub_id = "sub-poll-0001"

    # Create primary DB
    primary_db = os.path.join(env["conv_dir"], f"{primary_id}.db")
    create_mock_db(primary_db, [make_test_proto_blob(prompt=1000, candidates=100)])

    # Create subagent DB
    sub_db = os.path.join(env["conv_dir"], f"{sub_id}.db")
    create_mock_db(sub_db, [make_test_proto_blob(prompt=2000, candidates=200)])

    # Create transcript
    logs_dir = os.path.join(env["brain_dir"], primary_id, ".system_generated", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    with open(os.path.join(logs_dir, "transcript.jsonl"), "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "step_index": 1,
            "source": "MODEL",
            "type": "GENERIC",
            "content": f'Created the following subagents:\n{{\n  "conversationId":  "{sub_id}"\n}}'
        }) + "\n")

    emitted_payloads = []
    engine.session_updated.connect(lambda data: emitted_payloads.append(data))

    engine.switch_to_conversation(primary_id)
    assert len(emitted_payloads) == 1
    assert emitted_payloads[-1]["cluster"]["totalTokens"] == 2200

    # Poll without changes -> should NOT emit (0% unnecessary CPU)
    engine._poll_updates()
    assert len(emitted_payloads) == 1

    # Simulate subagent producing new tokens in SQLite DB
    conn = sqlite3.connect(sub_db)
    c = conn.cursor()
    c.execute("INSERT INTO gen_metadata (idx, data) VALUES (?, ?)", (1, make_test_proto_blob(prompt=3000, candidates=300)))
    conn.commit()
    conn.close()

    # Poll with changes -> should detect mtime update and emit fresh data
    engine._poll_updates()
    assert len(emitted_payloads) == 2
    assert emitted_payloads[-1]["cluster"]["totalTokens"] == 2200 + 3300

def test_subagents_pending_queue_desync_protection(mock_antigravity_env):
    """Tests that pending_subagents queue pops in exact 1-to-1 sync even when duplicate entries or multiple batches occur."""
    env = mock_antigravity_env
    engine = DataEngine()
    engine.conv_dir = env["conv_dir"]
    engine.brain_dir = env["brain_dir"]

    primary_id = "primary-queue-001"
    sub1_id = "sub-queue-001"
    sub2_id = "sub-queue-002"

    logs_dir = os.path.join(env["brain_dir"], primary_id, ".system_generated", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    transcript_file = os.path.join(logs_dir, "transcript.jsonl")

    lines = [
        # Call with 2 subagents
        json.dumps({
            "step_index": 1,
            "source": "MODEL",
            "type": "PLANNER_RESPONSE",
            "tool_calls": [{
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {"Role": "Role One", "TypeName": "type_one"},
                        {"Role": "Role Two", "TypeName": "type_two"}
                    ]
                }
            }]
        }),
        # Tool response with sub1_id twice (e.g. repeated block or log reprint) and then sub2_id
        json.dumps({
            "step_index": 2,
            "source": "MODEL",
            "type": "GENERIC",
            "content": f'Created the following subagents:\n"conversationId": "{sub1_id}"\n"conversationId": "{sub1_id}"\n"conversationId": "{sub2_id}"'
        })
    ]
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    subs = engine._discover_subagents(primary_id)
    assert len(subs) == 2
    s1 = next(s for s in subs if s["id"] == sub1_id)
    assert s1["role"] == "Role One"
    assert s1["type"] == "type_one"

    s2 = next(s for s in subs if s["id"] == sub2_id)
    # Even if sub1_id appeared twice in content, queue is drained appropriately
    assert s2["role"] in ("Role Two", "Subagent")

def test_ignore_command_output_and_message_completion(mock_antigravity_env):
    """Tests that command stdout noise is ignored and subagent completion via message is recognized."""
    env = mock_antigravity_env
    engine = DataEngine()
    engine.conv_dir = env["conv_dir"]
    engine.brain_dir = env["brain_dir"]

    primary_id = "primary-real-001"
    sub_real_id = "sub-real-001"
    fake_id = "fake-template-id"

    # Create dummy brain folder for real subagent so it passes validation
    os.makedirs(os.path.join(env["brain_dir"], sub_real_id), exist_ok=True)

    logs_dir = os.path.join(env["brain_dir"], primary_id, ".system_generated", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    transcript_file = os.path.join(logs_dir, "transcript.jsonl")

    lines = [
        # Terminal command output containing fake subagent string (like grep results)
        json.dumps({
            "step_index": 1,
            "source": "MODEL",
            "type": "GENERIC",
            "content": 'The command exited with code 0.\nOutput:\nFound line with sub:\nCreated the following subagents:\n"conversationId": "{sub1_id}"'
        }),
        # Real invoke_subagent call
        json.dumps({
            "step_index": 2,
            "source": "MODEL",
            "type": "PLANNER_RESPONSE",
            "tool_calls": [{
                "name": "invoke_subagent",
                "args": {
                    "Subagents": json.dumps([{"Role": "Deep Reviewer", "TypeName": "research"}])
                }
            }]
        }),
        # Real creation result
        json.dumps({
            "step_index": 3,
            "source": "MODEL",
            "type": "GENERIC",
            "content": f'Created At: 2026-09-04T12:00:00Z\nCompleted At: 2026-09-04T12:00:00Z\nCreated the following subagents:\n{{\n  "conversationId": "{sub_real_id}"\n}}\nThe subagents will send you a message when they have completed their task.'
        }),
        # Subagent message delivery to parent
        json.dumps({
            "step_index": 4,
            "source": "SYSTEM",
            "type": "SYSTEM_MESSAGE",
            "content": f'<SYSTEM_MESSAGE>\n[Message] sender={sub_real_id} priority=MESSAGE_PRIORITY_HIGH content=Review is done!'
        })
    ]
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    subs = engine._discover_subagents(primary_id)
    # Must NOT discover fake {sub1_id}
    assert len(subs) == 1
    assert subs[0]["id"] == sub_real_id
    assert subs[0]["role"] == "Deep Reviewer"
    assert subs[0]["state"] == "done"
    assert "已完成" in subs[0]["lastAction"]

