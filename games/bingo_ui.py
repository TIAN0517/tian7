from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSpinBox, QMessageBox, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from .bingo import BingoGame

class BingoCell(QFrame):
    def __init__(self, number: int, parent=None):
        super().__init__(parent)
        self.number = number
        self.marked = False
        self.setFixedSize(50, 50)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid black;
                border-radius: 5px;
            }
        """)
        
    def set_marked(self, marked: bool):
        self.marked = marked
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 設置字體
        font = QFont("Arial", 14)
        painter.setFont(font)
        
        # 如果被標記，繪製背景
        if self.marked:
            painter.fillRect(self.rect(), QColor(255, 255, 0, 100))
            
        # 繪製數字
        painter.drawText(self.rect(), Qt.AlignCenter, str(self.number))

class BingoUI(QWidget):
    def __init__(self, user_id: int, db_manager, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.game = BingoGame(db_manager)
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """設置UI界面"""
        layout = QVBoxLayout()
        
        # 賓果卡區域
        self.card_frame = QFrame()
        self.card_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        card_layout = QGridLayout()
        self.cells = []
        self.card = self.game.generate_card()
        for i in range(5):
            for j in range(5):
                cell = BingoCell(self.card[i][j])
                card_layout.addWidget(cell, i, j)
                self.cells.append(cell)
        self.card_frame.setLayout(card_layout)
        layout.addWidget(self.card_frame)
        
        # 下注控制區域
        bet_layout = QHBoxLayout()
        
        # 下注金額
        self.bet_amount_spin = QSpinBox()
        self.bet_amount_spin.setRange(1, 10000)
        self.bet_amount_spin.setValue(100)
        bet_layout.addWidget(QLabel("下注金額:"))
        bet_layout.addWidget(self.bet_amount_spin)
        
        layout.addLayout(bet_layout)
        
        # 下注按鈕
        self.bet_button = QPushButton("下注")
        layout.addWidget(self.bet_button)
        
        # 抽號區域
        self.drawn_numbers_label = QLabel("已抽出號碼: ")
        self.drawn_numbers_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.drawn_numbers_label)
        
        # 結果顯示
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)
        
    def connect_signals(self):
        """連接信號"""
        self.bet_button.clicked.connect(self.place_bet)
        self.game.game_result.connect(self.show_result)
        self.game.points_updated.connect(self.update_points_display)
        self.game.number_drawn.connect(self.update_drawn_numbers)
        
    def place_bet(self):
        """下注"""
        bet_amount = self.bet_amount_spin.value()
        
        # 下注
        success, message = self.game.place_bet(
            self.user_id, bet_amount
        )
        
        if not success:
            QMessageBox.warning(self, "下注失敗", message)
            return
            
        # 開始遊戲
        self.bet_button.setEnabled(False)
        self.play_game(bet_amount)
        
    def play_game(self, bet_amount: int):
        """開始遊戲"""
        result = self.game.play(self.user_id, self.card, bet_amount)
        if result:
            self.show_result(result)
            
    def show_result(self, result_data: dict):
        """顯示遊戲結果"""
        self.bet_button.setEnabled(True)
        
        # 更新標記
        for i, cell in enumerate(self.cells):
            row = i // 5
            col = i % 5
            cell.set_marked(result_data["marked"][row][col])
            
        # 顯示結果
        bingo = result_data["bingo"]
        payout = result_data["payout"]
        
        message = "已抽出號碼: " + ", ".join(map(str, result_data["drawn_numbers"])) + "\n"
        if bingo:
            message += f"恭喜賓果！獲得 {payout} 積分"
        else:
            message += "未中獎"
            
        self.result_label.setText(message)
        
    def update_drawn_numbers(self, number: int):
        """更新已抽出號碼顯示"""
        current_text = self.drawn_numbers_label.text()
        if current_text == "已抽出號碼: ":
            self.drawn_numbers_label.setText(current_text + str(number))
        else:
            self.drawn_numbers_label.setText(current_text + ", " + str(number))
            
    def update_points_display(self, points: int):
        """更新積分顯示"""
        # 這裡可以添加更新積分顯示的邏輯
        pass 