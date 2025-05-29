from typing import Dict, List, Optional
import logging
from datetime import datetime
from enum import Enum

class TransactionType(Enum):
    """交易类型"""
    BET = "bet"           # 下注
    WIN = "win"           # 赢取
    BONUS = "bonus"       # 奖励
    REFUND = "refund"     # 退款
    ADJUSTMENT = "adjustment"  # 调整

class TransactionManager:
    """交易管理器"""
    
    def __init__(self):
        self.transactions: Dict[str, List[Dict]] = {}
        self.logger = logging.getLogger(__name__)
        
    def add_transaction(self, user_id: str, amount: float, 
                       transaction_type: TransactionType,
                       description: str = "") -> Dict:
        """添加交易记录"""
        try:
            if user_id not in self.transactions:
                self.transactions[user_id] = []
                
            transaction = {
                "id": len(self.transactions[user_id]) + 1,
                "amount": amount,
                "type": transaction_type.value,
                "description": description,
                "timestamp": datetime.now()
            }
            
            self.transactions[user_id].append(transaction)
            return transaction
            
        except Exception as e:
            self.logger.error(f"添加交易记录失败: {str(e)}")
            raise
            
    def get_transactions(self, user_id: str, 
                        transaction_type: Optional[TransactionType] = None,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None) -> List[Dict]:
        """获取交易记录"""
        try:
            if user_id not in self.transactions:
                return []
                
            transactions = self.transactions[user_id]
            
            # 按类型过滤
            if transaction_type:
                transactions = [t for t in transactions 
                              if t["type"] == transaction_type.value]
                
            # 按时间范围过滤
            if start_time:
                transactions = [t for t in transactions 
                              if t["timestamp"] >= start_time]
            if end_time:
                transactions = [t for t in transactions 
                              if t["timestamp"] <= end_time]
                
            return transactions
            
        except Exception as e:
            self.logger.error(f"获取交易记录失败: {str(e)}")
            raise
            
    def get_balance(self, user_id: str) -> float:
        """获取用户余额"""
        try:
            if user_id not in self.transactions:
                return 0.0
                
            balance = 0.0
            for transaction in self.transactions[user_id]:
                if transaction["type"] in [TransactionType.WIN.value, 
                                         TransactionType.BONUS.value,
                                         TransactionType.REFUND.value]:
                    balance += transaction["amount"]
                elif transaction["type"] in [TransactionType.BET.value,
                                           TransactionType.ADJUSTMENT.value]:
                    balance -= transaction["amount"]
                    
            return balance
            
        except Exception as e:
            self.logger.error(f"获取用户余额失败: {str(e)}")
            raise
            
    def get_statistics(self, user_id: str) -> Dict:
        """获取交易统计信息"""
        try:
            if user_id not in self.transactions:
                return {
                    "total_bets": 0,
                    "total_wins": 0,
                    "total_bonus": 0,
                    "net_profit": 0
                }
                
            stats = {
                "total_bets": 0,
                "total_wins": 0,
                "total_bonus": 0,
                "net_profit": 0
            }
            
            for transaction in self.transactions[user_id]:
                if transaction["type"] == TransactionType.BET.value:
                    stats["total_bets"] += transaction["amount"]
                elif transaction["type"] == TransactionType.WIN.value:
                    stats["total_wins"] += transaction["amount"]
                elif transaction["type"] == TransactionType.BONUS.value:
                    stats["total_bonus"] += transaction["amount"]
                    
            stats["net_profit"] = (stats["total_wins"] + stats["total_bonus"] - 
                                 stats["total_bets"])
                                 
            return stats
            
        except Exception as e:
            self.logger.error(f"获取交易统计信息失败: {str(e)}")
            raise 