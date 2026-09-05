import os
import sys

# 将工程根目录与 src 目录加入 Python 模块搜索路径
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")

for path in [ROOT_DIR, SRC_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

import pytest

@pytest.fixture(autouse=True)
def isolate_user_settings(tmp_path, monkeypatch):
    """防止测试用例读写和污染用户本机的 ~/.gemini/antigravity/capsule_settings.json"""
    import capsule_ui
    fake_settings = str(tmp_path / "capsule_settings.json")
    fake_theme = str(tmp_path / "capsule_theme.json")
    monkeypatch.setattr(capsule_ui, "get_settings_file_path", lambda: fake_settings)
    monkeypatch.setattr(capsule_ui, "get_theme_file_path", lambda: fake_theme)

