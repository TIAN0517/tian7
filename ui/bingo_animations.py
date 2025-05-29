from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint, QObject
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from typing import List, Dict, Optional
import logging
from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserInfo(Base):
    __tablename__ = 'UserInfo'
    UserNum = Column(Integer, primary_key=True)
    UserName = Column(String)
    UserID = Column(String)
    UserPass = Column(String)
    UserPass_N = Column(String)
    UserPass2 = Column(String)
    UserPass2_N = Column(String)
    UserType = Column(Integer)
    UserLoginState = Column(Integer)
    UserAvailable = Column(Integer)
    CreateDate = Column(DateTime)
    LastLoginDate = Column(DateTime)
    SGNum = Column(Integer)
    SvrNum = Column(Integer)
    ChaName = Column(String)
    UserBlock = Column(Integer)
    UserBlockDate = Column(DateTime)
    ChaRemain = Column(Integer)
    ChaTestRemain = Column(Integer)
    PremiumDate = Column(DateTime)
    ChatBlockDate = Column(DateTime)
    UserEmail = Column(String)
    UserPoint = Column(Integer)
    WebLoginState = Column(String)
    UserAge = Column(Integer)
    OfflineTime = Column(BigInteger)
    GameTime = Column(BigInteger)
    UserIP = Column(String)
    UserLastLoginDate = Column(DateTime)
    PlayTime = Column(BigInteger)
    Donated = Column(Integer)
    UserSA = Column(String)
    UserFullName = Column(String)
    UserFlagVerified = Column(BigInteger)
    UserFlagRestricted = Column(BigInteger)
    UserPCIDHWID = Column(String)
    UserPCIDMAC = Column(String)
    UserPCID = Column(String)
    LastPCIDHWID = Column(String)
    LastPCIDMAC = Column(String)
    LastIP = Column(String)
    UserLoginDeviceCheck = Column(Integer)
    ReferralUserNum = Column(BigInteger)
    ReferralCount = Column(BigInteger)
    Referral = Column(String)
    UserVIP = Column(BigInteger)
    ExchangeItemPoints = Column(BigInteger)
    VotePoint = Column(Integer)

class BallDrawAnimation:
    """抽球動畫"""
    
    def __init__(self, parent: QWidget, ball_number: int):
        self.parent = parent
        self.ball_number = ball_number
        self.ball_label = QLabel(str(ball_number), parent)
        self.ball_label.setStyleSheet("""
            QLabel {
                background-color: #e74c3c;
                color: white;
                border-radius: 25px;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        self.ball_label.setFixedSize(50, 50)
        self.ball_label.setAlignment(Qt.AlignCenter) # type: ignore
        
        # 初始位置 (右上角)
        self.ball_label.move(600, 50)
        
        # 動畫
        self.animation = QPropertyAnimation(self.ball_label, b"geometry")
        self.animation.setDuration(800)  # 0.8秒
        self.animation.setStartValue(QRect(600, 50, 50, 50))
        self.animation.setEndValue(QRect(300, 150, 50, 50))
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        
    def start(self):
        """開始動畫"""
        self.animation.start()
        
    def stop(self):
        """停止動畫"""
        self.animation.stop()
        self.ball_label.deleteLater()

class CardMarkAnimation:
    """卡片標記動畫"""
    
    def __init__(self, cell_widget):
        self.cell_widget = cell_widget
        self.animation = QPropertyAnimation(self.cell_widget, b"geometry")
        self.animation.setDuration(200)  # 0.2秒
        
        # 保存原始大小
        self.original_geometry = self.cell_widget.geometry()
        
    def start(self):
        """開始動畫"""
        # 縮小
        self.animation.setStartValue(self.original_geometry)
        self.animation.setEndValue(self.original_geometry.adjusted(5, 5, -5, -5))
        self.animation.setEasingCurve(QEasingCurve.OutBack)
        self.animation.start()
        
    def stop(self):
        """停止動畫"""
        self.animation.stop()
        self.cell_widget.setGeometry(self.original_geometry)

class WinningCelebrationAnimation:
    """中獎慶祝動畫"""
    
    def __init__(self, card_widget):
        self.card_widget = card_widget
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self.toggle_flash)
        self.is_flashing = False
        self.flash_count = 0
        self.max_flashes = 5
        
    def start(self):
        """開始動畫"""
        self.flash_timer.start(200)  # 每0.2秒閃爍一次
        
    def toggle_flash(self):
        """切換閃爍狀態"""
        self.is_flashing = not self.is_flashing
        self.flash_count += 1
        
        if self.is_flashing:
            self.card_widget.setStyleSheet("""
                QWidget {
                    background-color: #f1c40f;
                    border: 2px solid #f39c12;
                    border-radius: 10px;
                }
            """)
        else:
            self.card_widget.setStyleSheet("")
            
        if self.flash_count >= self.max_flashes * 2:  # 來回閃爍
            self.stop()
            
    def stop(self):
        """停止動畫"""
        self.flash_timer.stop()
        self.card_widget.setStyleSheet("")

class PointsUpdateAnimation:
    """積分更新動畫"""
    
    def __init__(self, points_label: QLabel, old_points: int, new_points: int):
        self.points_label = points_label
        self.old_points = old_points
        self.new_points = new_points
        self.current_points = old_points
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_points)
        self.step = (new_points - old_points) / 20  # 分20步完成
        
    def start(self):
        """開始動畫"""
        self.animation_timer.start(50)  # 每0.05秒更新一次
        
    def update_points(self):
        """更新積分顯示"""
        self.current_points += self.step
        if (self.step > 0 and self.current_points >= self.new_points) or \
           (self.step < 0 and self.current_points <= self.new_points):
            self.current_points = self.new_points
            self.stop()
            
        self.points_label.setText(f"當前積分: {int(self.current_points)}")
        
    def stop(self):
        """停止動畫"""
        self.animation_timer.stop()
        self.points_label.setText(f"當前積分: {self.new_points}")

class BingoAnimationManager(QObject):
    """賓果遊戲動畫管理器"""
    
    def __init__(self, parent: QWidget):
        """初始化動畫管理器"""
        super().__init__()
        self.parent = parent
        self.animations: List[QPropertyAnimation] = []
        self.balls: List[QLabel] = []
        self.win_animations: List[QPropertyAnimation] = []
        self.is_animating = False
        self.logger = logging.getLogger(__name__)
        
    def create_ball(self, number: int) -> QLabel:
        """創建球"""
        try:
            ball = QLabel(str(number), self.parent)
            ball.setFixedSize(60, 60)
            ball.setAlignment(Qt.AlignCenter) # type: ignore
            ball.setStyleSheet("""
                QLabel {
                    background-color: #4a90e2;
                    color: white;
                    border-radius: 30px;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)
            ball.hide()
            self.balls.append(ball)
            return ball
            
        except Exception as e:
            self.logger.error(f"創建球失敗: {str(e)}")
            return None
            
    def animate_ball(self, ball: QLabel, start_pos: QPoint, end_pos: QPoint,
                    duration: int = 1000) -> QPropertyAnimation:
        """播放球動畫"""
        try:
            ball.show()
            ball.move(start_pos)
            
            animation = QPropertyAnimation(ball, b"pos")
            animation.setStartValue(start_pos)
            animation.setEndValue(end_pos)
            animation.setDuration(duration)
            animation.setEasingCurve(QEasingCurve.OutBounce)
            
            self.animations.append(animation)
            animation.start()
            
            return animation
            
        except Exception as e:
            self.logger.error(f"播放球動畫失敗: {str(e)}")
            return None
            
    def animate_win(self, card: QWidget, pattern: str) -> QPropertyAnimation:
        """播放獲勝動畫"""
        try:
            win_label = QLabel("BINGO!", card)
            win_label.setAlignment(Qt.AlignCenter) # type: ignore
            win_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(76, 175, 80, 0.9);
                    color: white;
                    border-radius: 100px;
                    font-size: 36px;
                    font-weight: bold;
                }
            """)
            
            start_rect = QRect(0, 0, 0, 0)
            end_rect = QRect(0, 0, 200, 200)
            end_rect.moveCenter(card.rect().center())
            
            animation = QPropertyAnimation(win_label, b"geometry")
            animation.setStartValue(start_rect)
            animation.setEndValue(end_rect)
            animation.setDuration(1500)
            animation.setEasingCurve(QEasingCurve.OutBounce)
            
            self.win_animations.append(animation)
            animation.start()
            
            return animation
            
        except Exception as e:
            self.logger.error(f"播放獲勝動畫失敗: {str(e)}")
            return None
            
    def animate_card_highlight(self, card: QWidget, positions: List[tuple],
                             duration: int = 500) -> QPropertyAnimation:
        """播放卡片高亮動畫"""
        try:
            highlight = QWidget(card)
            highlight.setStyleSheet("""
                QWidget {
                    background-color: rgba(76, 175, 80, 0.3);
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                }
            """)
            
            # 計算高亮區域
            min_row = min(pos[0] for pos in positions)
            max_row = max(pos[0] for pos in positions)
            min_col = min(pos[1] for pos in positions)
            max_col = max(pos[1] for pos in positions)
            
            start_rect = QRect(0, 0, 0, 0)
            end_rect = QRect(
                min_col * 50, min_row * 50,
                (max_col - min_col + 1) * 50,
                (max_row - min_row + 1) * 50
            )
            
            animation = QPropertyAnimation(highlight, b"geometry")
            animation.setStartValue(start_rect)
            animation.setEndValue(end_rect)
            animation.setDuration(duration)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            
            self.animations.append(animation)
            animation.start()
            
            return animation
            
        except Exception as e:
            self.logger.error(f"播放卡片高亮動畫失敗: {str(e)}")
            return None
            
    def animate_points_change(self, label: QLabel, old_value: int, new_value: int,
                            duration: int = 1000) -> QPropertyAnimation:
        """播放點數變化動畫"""
        try:
            animation = QPropertyAnimation(label, b"text")
            animation.setStartValue(str(old_value))
            animation.setEndValue(str(new_value))
            animation.setDuration(duration)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            
            self.animations.append(animation)
            animation.start()
            
            return animation
            
        except Exception as e:
            self.logger.error(f"播放點數變化動畫失敗: {str(e)}")
            return None
            
    def stop_all(self):
        """停止所有動畫"""
        try:
            self.is_animating = False
            
            # 停止所有動畫
            for animation in self.animations:
                animation.stop()
            self.animations.clear()
            
            for animation in self.win_animations:
                animation.stop()
            self.win_animations.clear()
            
            # 清理所有球
            for ball in self.balls:
                ball.deleteLater()
            self.balls.clear()
            
        except Exception as e:
            self.logger.error(f"停止所有動畫失敗: {str(e)}")
            
    def cleanup(self):
        """清理資源"""
        try:
            self.stop_all()
            
            # 確保所有資源都被清理
            QTimer.singleShot(0, self._final_cleanup)
            
        except Exception as e:
            self.logger.error(f"清理資源失敗: {str(e)}")
            
    def _final_cleanup(self):
        """最終清理"""
        try:
            # 再次檢查並清理所有資源
            for ball in self.balls:
                if ball:
                    ball.deleteLater()
            self.balls.clear()
            
            self.animations.clear()
            self.win_animations.clear()
            
        except Exception as e:
            self.logger.error(f"最終清理失敗: {str(e)}")
            
    def is_running(self) -> bool:
        """檢查是否有動畫正在運行"""
        try:
            return any(animation.state() == QPropertyAnimation.Running
                      for animation in self.animations + self.win_animations)
                      
        except Exception as e:
            self.logger.error(f"檢查動畫狀態失敗: {str(e)}")
            return False

class BingoAnimation(QWidget):
    """宾果动画基类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents) # type: ignore
        self.setAttribute(Qt.WA_TranslucentBackground) # type: ignore
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        
    def start_animation(self, start_pos: QPoint, end_pos: QPoint, duration: int = 1000):
        """开始动画"""
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.setDuration(duration)
        self.animation.start()
        
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.draw_animation(painter)
        
    def draw_animation(self, painter: QPainter):
        """绘制动画（由子类实现）"""
        pass

class NumberAnimation(BingoAnimation):
    """数字动画"""
    
    def __init__(self, number: int, parent=None):
        super().__init__(parent)
        self.number = number
        self.setFixedSize(50, 50)
        
    def draw_animation(self, painter: QPainter):
        """绘制数字"""
        # 绘制圆形背景
        painter.setPen(QPen(QColor(52, 152, 219), 2))
        painter.setBrush(QColor(52, 152, 219, 180))
        painter.drawEllipse(0, 0, 50, 50)
        
        # 绘制数字
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, str(self.number)) # type: ignore

class WinAnimation(BingoAnimation):
    """胜利动画"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 100)
        
    def draw_animation(self, painter: QPainter):
        """绘制胜利文字"""
        # 绘制文字背景
        painter.setPen(QPen(QColor(46, 204, 113), 3))
        painter.setBrush(QColor(46, 204, 113, 180))
        painter.drawRoundedRect(0, 0, 200, 100, 10, 10)
        
        # 绘制文字
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 36, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, "BINGO!")  # type: ignore