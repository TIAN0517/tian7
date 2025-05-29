import os
import sys
import json
import hashlib
import requests
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from .config import config
from .logger import get_logger
from .models import GameVersion, get_session

logger = get_logger(__name__)

class Updater:
    """更新器類"""
    
    def __init__(self):
        self.current_version = config['APP_VERSION']
        self.update_server = config['UPDATE_SERVER']
        self.updater_path = Path(config['UPDATER_PATH'])
        self.temp_dir = Path(tempfile.gettempdir()) / 'nl_online_updates'
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
    def _calculate_file_hash(self, file_path: Path) -> str:
        """計算文件的 SHA-256 哈希值
        
        Args:
            file_path: 文件路徑
            
        Returns:
            str: 文件的 SHA-256 哈希值
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
        
    def _download_file(self, url: str, save_path: Path) -> bool:
        """下載文件
        
        Args:
            url: 下載地址
            save_path: 保存路徑
            
        Returns:
            bool: 是否下載成功
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            return True
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
            
    def check_for_updates(self) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """檢查更新
        
        Returns:
            Tuple[bool, Optional[Dict[str, Any]]]: (是否有更新, 更新信息)
        """
        try:
            response = requests.get(
                f"{self.update_server}/api/v1/updates/check",
                params={"current_version": self.current_version}
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("has_update"):
                return True, data.get("update_info")
            return False, None
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            return False, None
            
    def download_update(self, version: str, download_url: str) -> Optional[Path]:
        """下載更新文件
        
        Args:
            version: 版本號
            download_url: 下載地址
            
        Returns:
            Optional[Path]: 下載文件的臨時路徑，如果下載失敗則返回 None
        """
        temp_file = self.temp_dir / f"update_{version}.zip"
        
        if self._download_file(download_url, temp_file):
            return temp_file
        return None
        
    def verify_update(self, file_path: Path, expected_hash: str) -> bool:
        """驗證更新文件
        
        Args:
            file_path: 更新文件路徑
            expected_hash: 預期的文件哈希值
            
        Returns:
            bool: 文件是否有效
        """
        actual_hash = self._calculate_file_hash(file_path)
        return actual_hash == expected_hash
        
    def install_update(self, update_file: Path) -> bool:
        """安裝更新
        
        Args:
            update_file: 更新文件路徑
            
        Returns:
            bool: 是否安裝成功
        """
        try:
            # 啟動更新器進程
            process = subprocess.Popen(
                [str(self.updater_path), str(update_file)],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # 等待更新完成
            process.wait()
            
            if process.returncode == 0:
                logger.info("Update installed successfully")
                return True
            else:
                logger.error(f"Update installation failed with code: {process.returncode}")
                return False
        except Exception as e:
            logger.error(f"Update installation failed: {e}")
            return False
            
    def record_update(self, version: str, file_hash: str, download_url: str) -> bool:
        """記錄更新信息到數據庫
        
        Args:
            version: 版本號
            file_hash: 文件哈希值
            download_url: 下載地址
            
        Returns:
            bool: 是否記錄成功
        """
        session = get_session()
        try:
            game_version = GameVersion(
                version=version,
                download_url=download_url,
                file_hash=file_hash,
                is_active=True,
                release_notes=""
            )
            
            session.add(game_version)
            session.commit()
            
            logger.info(f"Update recorded: {version}")
            return True
        except Exception as e:
            logger.error(f"Failed to record update: {e}")
            session.rollback()
            return False
        finally:
            session.close()
            
    def cleanup(self):
        """清理臨時文件"""
        try:
            for file in self.temp_dir.glob("*"):
                file.unlink()
            self.temp_dir.rmdir()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            
    def run_update_check(self) -> Tuple[bool, Optional[str]]:
        """運行更新檢查
        
        Returns:
            Tuple[bool, Optional[str]]: (是否更新成功, 錯誤信息)
        """
        try:
            # 檢查更新
            has_update, update_info = self.check_for_updates()
            if not has_update or not update_info:
                return True, None
                
            # 下載更新
            update_file = self.download_update(
                update_info['version'],
                update_info['download_url']
            )
            if not update_file:
                return False, "Failed to download update"
                
            # 驗證更新
            if not self.verify_update(update_file, update_info['file_hash']):
                return False, "Update file verification failed"
                
            # 安裝更新
            if not self.install_update(update_file):
                return False, "Update installation failed"
                
            # 記錄更新
            if not self.record_update(
                update_info['version'],
                update_info['file_hash'],
                update_info['download_url']
            ):
                return False, "Failed to record update"
                
            # 清理
            self.cleanup()
            
            return True, None
        except Exception as e:
            logger.error(f"Update process failed: {e}")
            return False, str(e)
            
    @staticmethod
    def is_updater_running() -> bool:
        """檢查更新器是否正在運行
        
        Returns:
            bool: 更新器是否正在運行
        """
        try:
            if sys.platform == 'win32':
                import psutil
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] == 'updater.exe':
                        return True
            return False
        except Exception as e:
            logger.error(f"Failed to check updater status: {e}")
            return False 