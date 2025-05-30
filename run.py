import os
import sys

# 添加專案根目錄到 Python 路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 運行應用程式
from src.core.application import RanOnlineApp

if __name__ == '__main__':
    app = RanOnlineApp()
    sys.exit(app.run()) 