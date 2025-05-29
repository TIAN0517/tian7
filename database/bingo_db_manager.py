from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Optional
from datetime import datetime
import json
import logging
import uuid

from .bingo_models import Base, BingoGameRecord, BingoCardRecord, BingoStatistics, User, GameHistory, Transaction

logger = logging.getLogger(__name__)

class BingoDatabaseManager:
    """賓果遊戲數據庫管理器"""
    
    def __init__(self, db_url: str):
        """初始化數據庫管理器"""
        try:
            self.engine = create_engine(db_url)
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            logger.info("數據庫連接成功")
        except SQLAlchemyError as e:
            logger.error(f"數據庫連接失敗: {str(e)}")
            raise
            
    def get_user(self, user_id: str) -> Optional[User]:
        """獲取用戶信息"""
        try:
            return self.session.query(User).filter_by(user_id=user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"獲取用戶信息失敗: {str(e)}")
            return None
            
    def create_user(self, user_id: str, points: float = 1000.0) -> Optional[User]:
        """創建新用戶"""
        try:
            user = User(user_id=user_id, points=points)
            self.session.add(user)
            self.session.commit()
            return user
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"創建用戶失敗: {str(e)}")
            return None
            
    def update_user_points(self, user_id: str, points: float) -> bool:
        """更新用戶積分"""
        try:
            user = self.get_user(user_id)
            if user:
                user.points = points
                self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"更新用戶積分失敗: {str(e)}")
            return False
            
    def record_transaction(self, user_id: str, transaction_data: Dict) -> bool:
        """記錄交易"""
        try:
            transaction = Transaction(
                user_id=user_id,
                type=transaction_data["type"],
                amount=transaction_data["amount"],
                description=transaction_data.get("description", "")
            )
            self.session.add(transaction)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"記錄交易失敗: {str(e)}")
            return False
            
    def record_game_history(self, game_data: Dict) -> bool:
        """記錄遊戲歷史"""
        try:
            history = GameHistory(
                user_id=game_data["user_id"],
                bet_amount=game_data["bet_amount"],
                card_count=game_data["card_count"],
                drawn_balls=game_data["drawn_balls"],
                winning_patterns=game_data["winning_patterns"],
                payout=game_data["payout"],
                duration=game_data["duration"]
            )
            self.session.add(history)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"記錄遊戲歷史失敗: {str(e)}")
            return False
            
    def get_user_transactions(self, user_id: str) -> List[Dict]:
        """獲取用戶交易歷史"""
        try:
            transactions = self.session.query(Transaction)\
                .filter_by(user_id=user_id)\
                .order_by(Transaction.created_at.desc())\
                .all()
            return [t.to_dict() for t in transactions]
        except SQLAlchemyError as e:
            logger.error(f"獲取用戶交易歷史失敗: {str(e)}")
            return []
            
    def get_user_game_history(self, user_id: str) -> List[Dict]:
        """獲取用戶遊戲歷史"""
        try:
            history = self.session.query(GameHistory)\
                .filter_by(user_id=user_id)\
                .order_by(GameHistory.created_at.desc())\
                .all()
            return [h.to_dict() for h in history]
        except SQLAlchemyError as e:
            logger.error(f"獲取用戶遊戲歷史失敗: {str(e)}")
            return []
            
    def get_or_create_statistics(self, user_id: str) -> Optional[BingoStatistics]:
        """獲取或創建用戶統計數據"""
        try:
            stats = self.session.query(BingoStatistics)\
                .filter_by(user_id=user_id)\
                .first()
            if not stats:
                stats = BingoStatistics(user_id=user_id)
                self.session.add(stats)
                self.session.commit()
            return stats
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"獲取統計數據失敗: {str(e)}")
            return None
            
    def record_game(self, game_data: Dict) -> bool:
        """記錄完整遊戲數據"""
        try:
            # 創建遊戲記錄
            game_record = BingoGameRecord(
                user_id=game_data["user_id"],
                session_id=str(uuid.uuid4()),
                card_count=game_data["card_count"],
                bet_amount=game_data["bet_amount"],
                total_payout=game_data.get("total_payout", 0),
                cards_data=game_data["cards_data"],
                drawn_balls=game_data["drawn_balls"],
                winning_patterns=game_data["winning_patterns"],
                game_duration=game_data["game_duration"]
            )
            self.session.add(game_record)
            self.session.flush()
            
            # 記錄每張卡片
            for card_data in game_data["cards_data"]:
                card_record = BingoCardRecord(
                    game_record_id=game_record.id,
                    card_index=card_data["index"],
                    card_numbers=card_data["numbers"],
                    marked_positions=card_data["marked_positions"],
                    winning_lines=card_data["winning_lines"],
                    payout_amount=card_data.get("payout_amount", 0)
                )
                self.session.add(card_record)
            
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"記錄遊戲數據失敗: {str(e)}")
            return False
            
    def get_user_game_records(self, user_id: str) -> List[Dict]:
        """獲取用戶遊戲記錄"""
        try:
            records = self.session.query(BingoGameRecord)\
                .filter_by(user_id=user_id)\
                .order_by(BingoGameRecord.created_at.desc())\
                .all()
            return [r.to_dict() for r in records]
        except SQLAlchemyError as e:
            logger.error(f"獲取用戶遊戲記錄失敗: {str(e)}")
            return []
            
    def get_game_cards(self, game_record_id: int) -> List[Dict]:
        """獲取遊戲卡片記錄"""
        try:
            cards = self.session.query(BingoCardRecord)\
                .filter_by(game_record_id=game_record_id)\
                .order_by(BingoCardRecord.card_index)\
                .all()
            return [c.to_dict() for c in cards]
        except SQLAlchemyError as e:
            logger.error(f"獲取遊戲卡片記錄失敗: {str(e)}")
            return []
            
    def close(self):
        """關閉數據庫連接"""
        try:
            self.session.close()
            self.engine.dispose()
            logger.info("數據庫連接已關閉")
        except SQLAlchemyError as e:
            logger.error(f"關閉數據庫連接失敗: {str(e)}") 