import os
import sys
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QPointF, QEvent
from PySide6.QtGui import QMouseEvent

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
    assert window.width() == 340 or window.card_frame.width() == 340

def test_data_update_without_subagents(window):
    """Verifies data update for a primary session with zero subagents."""
    data = make_sample_data(with_subagents=False)
    window.update_data(data)

    # Primary cost should not have cluster rollup in parentheses
    assert "$0.081" in window.val_cost.text()
    assert "含 Subagents" not in window.val_cost.text()
    assert "含集群" not in window.val_cost.text()
    # Tab badge should reflect 0
    assert window.btn_tab_cluster.text() in ("🤖 Subagents", "🤖 智能体集群") or "0" in window.btn_tab_cluster.text()

def test_data_update_with_subagents_and_dual_cost(window):
    """Verifies dual-cost linkage and subagent population."""
    data = make_sample_data(with_subagents=True)
    window.update_data(data)

    # Dual cost linkage check
    cost_text = window.val_cost.text()
    assert "$0.081" in cost_text
    assert "含 Subagents: $0.186" in cost_text or "含集群: $0.186" in cost_text

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
    assert "计费" in c1.lbl_tok.text()
    assert "52.4k" in c1.lbl_tok.text()
    assert "计费总量" in c1.toolTip()
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
    assert window.width() == 340
    assert window.wing_divider.isVisible() is False

def test_theme_compatibility(window):
    """Tests that all 5 themes apply cleanly without throwing exceptions."""
    for theme_name in THEME_CONFIGS.keys():
        window.set_theme(theme_name, save=False)
        assert window.get_current_theme() == theme_name

def test_toggle_mode_width_constraints(window):
    """Tests that collapsing to pill releases width constraints and expanding restores them."""
    assert window.is_expanded is True
    assert window.card_frame.isVisible() is True
    assert window.pill_frame.isVisible() is False

    # Collapse to pill
    window.toggle_mode()
    assert window.is_expanded is False
    assert window.card_frame.isVisible() is False
    assert window.pill_frame.isVisible() is True
    assert window.minimumWidth() == 0
    assert window.maximumWidth() == 16777215

    # Expand back to card in compact mode
    window.toggle_mode()
    assert window.is_expanded is True
    assert window.card_frame.isVisible() is True
    assert window.width() == 340

    # Expand back to card in dual_wing mode
    window.set_layout_mode("dual_wing")
    assert window.width() == 680
    window.toggle_mode()
    assert window.minimumWidth() == 0
    window.toggle_mode()
    assert window.width() == 680

def test_cluster_tab_and_pill_indicator_behaviors(window):
    """Tests cluster tab disabled state and pill active indicator."""
    # 1. Without subagents: cluster tab disabled, pill info has no robot icon
    data_no_sub = make_sample_data(with_subagents=False)
    window.update_data(data_no_sub)
    assert window.btn_tab_cluster.isEnabled() is False
    assert "🤖" not in window.pill_info.text()

    # 2. With running subagents: cluster tab enabled, pill info shows robot indicator
    data_with_sub = make_sample_data(with_subagents=True)
    window.update_data(data_with_sub)
    assert window.btn_tab_cluster.isEnabled() is True
    assert "🤖1" in window.pill_info.text()

def test_cluster_view_height_stability(window):
    """Tests that switching to cluster tab does not collapse window height and maintains scroll area minimum height."""
    data = make_sample_data(with_subagents=True)
    window.update_data(data)
    window.set_layout_mode("compact")

    # Primary tab height
    window.switch_tab("primary")
    primary_h = window.height()

    # Switch to cluster tab
    window.switch_tab("cluster")
    cluster_h = window.height()

    # Must NOT collapse into a tiny window (must maintain at least 380px)
    assert cluster_h >= 380
    assert window.scroll_area.minimumHeight() >= 300
    assert abs(primary_h - cluster_h) < 100

def test_drag_isolation_and_teleport_prevention(window):
    """Verifies that clicking or moving mouse over subagent cards does not trigger window drag."""
    data = make_sample_data(with_subagents=True)
    window.update_data(data)
    window.set_layout_mode("dual_wing")

    initial_pos = window.pos()
    assert window.is_dragging is False

    card = window.subagent_cards[0]
    # Simulate left click on card
    press_ev = QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(20, 20),
        QPointF(window.x() + 400, window.y() + 100),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    card.mousePressEvent(press_ev)
    # Window is_dragging should remain False
    assert window.is_dragging is False
    assert card.detail_frame.isVisible() is True

    # Simulate mouse move on card
    move_ev = QMouseEvent(
        QEvent.Type.MouseMove,
        QPointF(25, 25),
        QPointF(window.x() + 405, window.y() + 105),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    card.mouseMoveEvent(move_ev)
    assert move_ev.isAccepted() is True
    # Window position must not teleport or change
    assert window.pos() == initial_pos

def test_hierarchical_tree_rendering_and_branch_toggle(window):
    """Verifies Option A hierarchical tree cards, branch summary calculation, and expandable children container."""
    l2_child1 = {
        "id": "l2-child-0001",
        "parentId": "l1-root-0001",
        "depth": 2,
        "role": "Backend Scout",
        "type": "researcher",
        "state": "running",
        "totalTokens": 20000,
        "costUsd": 0.024,
        "promptTokens": 18000,
        "candidateTokens": 2000,
        "thinkingTokens": 400,
        "cachedTokens": 12000,
        "ttft": 0.28,
        "speed": 62.0,
        "lastAction": "正在搜索架构代码...",
        "children": []
    }
    l2_child2 = {
        "id": "l2-child-0002",
        "parentId": "l1-root-0001",
        "depth": 2,
        "role": "Frontend Scout",
        "type": "developer",
        "state": "done",
        "totalTokens": 30000,
        "costUsd": 0.036,
        "promptTokens": 26000,
        "candidateTokens": 4000,
        "thinkingTokens": 600,
        "cachedTokens": 18000,
        "ttft": 0.32,
        "speed": 75.0,
        "lastAction": "已完成组件构建",
        "children": []
    }
    l1_root = {
        "id": "l1-root-0001",
        "parentId": "primary-0001",
        "depth": 1,
        "role": "Lead Architect",
        "type": "architect",
        "state": "running",
        "totalTokens": 45000,
        "costUsd": 0.054,
        "promptTokens": 40000,
        "candidateTokens": 5000,
        "thinkingTokens": 1000,
        "cachedTokens": 30000,
        "ttft": 0.40,
        "speed": 80.0,
        "lastAction": "协调子任务执行",
        "children": [l2_child1, l2_child2]
    }

    cluster = {
        "totalTokens": 45000 + 20000 + 30000,
        "totalCostUsd": round(0.054 + 0.024 + 0.036, 3),
        "combinedCostUsd": 0.200,
        "totalCount": 3,
        "runningCount": 2,
        "doneCount": 1,
        "activeCount": 2,
        "completedCount": 1,
        "subagents": [l1_root],
        "allSubagents": [l1_root, l2_child1, l2_child2]
    }

    data = {
        "conversationId": "primary-0001",
        "title": "Nested Subagents Session",
        "autoFollow": True,
        "activeContext": 20000,
        "breakdown": {
            "system": {"tokens": 3200, "pct": 16.0},
            "tools": {"tokens": 4600, "pct": 23.0},
            "messages": {"tokens": 6900, "pct": 34.5},
            "mcp": {"tokens": 1500, "pct": 7.5},
            "skills": {"tokens": 3800, "pct": 19.0}
        },
        "turn": {},
        "cumulative": {"costUsd": 0.086, "billedTokens": 20000},
        "cluster": cluster
    }

    window.update_data(data)

    # 1. Total count badge must reflect all 3 subagents
    assert "3" in window.btn_tab_cluster.text()
    assert "共 3 个 Subagent" in window.lbl_wing_count.text()
    assert "95.0k" in window.micro_metric_val.text()

    # 2. Only 1 root card in list layout
    assert len(window.subagent_cards) == 1
    root_card = window.subagent_cards[0]
    assert root_card.depth == 1
    assert "Lead Architect" in root_card.lbl_role.text()

    # 3. Option A: Branch row must exist
    assert hasattr(root_card, "branch_row")
    assert hasattr(root_card, "btn_toggle_branch")
    assert hasattr(root_card, "children_container")
    assert "↳ 派生 2 个子任务" in root_card.lbl_branch_summary.text()
    # Branch totals = 20k + 30k = 50.0k
    assert "50.0k" in root_card.lbl_branch_summary.text()

    # 4. Children container initially hidden (switch to cluster tab so view_cluster is visible)
    window.switch_tab("cluster")
    assert root_card.children_container.isVisible() is False
    assert "展开子任务 ▼" in root_card.btn_toggle_branch.text()

    # 5. Toggle branch expansion
    root_card.toggle_branch()
    assert root_card.children_container.isVisible() is True
    assert "收起子任务 ▲" in root_card.btn_toggle_branch.text()

    # 6. Verify nested child cards inside children_container
    assert len(root_card.child_widgets) == 2
    c1, c2 = root_card.child_widgets
    assert c1.depth == 2
    assert "Backend Scout" in c1.lbl_role.text()
    assert "L2 ·" in c1.lbl_sub.text()
    assert "20.0k" in c1.lbl_tok.text()

    assert c2.depth == 2
    assert "Frontend Scout" in c2.lbl_role.text()
    assert "L2 ·" in c2.lbl_sub.text()
    assert "30.0k" in c2.lbl_tok.text()

    # 7. Independent accordion expansion in nested child card
    assert c1.detail_frame.isVisible() is False
    c1.toggle_accordion()
    assert c1.detail_frame.isVisible() is True
    assert root_card.detail_frame.isVisible() is False  # parent accordion unaffected

def test_long_unspaced_type_name_and_branch_layout(window):
    """Verifies that long continuous camelCase type names do not push right-side metrics off-screen."""
    l2_long_type_child = {
        "id": "l2-long-0001",
        "parentId": "l1-root-0002",
        "depth": 2,
        "role": "ImprovementWorker",
        "type": "DeepInvestigatorImprovementWorker",
        "state": "running",
        "totalTokens": 15000,
        "costUsd": 0.018,
        "promptTokens": 13000,
        "candidateTokens": 2000,
        "thinkingTokens": 200,
        "cachedTokens": 8000,
        "ttft": 0.35,
        "speed": 65.0,
        "lastAction": "运行中...",
        "children": []
    }
    l1_root = {
        "id": "l1-root-0002",
        "parentId": "primary-0002",
        "depth": 1,
        "role": "Lead Architect",
        "type": "architect",
        "state": "running",
        "totalTokens": 30000,
        "costUsd": 0.036,
        "promptTokens": 27000,
        "candidateTokens": 3000,
        "thinkingTokens": 500,
        "cachedTokens": 20000,
        "ttft": 0.40,
        "speed": 75.0,
        "lastAction": "运行中...",
        "children": [l2_long_type_child]
    }
    cluster = {
        "totalTokens": 45000,
        "totalCostUsd": 0.054,
        "combinedCostUsd": 0.100,
        "totalCount": 2,
        "runningCount": 2,
        "doneCount": 0,
        "activeCount": 2,
        "completedCount": 0,
        "subagents": [l1_root],
        "allSubagents": [l1_root, l2_long_type_child]
    }
    data = {
        "conversationId": "primary-0002",
        "title": "Long Type Name Session",
        "activeContext": 15000,
        "breakdown": {},
        "turn": {},
        "cumulative": {"costUsd": 0.046, "billedTokens": 15000},
        "cluster": cluster
    }
    window.update_data(data)
    window.switch_tab("cluster")

    root_card = window.subagent_cards[0]
    root_card.toggle_branch()
    assert root_card.children_container.isVisible() is True

    child_card = root_card.child_widgets[0]
    assert child_card.lbl_sub.wordWrap() is True
    assert child_card.lbl_tok.text() == "计费 15.0k"
    assert child_card.lbl_cost.text() == "$0.018"
    assert child_card.lbl_chevron.text() == "▼"
    # Ensure window width is maintained at 340 without forcing window to stretch
    assert window.width() == 340



