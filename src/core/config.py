import os
from pathlib import Path
from typing import Dict, Any
import json
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

class Config:
    """配置管理類"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.config: Dict[str, Any] = {}
        self._load_config()
        
    def _load_config(self):
        """加載配置"""
        # 應用程序配置
        self.config.update({
            'APP_NAME': os.getenv('APP_NAME', 'N.L.Online'),
            'APP_VERSION': os.getenv('APP_VERSION', '1.0.0'),
            'APP_ENV': os.getenv('APP_ENV', 'development'),
            'DEBUG': os.getenv('DEBUG', 'True').lower() == 'true',
            
            # 數據庫配置
            'DB_TYPE': os.getenv('DB_TYPE', 'sqlite'),
            'DB_PATH': os.getenv('DB_PATH', str(self.base_dir / 'data/db/nl_online.db')),
            'DB_POOL_SIZE': int(os.getenv('DB_POOL_SIZE', '5')),
            
            # 安全配置
            'SECRET_KEY': os.getenv('SECRET_KEY', 'NL_ONLINE_DEV_SECRET_KEY_2024'),
            'JWT_SECRET': os.getenv('JWT_SECRET', 'NL_ONLINE_JWT_SECRET_2024'),
            'JWT_ALGORITHM': os.getenv('JWT_ALGORITHM', 'HS256'),
            'JWT_EXPIRATION': int(os.getenv('JWT_EXPIRATION', '86400')),
            
            # 更新器配置
            'UPDATER_PATH': os.getenv('UPDATER_PATH', str(self.base_dir / 'src/core/updater/updater.exe')),
            'UPDATE_SERVER': os.getenv('UPDATE_SERVER', 'http://localhost:8000'),
            'UPDATE_CHECK_INTERVAL': int(os.getenv('UPDATE_CHECK_INTERVAL', '3600')),
            
            # API 配置
            'API_BASE_URL': os.getenv('API_BASE_URL', 'http://localhost:8000'),
            'API_VERSION': os.getenv('API_VERSION', 'v1'),
            'API_TIMEOUT': int(os.getenv('API_TIMEOUT', '30')),
            
            # 遊戲配置
            'CASINO_ENABLED': os.getenv('CASINO_ENABLED', 'True').lower() == 'true',
            'MINIGAMES_ENABLED': os.getenv('MINIGAMES_ENABLED', 'True').lower() == 'true',
            'INITIAL_CREDITS': int(os.getenv('INITIAL_CREDITS', '1000')),
            
            # 客服配置
            'AI_CHAT_ENABLED': os.getenv('AI_CHAT_ENABLED', 'True').lower() == 'true',
            'AI_CHAT_MODEL': os.getenv('AI_CHAT_MODEL', 'gpt-3.5-turbo'),
            'AI_CHAT_TIMEOUT': int(os.getenv('AI_CHAT_TIMEOUT', '30')),
            
            # 日誌配置
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'DEBUG'),
            'LOG_PATH': os.getenv('LOG_PATH', str(self.base_dir / 'logs/nl_online.log')),
            'LOG_FORMAT': os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        })
        
        # 確保必要的目錄存在
        self._ensure_directories()
        
    def _ensure_directories(self):
        """確保必要的目錄存在"""
        directories = [
            self.base_dir / 'data/db',
            self.base_dir / 'data/cache',
            self.base_dir / 'logs',
            self.base_dir / 'dist',
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置值"""
        return self.config.get(key, default)
        
    def __getitem__(self, key: str) -> Any:
        """使用字典方式訪問配置"""
        return self.config[key]
        
    def __contains__(self, key: str) -> bool:
        """檢查配置是否存在"""
        return key in self.config
        
    def to_dict(self) -> Dict[str, Any]:
        """返回配置字典的副本"""
        return self.config.copy()
        
    def save(self, path: str = None):
        """保存配置到文件"""
        if path is None:
            path = self.base_dir / 'config.json'
            
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
            
    @classmethod
    def load(cls, path: str = None) -> 'Config':
        """從文件加載配置"""
        config = cls()
        if path is None:
            path = config.base_dir / 'config.json'
            
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                config.config.update(json.load(f))
                
        return config

# 創建全局配置實例
config = Config() 