import sys
import os
import logging
import datetime
from pathlib import Path
import click
import json
import sqlite3
from typing import List, Dict, Any

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

# 遷移文件目錄
MIGRATIONS_DIR = project_root / 'migrations'
MIGRATIONS_DIR.mkdir(exist_ok=True)

class Migration:
    """數據庫遷移"""
    
    def __init__(self, version: int, name: str, up_sql: str, down_sql: str):
        self.version = version
        self.name = name
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.created_at = datetime.datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'version': self.version,
            'name': self.name,
            'up_sql': self.up_sql,
            'down_sql': down_sql,
            'created_at': self.created_at.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Migration':
        migration = cls(
            version=data['version'],
            name=data['name'],
            up_sql=data['up_sql'],
            down_sql=data['down_sql']
        )
        migration.created_at = datetime.datetime.fromisoformat(data['created_at'])
        return migration

class MigrationManager:
    """遷移管理器"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = sqlite3.connect(db_url.replace('sqlite:///', ''))
        self.cursor = self.conn.cursor()
        self._init_migrations_table()
        
    def _init_migrations_table(self):
        """初始化遷移表"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        
    def get_applied_migrations(self) -> List[int]:
        """獲取已應用的遷移版本"""
        self.cursor.execute('SELECT version FROM migrations ORDER BY version')
        return [row[0] for row in self.cursor.fetchall()]
        
    def apply_migration(self, migration: Migration):
        """應用遷移"""
        try:
            # 開始事務
            self.conn.execute('BEGIN')
            
            # 執行遷移SQL
            for sql in migration.up_sql.split(';'):
                if sql.strip():
                    self.conn.execute(sql)
                    
            # 記錄遷移
            self.conn.execute(
                'INSERT INTO migrations (version, name) VALUES (?, ?)',
                (migration.version, migration.name)
            )
            
            # 提交事務
            self.conn.commit()
            logger.info(f"成功應用遷移：{migration.name} (v{migration.version})")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"應用遷移失敗：{str(e)}")
            raise
            
    def rollback_migration(self, migration: Migration):
        """回滾遷移"""
        try:
            # 開始事務
            self.conn.execute('BEGIN')
            
            # 執行回滾SQL
            for sql in migration.down_sql.split(';'):
                if sql.strip():
                    self.conn.execute(sql)
                    
            # 刪除遷移記錄
            self.conn.execute(
                'DELETE FROM migrations WHERE version = ?',
                (migration.version,)
            )
            
            # 提交事務
            self.conn.commit()
            logger.info(f"成功回滾遷移：{migration.name} (v{migration.version})")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"回滾遷移失敗：{str(e)}")
            raise
            
    def close(self):
        """關閉數據庫連接"""
        self.conn.close()

def create_migration(name: str) -> Migration:
    """創建新的遷移"""
    # 獲取當前最高版本
    versions = [0]
    for file in MIGRATIONS_DIR.glob('*.json'):
        try:
            version = int(file.stem.split('_')[0])
            versions.append(version)
        except ValueError:
            continue
            
    new_version = max(versions) + 1
    
    # 創建遷移對象
    migration = Migration(
        version=new_version,
        name=name,
        up_sql='',  # 需要手動填寫
        down_sql=''  # 需要手動填寫
    )
    
    # 保存遷移文件
    migration_file = MIGRATIONS_DIR / f'{new_version:03d}_{name}.json'
    with open(migration_file, 'w') as f:
        json.dump(migration.to_dict(), f, indent=2)
        
    logger.info(f"創建遷移文件：{migration_file}")
    return migration

def load_migrations() -> List[Migration]:
    """加載所有遷移"""
    migrations = []
    for file in sorted(MIGRATIONS_DIR.glob('*.json')):
        try:
            with open(file) as f:
                data = json.load(f)
                migrations.append(Migration.from_dict(data))
        except Exception as e:
            logger.error(f"加載遷移文件失敗 {file}: {str(e)}")
    return migrations

@click.group()
def cli():
    """數據庫遷移工具"""
    pass

@cli.command()
@click.argument('name')
def create(name):
    """創建新的遷移"""
    try:
        migration = create_migration(name)
        logger.info(f"創建遷移成功：{migration.name} (v{migration.version})")
    except Exception as e:
        logger.error(f"創建遷移失敗：{str(e)}")

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def migrate(env):
    """應用所有未應用的遷移"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建遷移管理器
        manager = MigrationManager(db_config['url'])
        
        # 獲取已應用的遷移
        applied_versions = manager.get_applied_migrations()
        
        # 加載所有遷移
        migrations = load_migrations()
        
        # 應用未應用的遷移
        for migration in migrations:
            if migration.version not in applied_versions:
                manager.apply_migration(migration)
                
        logger.info("所有遷移已應用")
        
    except Exception as e:
        logger.error(f"應用遷移失敗：{str(e)}")
    finally:
        if 'manager' in locals():
            manager.close()

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def rollback(env):
    """回滾最後一個遷移"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建遷移管理器
        manager = MigrationManager(db_config['url'])
        
        # 獲取已應用的遷移
        applied_versions = manager.get_applied_migrations()
        if not applied_versions:
            logger.info("沒有可回滾的遷移")
            return
            
        # 獲取最後一個遷移
        last_version = max(applied_versions)
        migrations = load_migrations()
        last_migration = next(
            (m for m in migrations if m.version == last_version),
            None
        )
        
        if last_migration:
            manager.rollback_migration(last_migration)
        else:
            logger.error(f"找不到版本 {last_version} 的遷移文件")
            
    except Exception as e:
        logger.error(f"回滾遷移失敗：{str(e)}")
    finally:
        if 'manager' in locals():
            manager.close()

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def status(env):
    """顯示遷移狀態"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建遷移管理器
        manager = MigrationManager(db_config['url'])
        
        # 獲取已應用的遷移
        applied_versions = manager.get_applied_migrations()
        
        # 加載所有遷移
        migrations = load_migrations()
        
        # 顯示狀態
        logger.info("遷移狀態：")
        for migration in migrations:
            status = "已應用" if migration.version in applied_versions else "未應用"
            logger.info(f"- {migration.name} (v{migration.version}): {status}")
            
    except Exception as e:
        logger.error(f"獲取遷移狀態失敗：{str(e)}")
    finally:
        if 'manager' in locals():
            manager.close()

if __name__ == '__main__':
    cli() 