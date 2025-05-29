import sys
import os
import logging
from pathlib import Path

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from database.bingo_models import Base
from database.bingo_db_manager import BingoDatabaseManager
from config.database_config import get_db_config

def init_database():
    """初始化數據庫"""
    db_manager = None
    try:
        # 獲取數據庫配置
        db_config = get_db_config()
        logger.info("開始初始化數據庫...")
        
        # 創建數據庫管理器
        db_manager = BingoDatabaseManager(db_config['url'])
        
        # 創建所有表
        Base.metadata.create_all(db_manager.engine)
        logger.info("數據庫表創建成功")
        
        # 創建測試用戶
        test_users = [
            ("admin", 10000.0),
            ("test_user", 1000.0),
            ("demo_user", 500.0)
        ]
        
        for user_id, points in test_users:
            user = db_manager.create_user(user_id, points)
            if user:
                logger.info(f"創建用戶成功：{user.user_id}")
            else:
                logger.warning(f"創建用戶失敗：{user_id}")
        
        logger.info("數據庫初始化完成")
        
    except Exception as e:
        logger.error(f"數據庫初始化失敗：{str(e)}")
        raise
    finally:
        if db_manager:
            db_manager.close()
            logger.info("數據庫連接已關閉")

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        logger.error(f"程序執行失敗：{str(e)}")
        sys.exit(1) 