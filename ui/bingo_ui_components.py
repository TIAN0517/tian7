from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSpinBox, QDoubleSpinBox, QMessageBox)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
import random
import logging

logger = logging.getLogger(__name__)

class BingoCard(QWidget):
    """賓果卡片組件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.numbers = []
        self.marked_positions = set()
        
    def init_ui(self):
        """初始化UI"""
        self.setFixedSize(300, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #4a90e2;
                border-radius: 10px;
            }
        """)
        
        self.layout = QVBoxLayout()
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        self.cells = []
        for i in range(5):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(2)
            row_cells = []
            
            for j in range(5):
                cell = QLabel()
                cell.setFixedSize(50, 50)
                cell.setAlignment(Qt.AlignCenter)
                cell.setStyleSheet("""
                    QLabel {
                        background-color: #f0f0f0;
                        border: 1px solid #ccc;
                        border-radius: 5px;
                        font-size: 16px;
                        font-weight: bold;
                    }
                """)
                row_layout.addWidget(cell)
                row_cells.append(cell)
                
            self.layout.addLayout(row_layout)
            self.cells.append(row_cells)
            
        self.setLayout(self.layout)
        
    def set_numbers(self, numbers):
        """設置卡片數字"""
        try:
            if len(numbers) != 25:
                raise ValueError("卡片必須包含25個數字")
                
            self.numbers = numbers
            for i in range(5):
                for j in range(5):
                    self.cells[i][j].setText(str(numbers[i * 5 + j]))
                    
        except Exception as e:
            logger.error(f"設置卡片數字失敗: {str(e)}")
            
    def mark_number(self, number):
        """標記數字"""
        try:
            if number in self.numbers:
                index = self.numbers.index(number)
                row = index // 5
                col = index % 5
                self.marked_positions.add((row, col))
                self.cells[row][col].setStyleSheet("""
                    QLabel {
                        background-color: #4CAF50;
                        color: white;
                        border: 1px solid #45a049;
                        border-radius: 5px;
                        font-size: 16px;
                        font-weight: bold;
                    }
                """)
                
        except Exception as e:
            logger.error(f"標記數字失敗: {str(e)}")
            
    def reset(self):
        """重置卡片"""
        try:
            self.marked_positions.clear()
            for i in range(5):
                for j in range(5):
                    self.cells[i][j].setStyleSheet("""
                        QLabel {
                            background-color: #f0f0f0;
                            border: 1px solid #ccc;
                            border-radius: 5px;
                            font-size: 16px;
                            font-weight: bold;
                        }
                    """)
                    
        except Exception as e:
            logger.error(f"重置卡片失敗: {str(e)}")
            
class ControlPanel(QWidget):
    """控制面板組件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setFixedHeight(100)
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QSpinBox, QDoubleSpinBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 4px;
                font-size: 14px;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 下注金額
        bet_layout = QVBoxLayout()
        bet_label = QLabel("下注金額:")
        self.bet_amount = QDoubleSpinBox()
        self.bet_amount.setRange(10, 1000)
        self.bet_amount.setValue(100)
        self.bet_amount.setSingleStep(10)
        bet_layout.addWidget(bet_label)
        bet_layout.addWidget(self.bet_amount)
        
        # 卡片數量
        card_layout = QVBoxLayout()
        card_label = QLabel("卡片數量:")
        self.card_count = QSpinBox()
        self.card_count.setRange(1, 4)
        self.card_count.setValue(1)
        card_layout.addWidget(card_label)
        card_layout.addWidget(self.card_count)
        
        # 開始按鈕
        self.start_button = QPushButton("開始遊戲")
        self.start_button.setFixedWidth(120)
        
        # 重置按鈕
        self.reset_button = QPushButton("重置")
        self.reset_button.setFixedWidth(120)
        self.reset_button.setEnabled(False)
        
        layout.addLayout(bet_layout)
        layout.addLayout(card_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(self.reset_button)
        layout.addStretch()
        
        self.setLayout(layout)
        
class BallAnimation(QWidget):
    """球動畫組件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setFixedSize(60, 60)
        self.setStyleSheet("""
            QWidget {
                background-color: #4a90e2;
                border-radius: 30px;
                color: white;
            }
        """)
        
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        
    def animate(self, number, start_pos, end_pos):
        """播放動畫"""
        try:
            self.label.setText(str(number))
            self.animation.setStartValue(start_pos)
            self.animation.setEndValue(end_pos)
            self.animation.setDuration(1000)
            self.animation.start()
            
        except Exception as e:
            logger.error(f"播放球動畫失敗: {str(e)}")
            
class WinAnimation(QWidget):
    """獲勝動畫組件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setFixedSize(200, 200)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(76, 175, 80, 0.9);
                border-radius: 100px;
            }
        """)
        
        self.label = QLabel("BINGO!", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 36px;
                font-weight: bold;
            }
        """)
        
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setEasingCurve(QEasingCurve.OutBounce)
        
    def animate(self, start_rect, end_rect):
        """播放動畫"""
        try:
            self.animation.setStartValue(start_rect)
            self.animation.setEndValue(end_rect)
            self.animation.setDuration(1500)
            self.animation.start()
            
        except Exception as e:
            logger.error(f"播放獲勝動畫失敗: {str(e)}")
            
class MessageDialog(QMessageBox):
    """消息對話框組件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #333333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        
    def show_message(self, title, message, icon=QMessageBox.Information):
        """顯示消息"""
        try:
            self.setWindowTitle(title)
            self.setText(message)
            self.setIcon(icon)
            self.exec_()
            
        except Exception as e:
            logger.error(f"顯示消息失敗: {str(e)}")
            
class LoadingOverlay(QWidget):
    """加載遮罩組件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 0.7);
            }
        """)
        
        self.label = QLabel("加載中...", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
    def showEvent(self, event):
        """顯示事件"""
        try:
            if self.parent():
                self.setGeometry(0, 0, self.parent().width(), self.parent().height())
            super().showEvent(event)
            
        except Exception as e:
            logger.error(f"顯示加載遮罩失敗: {str(e)}")
            
    def hideEvent(self, event):
        """隱藏事件"""
        try:
            super().hideEvent(event)
            
        except Exception as e:
            logger.error(f"隱藏加載遮罩失敗: {str(e)}") 