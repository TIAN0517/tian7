"""
遊戲管理器模塊
負責管理所有遊戲的載入、啟動和狀態管理
"""

from typing import Dict, Any, Optional, Type, List
import importlib
import logging
from .game_data import ALL_GAMES_INFO, get_game_by_id

class GameManager:
    """遊戲管理器"""
    
    def __init__(self, config: Optional[Any] = None):
        """
        初始化遊戲管理器
        
        Args:
            config: 配置對象
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.loaded_games: Dict[str, Any] = {}
        self.game_instances: Dict[str, Any] = {}
        
        # 初始化所有遊戲
        self._initialize_games()
    
    def _initialize_games(self) -> None:
        """初始化所有遊戲模塊"""
        self.logger.info("開始初始化遊戲模塊...")
        
        success_count = 0
        for game_info in ALL_GAMES_INFO:
            try:
                self._load_game(game_info)
                success_count += 1
            except Exception as e:
                self.logger.error(f"載入遊戲失敗: {game_info['name']} ({game_info['id']}) - {e}")
        
        self.logger.info(f"遊戲模塊初始化完成，成功載入 {success_count}/{len(ALL_GAMES_INFO)} 款遊戲")
    
    def _load_game(self, game_info: Dict[str, Any]) -> None:
        """
        載入單個遊戲模塊
        
        Args:
            game_info: 遊戲信息字典
        """
        game_id = game_info["id"]
        module_name = f"src.games.{game_info['module_name']}"
        class_name = game_info["class_name"]
        
        try:
            # 動態導入遊戲模塊
            module = importlib.import_module(module_name)
            game_class = getattr(module, class_name)
            
            # 儲存遊戲類
            self.loaded_games[game_id] = {
                "class": game_class,
                "info": game_info,
                "module": module
            }
            
            self.logger.debug(f"成功載入遊戲: {game_info['name']} ({game_id})")
            
        except ImportError as e:
            self.logger.warning(f"遊戲模塊 {module_name} 不存在，將創建佔位符: {e}")
            # 創建佔位符類
            self._create_placeholder_game(game_info)
        except AttributeError as e:
            self.logger.error(f"遊戲類 {class_name} 在模塊 {module_name} 中不存在: {e}")
            raise
    
    def _create_placeholder_game(self, game_info: Dict[str, Any]) -> None:
        """
        為不存在的遊戲創建佔位符類
        
        Args:
            game_info: 遊戲信息字典
        """
        game_id = game_info["id"]
        
        class PlaceholderGame:
            def __init__(self, user_id: str, config: Any = None):
                self.user_id = user_id
                self.game_name = game_info["name"]
                self.game_id = game_id
                self.config = config
                self.logger = logging.getLogger(f"placeholder.{game_id}")
                self.logger.info(f"佔位符遊戲 {self.game_name} 初始化完成 (用戶: {user_id})")
            
            def start_game(self, bet_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
                """啟動遊戲（佔位符實現）"""
                self.logger.info(f"啟動佔位符遊戲 {self.game_name}，下注信息: {bet_info}")
                return {
                    "success": True,
                    "message": f"遊戲 {self.game_name} 正在開發中，敬請期待！",
                    "game_id": self.game_id,
                    "result": "placeholder",
                    "bet_amount": bet_info.get("amount", 0) if bet_info else 0,
                    "win_amount": 0
                }
            
            def get_game_info(self) -> Dict[str, Any]:
                """獲取遊戲信息"""
                return game_info.copy()
        
        # 儲存佔位符遊戲類
        self.loaded_games[game_id] = {
            "class": PlaceholderGame,
            "info": game_info,
            "module": None,
            "placeholder": True
        }
        
        self.logger.info(f"為遊戲 {game_info['name']} ({game_id}) 創建佔位符")
    
    def start_game(self, game_id: str, user_id: str, bet_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        啟動指定遊戲
        
        Args:
            game_id: 遊戲ID
            user_id: 用戶ID
            bet_info: 下注信息
            
        Returns:
            遊戲結果字典
        """
        if game_id not in self.loaded_games:
            error_msg = f"遊戲 {game_id} 未載入"
            self.logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "game_id": game_id
            }
        
        try:
            # 獲取或創建遊戲實例
            game_instance = self._get_or_create_game_instance(game_id, user_id)
            
            # 啟動遊戲
            result = game_instance.start_game(bet_info)
            
            self.logger.info(f"用戶 {user_id} 啟動遊戲 {game_id}，結果: {result.get('success', False)}")
            return result
            
        except Exception as e:
            error_msg = f"啟動遊戲 {game_id} 時發生錯誤: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "game_id": game_id,
                "error": str(e)
            }
    
    def _get_or_create_game_instance(self, game_id: str, user_id: str) -> Any:
        """
        獲取或創建遊戲實例
        
        Args:
            game_id: 遊戲ID
            user_id: 用戶ID
            
        Returns:
            遊戲實例
        """
        instance_key = f"{game_id}_{user_id}"
        
        if instance_key not in self.game_instances:
            game_class = self.loaded_games[game_id]["class"]
            self.game_instances[instance_key] = game_class(user_id, self.config)
        
        return self.game_instances[instance_key]
    
    def get_game_info(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        獲取遊戲信息
        
        Args:
            game_id: 遊戲ID
            
        Returns:
            遊戲信息字典或None
        """
        try:
            return get_game_by_id(game_id)
        except ValueError:
            self.logger.error(f"找不到遊戲ID: {game_id}")
            return None
    
    def get_all_games_info(self) -> List[Dict[str, Any]]:
        """獲取所有遊戲信息"""
        return ALL_GAMES_INFO.copy()
    
    def get_loaded_games(self) -> Dict[str, Any]:
        """獲取已載入的遊戲"""
        return self.loaded_games.copy()
    
    def get_games_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        根據類別獲取遊戲列表
        
        Args:
            category: 遊戲類別
            
        Returns:
            遊戲信息列表
        """
        return [game for game in ALL_GAMES_INFO if game["category"] == category]
    
    def is_game_available(self, game_id: str) -> bool:
        """
        檢查遊戲是否可用
        
        Args:
            game_id: 遊戲ID
            
        Returns:
            遊戲是否可用
        """
        return game_id in self.loaded_games
    
    def get_game_statistics(self) -> Dict[str, Any]:
        """獲取遊戲統計信息"""
        total_games = len(ALL_GAMES_INFO)
        loaded_games = len(self.loaded_games)
        placeholder_games = len([g for g in self.loaded_games.values() if g.get("placeholder", False)])
        
        return {
            "total_games": total_games,
            "loaded_games": loaded_games,
            "placeholder_games": placeholder_games,
            "real_games": loaded_games - placeholder_games,
            "categories": len(set(game["category"] for game in ALL_GAMES_INFO))
        }