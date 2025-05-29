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

def init_test_database():
    """初始化測試數據庫"""
    db_manager = None
    try:
        # 設置測試環境
        os.environ['ENV'] = 'testing'
        logger.info("設置測試環境")
        
        # 獲取數據庫配置
        db_config = get_db_config()
        logger.info("開始初始化測試數據庫...")
        
        # 創建數據庫管理器
        db_manager = BingoDatabaseManager(db_config['url'])
        
        # 創建所有表
        Base.metadata.create_all(db_manager.engine)
        logger.info("測試數據庫表創建成功")
        
        # 創建測試用戶
        test_users = [
            ("test_user1", 1000.0),
            ("test_user2", 2000.0),
            ("test_user3", 3000.0),
            ("test_admin", 10000.0)
        ]
        
        for user_id, points in test_users:
            user = db_manager.create_user(user_id, points)
            if user:
                logger.info(f"創建測試用戶成功：{user.user_id}")
            else:
                logger.warning(f"創建測試用戶失敗：{user_id}")
        
        # 創建測試遊戲記錄
        for user_id in [u[0] for u in test_users]:
            # 創建一些測試遊戲記錄
            for i in range(3):
                game_data = {
                    'user_id': user_id,
                    'bet_amount': 100.0,
                    'card_count': 1,
                    'drawn_balls': [1, 2, 3, 4, 5],
                    'winning_patterns': ['horizontal'],
                    'win_amount': 500.0 if i == 0 else 0.0
                }
                db_manager.record_game_history(game_data)
                logger.info(f"創建測試遊戲記錄：{user_id} - 遊戲 {i+1}")
        
        logger.info("測試數據庫初始化完成")
        
    except Exception as e:
        logger.error(f"測試數據庫初始化失敗：{str(e)}")
        raise
    finally:
        if db_manager:
            db_manager.close()
            logger.info("測試數據庫連接已關閉")

if __name__ == "__main__":
    try:
        init_test_database()
    except Exception as e:
        logger.error(f"程序執行失敗：{str(e)}")
        sys.exit(1) 