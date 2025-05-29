import sys
import os
import logging
import datetime
import time
import threading
import psutil
import sqlite3
import json
from pathlib import Path
import click
from typing import Dict, Any, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

# 監控日誌目錄
MONITOR_DIR = project_root / 'logs' / 'monitor'
MONITOR_DIR.mkdir(parents=True, exist_ok=True)

class DatabaseMonitor:
    """數據庫監控器"""
    
    def __init__(self, db_url: str, alert_thresholds: Dict[str, float] = None):
        self.db_url = db_url
        self.alert_thresholds = alert_thresholds or {
            'cpu_percent': 80.0,
            'memory_percent': 80.0,
            'disk_percent': 80.0,
            'db_size_mb': 1000.0,
            'query_time_ms': 1000.0
        }
        self.alerts: List[Dict[str, Any]] = []
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self, interval_seconds: int = 60):
        """開始監控"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info(f"數據庫監控已啟動，間隔：{interval_seconds}秒")
        
    def stop_monitoring(self):
        """停止監控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("數據庫監控已停止")
        
    def _monitor_loop(self, interval_seconds: int):
        """監控循環"""
        while self.monitoring:
            try:
                metrics = self.collect_metrics()
                self.check_alerts(metrics)
                self.save_metrics(metrics)
                time.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"監控循環錯誤：{str(e)}")
                
    def collect_metrics(self) -> Dict[str, Any]:
        """收集性能指標"""
        metrics = {
            'timestamp': datetime.datetime.now().isoformat(),
            'system': self._collect_system_metrics(),
            'database': self._collect_database_metrics()
        }
        return metrics
        
    def _collect_system_metrics(self) -> Dict[str, float]:
        """收集系統指標"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }
        
    def _collect_database_metrics(self) -> Dict[str, Any]:
        """收集數據庫指標"""
        try:
            conn = sqlite3.connect(self.db_url.replace('sqlite:///', ''))
            cursor = conn.cursor()
            
            # 獲取數據庫大小
            db_size = os.path.getsize(self.db_url.replace('sqlite:///', '')) / (1024 * 1024)
            
            # 獲取表信息
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # 獲取每個表的記錄數
            table_stats = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                table_stats[table_name] = count
                
            # 獲取數據庫配置
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA cache_size")
            cache_size = cursor.fetchone()[0]
            
            return {
                'size_mb': db_size,
                'tables': table_stats,
                'page_size': page_size,
                'page_count': page_count,
                'cache_size': cache_size
            }
            
        except Exception as e:
            logger.error(f"收集數據庫指標失敗：{str(e)}")
            return {}
        finally:
            if 'conn' in locals():
                conn.close()
                
    def check_alerts(self, metrics: Dict[str, Any]):
        """檢查警報"""
        system = metrics['system']
        database = metrics['database']
        
        # 檢查系統指標
        for metric, value in system.items():
            threshold = self.alert_thresholds.get(metric)
            if threshold and value > threshold:
                self._create_alert(metric, value, threshold)
                
        # 檢查數據庫指標
        if database:
            db_size = database.get('size_mb', 0)
            threshold = self.alert_thresholds.get('db_size_mb')
            if threshold and db_size > threshold:
                self._create_alert('db_size_mb', db_size, threshold)
                
    def _create_alert(self, metric: str, value: float, threshold: float):
        """創建警報"""
        alert = {
            'timestamp': datetime.datetime.now().isoformat(),
            'metric': metric,
            'value': value,
            'threshold': threshold
        }
        self.alerts.append(alert)
        logger.warning(f"警報：{metric} = {value} (閾值：{threshold})")
        
    def save_metrics(self, metrics: Dict[str, Any]):
        """保存指標"""
        try:
            # 保存到文件
            date_str = datetime.datetime.now().strftime('%Y%m%d')
            metrics_file = MONITOR_DIR / f'metrics_{date_str}.json'
            
            with open(metrics_file, 'a') as f:
                f.write(json.dumps(metrics) + '\n')
                
            # 保存警報
            if self.alerts:
                alerts_file = MONITOR_DIR / f'alerts_{date_str}.json'
                with open(alerts_file, 'a') as f:
                    for alert in self.alerts:
                        f.write(json.dumps(alert) + '\n')
                self.alerts.clear()
                
        except Exception as e:
            logger.error(f"保存指標失敗：{str(e)}")
            
    def send_alert_email(self, smtp_config: Dict[str, str]):
        """發送警報郵件"""
        if not self.alerts:
            return
            
        try:
            # 創建郵件
            msg = MIMEMultipart()
            msg['From'] = smtp_config['from']
            msg['To'] = smtp_config['to']
            msg['Subject'] = "數據庫監控警報"
            
            # 創建郵件內容
            body = "數據庫監控警報：\n\n"
            for alert in self.alerts:
                body += f"- {alert['metric']}: {alert['value']} (閾值：{alert['threshold']})\n"
                
            msg.attach(MIMEText(body, 'plain'))
            
            # 發送郵件
            with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
                server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                server.send_message(msg)
                
            logger.info("警報郵件已發送")
            
        except Exception as e:
            logger.error(f"發送警報郵件失敗：{str(e)}")

@click.group()
def cli():
    """數據庫監控工具"""
    pass

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
@click.option('--interval', default=60, help='監控間隔（秒）')
def start(env, interval):
    """啟動監控"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 創建監控器
        monitor = DatabaseMonitor(db_config['url'])
        
        # 啟動監控
        monitor.start_monitoring(interval)
        
        # 保持程序運行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
            
    except Exception as e:
        logger.error(f"啟動監控失敗：{str(e)}")

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
@click.option('--days', default=7, help='保留天數')
def cleanup(env, days):
    """清理舊的監控數據"""
    try:
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        # 清理指標文件
        for file in MONITOR_DIR.glob('metrics_*.json'):
            try:
                file_date = datetime.datetime.strptime(
                    file.stem.split('_')[1],
                    '%Y%m%d'
                )
                if file_date < cutoff_date:
                    file.unlink()
                    logger.info(f"已刪除舊指標文件：{file.name}")
            except ValueError:
                continue
                
        # 清理警報文件
        for file in MONITOR_DIR.glob('alerts_*.json'):
            try:
                file_date = datetime.datetime.strptime(
                    file.stem.split('_')[1],
                    '%Y%m%d'
                )
                if file_date < cutoff_date:
                    file.unlink()
                    logger.info(f"已刪除舊警報文件：{file.name}")
            except ValueError:
                continue
                
        logger.info("清理完成")
        
    except Exception as e:
        logger.error(f"清理失敗：{str(e)}")

@cli.command()
@click.option('--env', default='development', help='環境 (development/testing/production)')
@click.option('--days', default=1, help='查看天數')
def report(env, days):
    """生成監控報告"""
    try:
        os.environ['ENV'] = env
        db_config = get_db_config()
        
        # 獲取日期範圍
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=days)
        
        # 收集指標
        metrics = []
        for file in MONITOR_DIR.glob('metrics_*.json'):
            try:
                file_date = datetime.datetime.strptime(
                    file.stem.split('_')[1],
                    '%Y%m%d'
                )
                if start_date <= file_date <= end_date:
                    with open(file) as f:
                        for line in f:
                            metrics.append(json.loads(line))
            except ValueError:
                continue
                
        # 收集警報
        alerts = []
        for file in MONITOR_DIR.glob('alerts_*.json'):
            try:
                file_date = datetime.datetime.strptime(
                    file.stem.split('_')[1],
                    '%Y%m%d'
                )
                if start_date <= file_date <= end_date:
                    with open(file) as f:
                        for line in f:
                            alerts.append(json.loads(line))
            except ValueError:
                continue
                
        # 生成報告
        logger.info(f"\n監控報告 ({start_date.date()} 到 {end_date.date()})")
        
        if metrics:
            # 計算平均值
            cpu_avg = sum(m['system']['cpu_percent'] for m in metrics) / len(metrics)
            memory_avg = sum(m['system']['memory_percent'] for m in metrics) / len(metrics)
            disk_avg = sum(m['system']['disk_percent'] for m in metrics) / len(metrics)
            
            logger.info("\n系統指標平均值：")
            logger.info(f"- CPU使用率：{cpu_avg:.1f}%")
            logger.info(f"- 內存使用率：{memory_avg:.1f}%")
            logger.info(f"- 磁盤使用率：{disk_avg:.1f}%")
            
            # 數據庫指標
            if metrics[0]['database']:
                db_size = metrics[-1]['database']['size_mb']
                logger.info(f"\n數據庫大小：{db_size:.1f} MB")
                
                logger.info("\n表記錄數：")
                for table, count in metrics[-1]['database']['tables'].items():
                    logger.info(f"- {table}: {count}")
                    
        if alerts:
            logger.info(f"\n警報數量：{len(alerts)}")
            logger.info("\n最近警報：")
            for alert in alerts[-5:]:
                logger.info(f"- {alert['metric']}: {alert['value']} (閾值：{alert['threshold']})")
                
    except Exception as e:
        logger.error(f"生成報告失敗：{str(e)}")

if __name__ == '__main__':
    cli() 