import os
from pathlib import Path

# 數據庫配置
DATABASE_CONFIG = {
    'development': {
        'url': 'sqlite:///bingo_game.db',
        'echo': True  # 顯示SQL語句，方便調試
    },
    'testing': {
        'url': 'sqlite:///test_bingo_game.db',
        'echo': False
    },
    'production': {
        'url': os.getenv('DATABASE_URL', 'sqlite:///bingo_game.db'),
        'echo': False
    }
}

# 獲取當前環境
ENV = os.getenv('ENV', 'development')

# 數據庫文件路徑
DB_PATH = Path(__file__).parent.parent / 'data'
DB_PATH.mkdir(exist_ok=True)

# 獲取當前環境的數據庫配置
def get_db_config():
    """獲取數據庫配置"""
    config = DATABASE_CONFIG[ENV]
    if 'sqlite' in config['url']:
        # 確保數據庫目錄存在
        DB_PATH.mkdir(exist_ok=True)
        # 更新SQLite數據庫路徑
        db_file = DB_PATH / config['url'].split('/')[-1]
        config['url'] = f'sqlite:///{db_file}'
    return config 