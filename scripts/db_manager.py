import sys
import os
import shutil
import logging
import datetime
import schedule
import time
import threading
import psutil
import sqlite3
from pathlib import Path
import click
import json

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

# 備份目錄
BACKUP_DIR = project_root / 'backups'
BACKUP_DIR.mkdir(exist_ok=True)

# 監控日誌目錄
MONITOR_DIR = project_root / 'logs' / 'monitor'
MONITOR_DIR.mkdir(parents=True, exist_ok=True)

def get_db_path():
    """獲取數據庫文件路徑"""
    db_config = get_db_config()
    if 'sqlite' in db_config['url']:
        return Path(db_config['url'].replace('sqlite:///', ''))
    return None

def monitor_database_performance():
    """監控數據庫性能"""
    try:
        db_path = get_db_path()
        if not db_path:
            return

        # 獲取數據庫大小
        db_size = db_path.stat().st_size / (1024 * 1024)  # MB
        
        # 獲取系統資源使用情況
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # 獲取數據庫連接信息
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 獲取數據庫統計信息
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA cache_size")
        cache_size = cursor.fetchone()[0]
        
        # 獲取表信息
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        # 記錄監控信息
        monitor_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'db_size_mb': db_size,
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'page_size': page_size,
            'page_count': page_count,
            'cache_size': cache_size,
            'tables': [table[0] for table in tables]
        }
        
        # 保存監控數據
        monitor_file = MONITOR_DIR / f'monitor_{datetime.datetime.now().strftime("%Y%m%d")}.json'
        with open(monitor_file, 'a') as f:
            f.write(json.dumps(monitor_data) + '\n')
            
        logger.info(f"數據庫性能監控完成：{monitor_data}")
        
    except Exception as e:
        logger.error(f"監控數據庫性能失敗：{str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

def start_performance_monitoring(interval_minutes=5):
    """啟動性能監控"""
    def monitor_loop():
        while True:
            monitor_database_performance()
            time.sleep(interval_minutes * 60)
            
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
    logger.info(f"數據庫性能監控已啟動，間隔：{interval_minutes}分鐘")

@click.group()
def cli():
    """數據庫管理工具"""
    pass

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
@click.option('--interval', default=24, help='備份間隔（小時）')
def schedule_backup(env, interval):
    """設置自動備份"""
    try:
        def backup_job():
            backup(env)
            
        schedule.every(interval).hours.do(backup_job)
        logger.info(f"已設置自動備份，間隔：{interval}小時")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
            
    except Exception as e:
        logger.error(f"設置自動備份失敗：{str(e)}")

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def backup(env):
    """備份數據庫"""
    try:
        os.environ['ENV'] = env
        db_path = get_db_path()
        if not db_path:
            logger.error("只支持SQLite數據庫備份")
            return

        # 創建備份文件名
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = BACKUP_DIR / f'bingo_game_{env}_{timestamp}.db'
        
        # 複製數據庫文件
        shutil.copy2(db_path, backup_file)
        logger.info(f"數據庫備份成功：{backup_file}")
        
        # 清理舊備份
        cleanup_old_backups(env)
        
    except Exception as e:
        logger.error(f"備份失敗：{str(e)}")

def cleanup_old_backups(env, keep_days=7):
    """清理舊備份"""
    try:
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
        backups = BACKUP_DIR.glob(f'bingo_game_{env}_*.db')
        
        for backup in backups:
            backup_date = datetime.datetime.strptime(
                backup.stem.split('_')[-1],
                '%Y%m%d_%H%M%S'
            )
            if backup_date < cutoff_date:
                backup.unlink()
                logger.info(f"已刪除舊備份：{backup.name}")
                
    except Exception as e:
        logger.error(f"清理舊備份失敗：{str(e)}")

@cli.command()
@click.argument('backup_file')
@click.option('--env', default='development', help='環境 (development/testing/production)')
def restore(backup_file, env):
    """從備份恢復數據庫"""
    try:
        os.environ['ENV'] = env
        db_path = get_db_path()
        if not db_path:
            logger.error("只支持SQLite數據庫恢復")
            return

        backup_path = BACKUP_DIR / backup_file
        if not backup_path.exists():
            logger.error(f"備份文件不存在：{backup_file}")
            return

        # 停止數據庫連接
        db_manager = BingoDatabaseManager(get_db_config()['url'])
        db_manager.close()

        # 恢復數據庫文件
        shutil.copy2(backup_path, db_path)
        logger.info(f"數據庫恢復成功：{backup_file}")
        
    except Exception as e:
        logger.error(f"恢復失敗：{str(e)}")

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def list_backups(env):
    """列出所有備份"""
    try:
        backups = sorted(BACKUP_DIR.glob(f'bingo_game_{env}_*.db'))
        if not backups:
            logger.info("沒有找到備份文件")
            return

        logger.info(f"找到 {len(backups)} 個備份：")
        for backup in backups:
            size = backup.stat().st_size / 1024  # KB
            backup_date = datetime.datetime.strptime(
                backup.stem.split('_')[-1],
                '%Y%m%d_%H%M%S'
            )
            logger.info(f"- {backup.name} ({size:.1f} KB, {backup_date})")
            
    except Exception as e:
        logger.error(f"列出備份失敗：{str(e)}")

@cli.command()
@click.argument('user_id')
@click.option('--env', default='development', help='環境 (development/testing/production)')
def user_info(user_id, env):
    """查看用戶信息"""
    try:
        os.environ['ENV'] = env
        db_manager = BingoDatabaseManager(get_db_config()['url'])
        
        # 獲取用戶信息
        user = db_manager.get_user(user_id)
        if not user:
            logger.error(f"用戶不存在：{user_id}")
            return

        # 獲取用戶統計信息
        stats = db_manager.get_user_statistics(user_id)
        
        # 獲取最近的遊戲記錄
        history = db_manager.get_user_game_history(user_id, limit=5)
        
        # 輸出用戶信息
        logger.info(f"用戶信息：{user_id}")
        logger.info(f"餘額：{user.points}")
        logger.info(f"創建時間：{user.created_at}")
        logger.info(f"最後更新：{user.updated_at}")
        
        if stats:
            logger.info("\n統計信息：")
            logger.info(f"總遊戲次數：{stats.total_games}")
            logger.info(f"獲勝次數：{stats.wins}")
            logger.info(f"總投注：{stats.total_bet}")
            logger.info(f"總獎金：{stats.total_win}")
        
        if history:
            logger.info("\n最近遊戲記錄：")
            for game in history:
                logger.info(f"- 遊戲ID：{game.id}")
                logger.info(f"  投注：{game.bet_amount}")
                logger.info(f"  獎金：{game.win_amount}")
                logger.info(f"  時間：{game.created_at}")
        
    except Exception as e:
        logger.error(f"獲取用戶信息失敗：{str(e)}")
    finally:
        db_manager.close()

@cli.command()
@click.argument('user_id')
@click.argument('points', type=float)
@click.option('--env', default='development', help='環境 (development/testing/production)')
def update_points(user_id, points, env):
    """更新用戶點數"""
    try:
        os.environ['ENV'] = env
        db_manager = BingoDatabaseManager(get_db_config()['url'])
        
        # 更新用戶點數
        success = db_manager.update_user_points(user_id, points)
        if success:
            logger.info(f"用戶 {user_id} 點數更新成功：{points}")
        else:
            logger.error(f"用戶 {user_id} 點數更新失敗")
            
    except Exception as e:
        logger.error(f"更新點數失敗：{str(e)}")
    finally:
        db_manager.close()

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def list_users(env):
    """列出所有用戶"""
    try:
        os.environ['ENV'] = env
        db_manager = BingoDatabaseManager(get_db_config()['url'])
        
        # 獲取所有用戶
        users = db_manager.get_all_users()
        if not users:
            logger.info("沒有找到用戶")
            return

        logger.info(f"找到 {len(users)} 個用戶：")
        for user in users:
            logger.info(f"- {user.user_id}: {user.points} 點")
            
    except Exception as e:
        logger.error(f"列出用戶失敗：{str(e)}")
    finally:
        db_manager.close()

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def optimize_database(env):
    """優化數據庫"""
    try:
        os.environ['ENV'] = env
        db_path = get_db_path()
        if not db_path:
            logger.error("只支持SQLite數據庫優化")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 執行VACUUM
        logger.info("開始優化數據庫...")
        cursor.execute("VACUUM")
        
        # 更新統計信息
        cursor.execute("ANALYZE")
        
        # 設置頁面大小
        cursor.execute("PRAGMA page_size = 4096")
        
        # 設置緩存大小
        cursor.execute("PRAGMA cache_size = -2000")  # 使用2MB緩存
        
        # 啟用外鍵約束
        cursor.execute("PRAGMA foreign_keys = ON")
        
        logger.info("數據庫優化完成")
        
    except Exception as e:
        logger.error(f"優化數據庫失敗：{str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def start_monitoring(env):
    """啟動數據庫監控"""
    try:
        os.environ['ENV'] = env
        start_performance_monitoring()
        logger.info("數據庫監控已啟動")
        
        # 保持程序運行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("監控已停止")
    except Exception as e:
        logger.error(f"啟動監控失敗：{str(e)}")

if __name__ == '__main__':
    cli() 