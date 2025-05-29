import sys
import os
import logging
import datetime
import sqlite3
import json
from pathlib import Path
import click
from typing import Dict, Any, List, Union
import psutil
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

class DatabaseDiagnostic:
    """數據庫診斷工具"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = sqlite3.connect(db_url.replace('sqlite:///', ''))
        self.cursor = self.conn.cursor()
        
    def check_database_integrity(self) -> Dict[str, Any]:
        """檢查數據庫完整性"""
        try:
            # 執行完整性檢查
            self.cursor.execute("PRAGMA integrity_check")
            integrity_result = self.cursor.fetchone()[0]
            
            # 檢查外鍵約束
            self.cursor.execute("PRAGMA foreign_key_check")
            foreign_key_issues = self.cursor.fetchall()
            
            # 檢查索引
            self.cursor.execute("PRAGMA index_list")
            indexes = self.cursor.fetchall()
            
            # 檢查表結構
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            
            return {
                'integrity_check': integrity_result,
                'foreign_key_issues': foreign_key_issues,
                'indexes': indexes,
                'tables': tables
            }
            
        except Exception as e:
            logger.error(f"檢查數據庫完整性失敗：{str(e)}")
            return {}
            
    def analyze_database_performance(self) -> Dict[str, Any]:
        """分析數據庫性能"""
        try:
            # 獲取數據庫大小
            db_size = os.path.getsize(self.db_url.replace('sqlite:///', ''))
            
            # 獲取系統資源使用情況
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            # 獲取數據庫統計信息
            self.cursor.execute("PRAGMA page_size")
            page_size = self.cursor.fetchone()[0]
            
            self.cursor.execute("PRAGMA page_count")
            page_count = self.cursor.fetchone()[0]
            
            self.cursor.execute("PRAGMA cache_size")
            cache_size = self.cursor.fetchone()[0]
            
            # 獲取表統計信息
            table_stats = {}
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = self.cursor.fetchone()[0]
                
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                column_count = len(self.cursor.fetchall())
                
                table_stats[table_name] = {
                    'row_count': row_count,
                    'column_count': column_count
                }
                
            return {
                'db_size': db_size,
                'system_stats': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available': memory.available
                },
                'db_stats': {
                    'page_size': page_size,
                    'page_count': page_count,
                    'cache_size': cache_size,
                    'total_size': page_size * page_count
                },
                'table_stats': table_stats
            }
            
        except Exception as e:
            logger.error(f"分析數據庫性能失敗：{str(e)}")
            return {}
            
    def check_database_issues(self) -> List[Dict[str, Any]]:
        """檢查數據庫問題"""
        issues = []
        
        try:
            # 檢查數據庫大小
            db_size = os.path.getsize(self.db_url.replace('sqlite:///', ''))
            if db_size > 100 * 1024 * 1024:  # 100MB
                issues.append({
                    'type': 'warning',
                    'message': f'數據庫大小超過100MB ({db_size / 1024 / 1024:.2f}MB)',
                    'suggestion': '考慮進行數據庫優化或清理'
                })
                
            # 檢查表索引
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                
                # 檢查表是否有主鍵
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns = self.cursor.fetchall()
                has_primary_key = any(col[5] for col in columns)
                
                if not has_primary_key:
                    issues.append({
                        'type': 'warning',
                        'message': f'表 {table_name} 沒有主鍵',
                        'suggestion': '建議添加主鍵以提高查詢性能'
                    })
                    
                # 檢查表是否有索引
                self.cursor.execute(f"PRAGMA index_list({table_name})")
                indexes = self.cursor.fetchall()
                
                if not indexes:
                    issues.append({
                        'type': 'info',
                        'message': f'表 {table_name} 沒有索引',
                        'suggestion': '考慮為常用查詢字段添加索引'
                    })
                    
            # 檢查數據庫配置
            self.cursor.execute("PRAGMA journal_mode")
            journal_mode = self.cursor.fetchone()[0]
            
            if journal_mode != 'WAL':
                issues.append({
                    'type': 'info',
                    'message': '數據庫未使用WAL模式',
                    'suggestion': '考慮啟用WAL模式以提高並發性能'
                })
                
            # 檢查數據庫連接
            self.cursor.execute("PRAGMA busy_timeout")
            busy_timeout = self.cursor.fetchone()[0]
            
            if busy_timeout < 5000:  # 5秒
                issues.append({
                    'type': 'warning',
                    'message': '數據庫忙等待超時設置較短',
                    'suggestion': '建議增加busy_timeout以處理高並發情況'
                })
                
        except Exception as e:
            logger.error(f"檢查數據庫問題失敗：{str(e)}")
            
        return issues
        
    def generate_diagnostic_report(self, output_file: str) -> bool:
        """生成診斷報告"""
        try:
            # 收集診斷信息
            integrity_info = self.check_database_integrity()
            performance_info = self.analyze_database_performance()
            issues = self.check_database_issues()
            
            # 生成報告
            report = {
                'timestamp': datetime.datetime.now().isoformat(),
                'database_url': self.db_url,
                'integrity_check': integrity_info,
                'performance_analysis': performance_info,
                'issues': issues,
                'recommendations': [
                    issue['suggestion'] for issue in issues
                ]
            }
            
            # 保存報告
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
                
            logger.info(f"成功生成診斷報告：{output_file}")
            return True
            
        except Exception as e:
            logger.error(f"生成診斷報告失敗：{str(e)}")
            return False
            
    def close(self):
        """關閉數據庫連接"""
        self.conn.close()

@click.group()
def cli():
    """數據庫診斷工具"""
    pass

@cli.command()
@click.argument('output_file')
@click.option('--env', default='development', help='環境 (development/testing/production)')
def diagnose(env, output_file):
    """生成數據庫診斷報告"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建診斷工具
        tool = DatabaseDiagnostic(db_config['url'])
        
        # 生成報告
        tool.generate_diagnostic_report(output_file)
        
    except Exception as e:
        logger.error(f"診斷失敗：{str(e)}")
    finally:
        if 'tool' in locals():
            tool.close()

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def check_integrity(env):
    """檢查數據庫完整性"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建診斷工具
        tool = DatabaseDiagnostic(db_config['url'])
        
        # 檢查完整性
        integrity_info = tool.check_database_integrity()
        print(json.dumps(integrity_info, ensure_ascii=False, indent=2))
        
    except Exception as e:
        logger.error(f"檢查完整性失敗：{str(e)}")
    finally:
        if 'tool' in locals():
            tool.close()

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def analyze_performance(env):
    """分析數據庫性能"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建診斷工具
        tool = DatabaseDiagnostic(db_config['url'])
        
        # 分析性能
        performance_info = tool.analyze_database_performance()
        print(json.dumps(performance_info, ensure_ascii=False, indent=2))
        
    except Exception as e:
        logger.error(f"分析性能失敗：{str(e)}")
    finally:
        if 'tool' in locals():
            tool.close()

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
def check_issues(env):
    """檢查數據庫問題"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建診斷工具
        tool = DatabaseDiagnostic(db_config['url'])
        
        # 檢查問題
        issues = tool.check_database_issues()
        print(json.dumps(issues, ensure_ascii=False, indent=2))
        
    except Exception as e:
        logger.error(f"檢查問題失敗：{str(e)}")
    finally:
        if 'tool' in locals():
            tool.close()

if __name__ == '__main__':
    cli() 