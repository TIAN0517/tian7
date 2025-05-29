import sys
import os
import logging
import datetime
import sqlite3
import json
from pathlib import Path
import click
from typing import Dict, Any, List, Tuple
import time

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.database_config import get_db_config

class DatabaseOptimizer:
    """數據庫優化器"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = sqlite3.connect(db_url.replace('sqlite:///', ''))
        self.cursor = self.conn.cursor()
        
    def analyze_tables(self) -> Dict[str, Any]:
        """分析表結構和索引"""
        try:
            # 獲取所有表
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            
            analysis = {}
            for table in tables:
                table_name = table[0]
                
                # 獲取表信息
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns = self.cursor.fetchall()
                
                # 獲取索引信息
                self.cursor.execute(f"PRAGMA index_list({table_name})")
                indexes = self.cursor.fetchall()
                
                # 獲取表統計信息
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = self.cursor.fetchone()[0]
                
                analysis[table_name] = {
                    'columns': len(columns),
                    'indexes': len(indexes),
                    'row_count': row_count,
                    'column_info': [
                        {
                            'name': col[1],
                            'type': col[2],
                            'not_null': bool(col[3]),
                            'default_value': col[4],
                            'primary_key': bool(col[5])
                        }
                        for col in columns
                    ],
                    'index_info': [
                        {
                            'name': idx[1],
                            'unique': bool(idx[2])
                        }
                        for idx in indexes
                    ]
                }
                
            return analysis
            
        except Exception as e:
            logger.error(f"分析表結構失敗：{str(e)}")
            return {}
            
    def optimize_database(self) -> Dict[str, Any]:
        """優化數據庫"""
        try:
            start_time = time.time()
            results = {}
            
            # 執行VACUUM
            logger.info("執行VACUUM...")
            self.conn.execute("VACUUM")
            results['vacuum'] = True
            
            # 更新統計信息
            logger.info("更新統計信息...")
            self.conn.execute("ANALYZE")
            results['analyze'] = True
            
            # 優化頁面大小
            logger.info("優化頁面大小...")
            self.conn.execute("PRAGMA page_size = 4096")
            results['page_size'] = 4096
            
            # 設置緩存大小
            logger.info("設置緩存大小...")
            self.conn.execute("PRAGMA cache_size = -2000")  # 使用2MB緩存
            results['cache_size'] = 2000
            
            # 啟用外鍵約束
            logger.info("啟用外鍵約束...")
            self.conn.execute("PRAGMA foreign_keys = ON")
            results['foreign_keys'] = True
            
            # 啟用WAL模式
            logger.info("啟用WAL模式...")
            self.conn.execute("PRAGMA journal_mode = WAL")
            results['wal_mode'] = True
            
            # 設置同步模式
            logger.info("設置同步模式...")
            self.conn.execute("PRAGMA synchronous = NORMAL")
            results['synchronous'] = 'NORMAL'
            
            # 設置臨時存儲
            logger.info("設置臨時存儲...")
            self.conn.execute("PRAGMA temp_store = MEMORY")
            results['temp_store'] = 'MEMORY'
            
            # 提交更改
            self.conn.commit()
            
            # 計算優化時間
            results['optimization_time'] = time.time() - start_time
            
            return results
            
        except Exception as e:
            logger.error(f"優化數據庫失敗：{str(e)}")
            return {}
            
    def optimize_indexes(self) -> Dict[str, Any]:
        """優化索引"""
        try:
            results = {}
            
            # 獲取所有表
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                
                # 獲取表的所有列
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns = self.cursor.fetchall()
                
                # 獲取現有索引
                self.cursor.execute(f"PRAGMA index_list({table_name})")
                existing_indexes = self.cursor.fetchall()
                existing_index_names = {idx[1] for idx in existing_indexes}
                
                # 分析需要創建的索引
                for col in columns:
                    col_name = col[1]
                    col_type = col[2]
                    
                    # 檢查是否已有索引
                    index_name = f"idx_{table_name}_{col_name}"
                    if index_name not in existing_index_names:
                        # 檢查列是否適合索引
                        if col_type in ('INTEGER', 'TEXT', 'REAL'):
                            # 檢查列的唯一性
                            self.cursor.execute(f"""
                                SELECT COUNT(DISTINCT {col_name}) * 100.0 / COUNT(*)
                                FROM {table_name}
                            """)
                            uniqueness = self.cursor.fetchone()[0]
                            
                            # 如果唯一性高，創建索引
                            if uniqueness > 10:  # 10%以上的唯一性
                                logger.info(f"為表 {table_name} 的列 {col_name} 創建索引")
                                self.cursor.execute(f"""
                                    CREATE INDEX {index_name}
                                    ON {table_name} ({col_name})
                                """)
                                results[index_name] = {
                                    'table': table_name,
                                    'column': col_name,
                                    'uniqueness': uniqueness
                                }
                                
            # 提交更改
            self.conn.commit()
            return results
            
        except Exception as e:
            logger.error(f"優化索引失敗：{str(e)}")
            return {}
            
    def defragment_database(self) -> Dict[str, Any]:
        """碎片整理"""
        try:
            start_time = time.time()
            results = {}
            
            # 獲取當前數據庫大小
            initial_size = os.path.getsize(self.db_url.replace('sqlite:///', ''))
            
            # 執行VACUUM
            logger.info("執行碎片整理...")
            self.conn.execute("VACUUM")
            
            # 獲取整理後的大小
            final_size = os.path.getsize(self.db_url.replace('sqlite:///', ''))
            
            results['initial_size'] = initial_size
            results['final_size'] = final_size
            results['space_saved'] = initial_size - final_size
            results['defrag_time'] = time.time() - start_time
            
            return results
            
        except Exception as e:
            logger.error(f"碎片整理失敗：{str(e)}")
            return {}
            
    def close(self):
        """關閉數據庫連接"""
        self.conn.close()

@click.group()
def cli():
    """數據庫優化工具"""
    pass

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def analyze(env):
    """分析數據庫結構"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建優化器
        optimizer = DatabaseOptimizer(db_config['url'])
        
        # 分析表結構
        analysis = optimizer.analyze_tables()
        
        # 顯示分析結果
        logger.info("\n數據庫分析結果：")
        for table, info in analysis.items():
            logger.info(f"\n表：{table}")
            logger.info(f"- 列數：{info['columns']}")
            logger.info(f"- 索引數：{info['indexes']}")
            logger.info(f"- 記錄數：{info['row_count']}")
            
            logger.info("\n列信息：")
            for col in info['column_info']:
                logger.info(f"- {col['name']} ({col['type']})")
                if col['primary_key']:
                    logger.info("  * 主鍵")
                if col['not_null']:
                    logger.info("  * 非空")
                    
            logger.info("\n索引信息：")
            for idx in info['index_info']:
                logger.info(f"- {idx['name']}")
                if idx['unique']:
                    logger.info("  * 唯一索引")
                    
    except Exception as e:
        logger.error(f"分析失敗：{str(e)}")
    finally:
        if 'optimizer' in locals():
            optimizer.close()

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def optimize(env):
    """優化數據庫"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建優化器
        optimizer = DatabaseOptimizer(db_config['url'])
        
        # 執行優化
        results = optimizer.optimize_database()
        
        # 顯示優化結果
        logger.info("\n數據庫優化結果：")
        for key, value in results.items():
            if key == 'optimization_time':
                logger.info(f"- 優化時間：{value:.2f}秒")
            else:
                logger.info(f"- {key}: {value}")
                
    except Exception as e:
        logger.error(f"優化失敗：{str(e)}")
    finally:
        if 'optimizer' in locals():
            optimizer.close()

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def optimize_indexes(env):
    """優化索引"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建優化器
        optimizer = DatabaseOptimizer(db_config['url'])
        
        # 執行索引優化
        results = optimizer.optimize_indexes()
        
        # 顯示優化結果
        logger.info("\n索引優化結果：")
        for index, info in results.items():
            logger.info(f"\n索引：{index}")
            logger.info(f"- 表：{info['table']}")
            logger.info(f"- 列：{info['column']}")
            logger.info(f"- 唯一性：{info['uniqueness']:.1f}%")
            
    except Exception as e:
        logger.error(f"索引優化失敗：{str(e)}")
    finally:
        if 'optimizer' in locals():
            optimizer.close()

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def defragment(env):
    """碎片整理"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建優化器
        optimizer = DatabaseOptimizer(db_config['url'])
        
        # 執行碎片整理
        results = optimizer.defragment_database()
        
        # 顯示整理結果
        logger.info("\n碎片整理結果：")
        logger.info(f"- 初始大小：{results['initial_size'] / 1024:.1f} KB")
        logger.info(f"- 最終大小：{results['final_size'] / 1024:.1f} KB")
        logger.info(f"- 節省空間：{results['space_saved'] / 1024:.1f} KB")
        logger.info(f"- 整理時間：{results['defrag_time']:.2f}秒")
        
    except Exception as e:
        logger.error(f"碎片整理失敗：{str(e)}")
    finally:
        if 'optimizer' in locals():
            optimizer.close()

if __name__ == '__main__':
    cli() 