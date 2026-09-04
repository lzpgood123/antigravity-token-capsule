import os
import sys
import json
import tempfile
import pytest

# Ensure tools/token-capsule is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import capsule_ui

def test_settings_roundtrip(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        settings_file = os.path.join(tmpdir, "capsule_settings.json")
        theme_file = os.path.join(tmpdir, "capsule_theme.json")
        monkeypatch.setattr(capsule_ui, "get_settings_file_path", lambda: settings_file)
        monkeypatch.setattr(capsule_ui, "get_theme_file_path", lambda: theme_file)

        # Initial load when file does not exist -> defaults
        st = capsule_ui.load_saved_settings()
        assert st["theme"] == "light"
        assert st["layout_mode"] == "compact"

        # Save new settings
        capsule_ui.save_settings({"theme": "dark", "layout_mode": "dual_wing"})

        # Reload
        reloaded = capsule_ui.load_saved_settings()
        assert reloaded["theme"] == "dark"
        assert reloaded["layout_mode"] == "dual_wing"

def test_legacy_theme_fallback(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        settings_file = os.path.join(tmpdir, "capsule_settings.json")
        theme_file = os.path.join(tmpdir, "capsule_theme.json")
        monkeypatch.setattr(capsule_ui, "get_settings_file_path", lambda: settings_file)
        monkeypatch.setattr(capsule_ui, "get_theme_file_path", lambda: theme_file)

        # Write legacy theme file only
        with open(theme_file, "w", encoding="utf-8") as f:
            json.dump({"theme": "cyberpunk"}, f)

        st = capsule_ui.load_saved_settings()
        assert st["theme"] == "cyberpunk"
        assert st["layout_mode"] == "compact"
