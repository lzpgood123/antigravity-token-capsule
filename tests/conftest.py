import os
import sys

# 将工程根目录与 src 目录加入 Python 模块搜索路径
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")

for path in [ROOT_DIR, SRC_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)
