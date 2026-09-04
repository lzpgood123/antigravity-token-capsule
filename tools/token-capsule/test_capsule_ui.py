import os
import sys
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Ensure tools/token-capsule is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from capsule_ui import CapsuleWindow, THEME_CONFIGS

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.fixture
def window(qapp):
    win = CapsuleWindow(default_layout_mode="compact")
    win.show()
    yield win
    win.close()

def make_sample_data(with_subagents=True):
    subagents = []
    if with_subagents:
        subagents = [
            {
                "id": "sub-1111",
                "role": "Explorer 1 (Backend)",
                "type": "explorer",
                "state": "running",
                "totalTokens": 52400,
                "costUsd": 0.063,
                "promptTokens": 48000,
                "candidateTokens": 4400,
                "thinkingTokens": 1200,
                "cachedTokens": 42000,
                "ttft": 0.38,
                "speed": 74.0,
                "lastAction": "正在执行 ripgrep 搜索..."
            },
            {
                "id": "sub-2222",
                "role": "Reviewer (Architecture)",
                "type": "reviewer",
                "state": "done",
                "totalTokens": 34900,
                "costUsd": 0.042,
                "promptTokens": 32000,
                "candidateTokens": 2900,
                "thinkingTokens": 800,
                "cachedTokens": 25000,
                "ttft": 0.42,
                "speed": 82.0,
                "lastAction": "已完成代码审查"
            }
        ]

    cluster = {
        "totalTokens": 87300 if with_subagents else 0,
        "totalCostUsd": 0.105 if with_subagents else 0.0,
        "combinedCostUsd": 0.186 if with_subagents else 0.081,
        "runningCount": 1 if with_subagents else 0,
        "doneCount": 1 if with_subagents else 0,
        "activeCount": 1 if with_subagents else 0,
        "completedCount": 1 if with_subagents else 0,
        "subagents": subagents
    }

    return {
        "conversationId": "primary-9999",
        "title": "Primary Task Session",
        "autoFollow": True,
        "activeContext": 26800,
        "breakdown": {
            "system": {"tokens": 8200, "pct": 3.2},
            "tools": {"tokens": 5400, "pct": 2.1},
            "messages": {"tokens": 9100, "pct": 3.6},
            "mcp": {"tokens": 2300, "pct": 0.9},
            "skills": {"tokens": 1800, "pct": 0.7}
        },
        "turn": {
            "promptTokens": 5000,
            "candidateTokens": 1200,
            "cachedTokens": 3000,
            "thinkingTokens": 200,
            "costUsd": 0.012,
            "ttft": 0.42,
            "speed": 68.0
        },
        "cumulative": {
            "promptTokens": 20000,
            "candidateTokens": 6800,
            "cachedTokens": 15000,
            "thinkingTokens": 1000,
            "billedTokens": 26800,
            "totalContext": 41800,
            "cacheRatio": 35.9,
            "costUsd": 0.081,
            "avgTtft": 0.45,
            "avgSpeed": 65.0
        },
        "cluster": cluster
    }

def test_window_initialization(window):
    """Verifies that window initializes in compact mode with tab bar and default views."""
    assert window is not None
    assert hasattr(window, "tab_bar")
    assert hasattr(window, "btn_tab_primary")
    assert hasattr(window, "btn_tab_cluster")
    assert window.layout_mode == "compact"
    assert window.width() == 320 or window.card_frame.width() == 320

def test_data_update_without_subagents(window):
    """Verifies data update for a primary session with zero subagents."""
    data = make_sample_data(with_subagents=False)
    window.update_data(data)

    # Primary cost should not have cluster rollup in parentheses
    assert "$0.081" in window.val_cost.text()
    assert "含集群" not in window.val_cost.text()
    # Tab badge should reflect 0
    assert window.btn_tab_cluster.text() == "🤖 智能体集群" or "0" in window.btn_tab_cluster.text()

def test_data_update_with_subagents_and_dual_cost(window):
    """Verifies dual-cost linkage and subagent population."""
    data = make_sample_data(with_subagents=True)
    window.update_data(data)

    # Dual cost linkage check
    cost_text = window.val_cost.text()
    assert "$0.081" in cost_text
    assert "含集群: $0.186" in cost_text

    # Tab badge should show 2 agents
    assert "2" in window.btn_tab_cluster.text()

    # Micro-dashboard in cluster view
    assert hasattr(window, "micro_metric_val")
    assert "87.3k" in window.micro_metric_val.text()
    assert "$0.105" in window.micro_metric_val.text()
    assert "1 运行" in window.micro_status_pill.text()
    assert "1 完成" in window.micro_status_pill.text()

    # Subagent cards list populated
    assert len(window.subagent_cards) == 2
    c1 = window.subagent_cards[0]
    assert c1.agent_data["role"] == "Explorer 1 (Backend)"
    assert c1.agent_data["state"] == "running"
    # Switch to cluster tab to inspect subagent card accordion
    window.switch_tab("cluster")
    assert c1.detail_frame.isVisible() is False

    # Toggle accordion
    c1.toggle_accordion()
    assert c1.detail_frame.isVisible() is True
    c1.toggle_accordion()
    assert c1.detail_frame.isVisible() is False

def test_tab_switching(window):
    """Tests switching between Primary and Cluster tabs in compact mode."""
    data = make_sample_data(with_subagents=True)
    window.update_data(data)

    # Switch to cluster
    window.switch_tab("cluster")
    assert window.active_tab == "cluster"
    assert window.view_cluster.isVisible() is True
    assert window.view_primary.isVisible() is False

    # Switch to primary
    window.switch_tab("primary")
    assert window.active_tab == "primary"
    assert window.view_primary.isVisible() is True
    assert window.view_cluster.isVisible() is False

def test_layout_mode_switching(window):
    """Tests switching between Compact (320px) and Dual-Wing (680px) modes."""
    data = make_sample_data(with_subagents=True)
    window.update_data(data)

    # Switch to dual_wing
    window.set_layout_mode("dual_wing")
    assert window.layout_mode == "dual_wing"
    assert window.width() == 680
    assert window.wing_divider.isVisible() is True
    assert window.view_primary.isVisible() is True
    assert window.view_cluster.isVisible() is True

    # Switch back to compact
    window.set_layout_mode("compact")
    assert window.layout_mode == "compact"
    assert window.width() == 320
    assert window.wing_divider.isVisible() is False

def test_theme_compatibility(window):
    """Tests that all 5 themes apply cleanly without throwing exceptions."""
    for theme_name in THEME_CONFIGS.keys():
        window.set_theme(theme_name, save=False)
        assert window.get_current_theme() == theme_name
