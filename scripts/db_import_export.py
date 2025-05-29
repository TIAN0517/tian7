import sys
import os
import logging
import datetime
import sqlite3
import json
import csv
import pandas as pd
from pathlib import Path
import click
from typing import Dict, Any, List, Union
import shutil

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

class DatabaseImporterExporter:
    """數據庫導入導出工具"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = sqlite3.connect(db_url.replace('sqlite:///', ''))
        self.cursor = self.conn.cursor()
        
    def export_table(self, table_name: str, format: str, output_file: str) -> bool:
        """導出表數據"""
        try:
            # 獲取表數據
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()
            
            # 獲取列名
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            # 根據格式導出
            if format == 'json':
                data = [dict(zip(columns, row)) for row in rows]
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
            elif format == 'csv':
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(columns)
                    writer.writerows(rows)
                    
            elif format == 'excel':
                df = pd.DataFrame(rows, columns=columns)
                df.to_excel(output_file, index=False)
                
            elif format == 'sql':
                # 獲取表結構
                self.cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                create_table_sql = self.cursor.fetchone()[0]
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    # 寫入創建表語句
                    f.write(f"{create_table_sql};\n\n")
                    
                    # 寫入數據
                    for row in rows:
                        values = []
                        for value in row:
                            if value is None:
                                values.append('NULL')
                            elif isinstance(value, (int, float)):
                                values.append(str(value))
                            else:
                                values.append(f"'{str(value)}'")
                        f.write(f"INSERT INTO {table_name} VALUES ({', '.join(values)});\n")
                        
            else:
                raise ValueError(f"不支持的格式：{format}")
                
            logger.info(f"成功導出表 {table_name} 到 {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"導出表 {table_name} 失敗：{str(e)}")
            return False
            
    def import_table(self, table_name: str, format: str, input_file: str) -> bool:
        """導入表數據"""
        try:
            # 根據格式導入
            if format == 'json':
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 獲取列名
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in self.cursor.fetchall()]
                
                # 插入數據
                for row in data:
                    values = [row.get(col) for col in columns]
                    placeholders = ','.join(['?' for _ in columns])
                    self.cursor.execute(
                        f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
                        values
                    )
                    
            elif format == 'csv':
                with open(input_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        columns = list(row.keys())
                        values = list(row.values())
                        placeholders = ','.join(['?' for _ in columns])
                        self.cursor.execute(
                            f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
                            values
                        )
                        
            elif format == 'excel':
                df = pd.read_excel(input_file)
                for _, row in df.iterrows():
                    columns = list(row.index)
                    values = list(row.values)
                    placeholders = ','.join(['?' for _ in columns])
                    self.cursor.execute(
                        f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})",
                        values
                    )
                    
            elif format == 'sql':
                with open(input_file, 'r', encoding='utf-8') as f:
                    sql = f.read()
                    self.cursor.executescript(sql)
                    
            else:
                raise ValueError(f"不支持的格式：{format}")
                
            # 提交更改
            self.conn.commit()
            logger.info(f"成功導入數據到表 {table_name}")
            return True
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"導入數據到表 {table_name} 失敗：{str(e)}")
            return False
            
    def export_database(self, output_dir: str) -> bool:
        """導出整個數據庫"""
        try:
            # 創建輸出目錄
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 獲取所有表
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            
            # 導出每個表
            for table in tables:
                table_name = table[0]
                output_file = output_path / f"{table_name}.json"
                self.export_table(table_name, 'json', str(output_file))
                
            # 導出數據庫結構
            schema_file = output_path / "schema.sql"
            with open(schema_file, 'w', encoding='utf-8') as f:
                for table in tables:
                    table_name = table[0]
                    self.cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                    create_table_sql = self.cursor.fetchone()[0]
                    f.write(f"{create_table_sql};\n\n")
                    
            logger.info(f"成功導出數據庫到 {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"導出數據庫失敗：{str(e)}")
            return False
            
    def import_database(self, input_dir: str) -> bool:
        """導入整個數據庫"""
        try:
            input_path = Path(input_dir)
            
            # 導入數據庫結構
            schema_file = input_path / "schema.sql"
            if schema_file.exists():
                with open(schema_file, 'r', encoding='utf-8') as f:
                    sql = f.read()
                    self.cursor.executescript(sql)
                    
            # 導入每個表的數據
            for json_file in input_path.glob("*.json"):
                if json_file.name != "schema.json":
                    table_name = json_file.stem
                    self.import_table(table_name, 'json', str(json_file))
                    
            logger.info(f"成功導入數據庫從 {input_dir}")
            return True
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"導入數據庫失敗：{str(e)}")
            return False
            
    def backup_database(self, backup_file: str) -> bool:
        """備份數據庫"""
        try:
            # 創建備份
            shutil.copy2(self.db_url.replace('sqlite:///', ''), backup_file)
            logger.info(f"成功備份數據庫到 {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"備份數據庫失敗：{str(e)}")
            return False
            
    def restore_database(self, backup_file: str) -> bool:
        """恢復數據庫"""
        try:
            # 關閉當前連接
            self.conn.close()
            
            # 恢復備份
            shutil.copy2(backup_file, self.db_url.replace('sqlite:///', ''))
            
            # 重新連接
            self.conn = sqlite3.connect(self.db_url.replace('sqlite:///', ''))
            self.cursor = self.conn.cursor()
            
            logger.info(f"成功從 {backup_file} 恢復數據庫")
            return True
            
        except Exception as e:
            logger.error(f"恢復數據庫失敗：{str(e)}")
            return False
            
    def close(self):
        """關閉數據庫連接"""
        self.conn.close()

@click.group()
def cli():
    """數據庫導入導出工具"""
    pass

@cli.command()
@click.argument('table')
@click.argument('format')
@click.argument('output_file')
@click.option('--env', default='development', help='環境 (development/testing/production)')
def export_table(env, table, format, output_file):
    """導出表數據"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建導入導出工具
        tool = DatabaseImporterExporter(db_config['url'])
        
        # 導出表
        tool.export_table(table, format, output_file)
        
    except Exception as e:
        logger.error(f"導出失敗：{str(e)}")
    finally:
        if 'tool' in locals():
            tool.close()

@cli.command()
@click.argument('table')
@click.argument('format')
@click.argument('input_file')
@click.option('--env', default='development', help='環境 (development/testing/production)')
def import_table(env, table, format, input_file):
    """導入表數據"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建導入導出工具
        tool = DatabaseImporterExporter(db_config['url'])
        
        # 導入表
        tool.import_table(table, format, input_file)
        
    except Exception as e:
        logger.error(f"導入失敗：{str(e)}")
    finally:
        if 'tool' in locals():
            tool.close()

@cli.command()
@click.argument('output_dir')
@click.option('--env', default='development', help='環境 (development/testing/production)')
def export_db(env, output_dir):
    """導出整個數據庫"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建導入導出工具
        tool = DatabaseImporterExporter(db_config['url'])
        
        # 導出數據庫
        tool.export_database(output_dir)
        
    except Exception as e:
        logger.error(f"導出失敗：{str(e)}")
    finally:
        if 'tool' in locals():
            tool.close()

@cli.command()
@click.argument('input_dir')
@click.option('--env', default='development', help='環境 (development/testing/production)')
def import_db(env, input_dir):
    """導入整個數據庫"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建導入導出工具
        tool = DatabaseImporterExporter(db_config['url'])
        
        # 導入數據庫
        tool.import_database(input_dir)
        
    except Exception as e:
        logger.error(f"導入失敗：{str(e)}")
    finally:
        if 'tool' in locals():
            tool.close()

@cli.command()
@click.argument('backup_file')
@click.option('--env', default='development', help='環境 (development/testing/production)')
def backup(env, backup_file):
    """備份數據庫"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建導入導出工具
        tool = DatabaseImporterExporter(db_config['url'])
        
        # 備份數據庫
        tool.backup_database(backup_file)
        
    except Exception as e:
        logger.error(f"備份失敗：{str(e)}")
    finally:
        if 'tool' in locals():
            tool.close()

@cli.command()
@click.argument('backup_file')
@click.option('--env', default='development', help='環境 (development/testing/production)')
def restore(env, backup_file):
    """恢復數據庫"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建導入導出工具
        tool = DatabaseImporterExporter(db_config['url'])
        
        # 恢復數據庫
        tool.restore_database(backup_file)
        
    except Exception as e:
        logger.error(f"恢復失敗：{str(e)}")
    finally:
        if 'tool' in locals():
            tool.close()

if __name__ == '__main__':
    cli() 