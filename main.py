# main.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*- 
import uvicorn
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# 設置 Qt 屬性
from PyQt5.QtCore import Qt, QCoreApplication
QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)

from PyQt5.QtWidgets import QApplication
from src.api.routes import app
from src.database.db_manager import db_manager
from src.config.usdt_config import config
from src.ui.main_window import MainWindow

# 設置日誌
def setup_logging():
    """設置日誌"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                filename=os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log"),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
        ]
    )
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

def init_database():
    """初始化數據庫"""
    try:
        if not db_manager.check_connection():
            raise Exception("數據庫連接失敗")
        db_manager.create_tables()
        logging.info("數據庫初始化成功")
    except Exception as e:
        logging.error(f"數據庫初始化失敗: {str(e)}")
        raise

def main():
    """主函數"""
    try:
        setup_logging()
        logging.info("啟動應用")
        init_database()
        
        # 初始化測試帳號
        from src.core.auth import Auth
        Auth.init_test_account()
        
        uvicorn.run(
            app,
            host=config.API_HOST,
            port=config.API_PORT,
            reload=config.DEBUG,
            workers=config.API_WORKERS,
            log_level="info"
        )
    except Exception as e:
        logging.error(f"啟動應用錯誤: {str(e)}")
        raise

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    from src.ui.main_window import MainWindow

    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
