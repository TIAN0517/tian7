from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSpinBox, QComboBox, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from .baccarat import BaccaratGame

class CardFrame(QFrame):
    def __init__(self, card_text: str = "", parent=None):
        super().__init__(parent)
        self.card_text = card_text
        self.setFixedSize(60, 90)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid black;
                border-radius: 5px;
            }
        """)
        
    def set_card(self, card_text: str):
        self.card_text = card_text
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 設置字體
        font = QFont("Arial", 14)
        painter.setFont(font)
        
        # 繪製卡片文字
        painter.drawText(self.rect(), Qt.AlignCenter, self.card_text)

class BaccaratUI(QWidget):
    def __init__(self, user_id: int, db_manager, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.game = BaccaratGame(db_manager)
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """設置UI界面"""
        layout = QVBoxLayout()
        
        # 牌桌區域
        table_layout = QHBoxLayout()
        
        # 閒家區域
        player_frame = QFrame()
        player_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        player_layout = QVBoxLayout()
        player_layout.addWidget(QLabel("閒家", alignment=Qt.AlignCenter))
        self.player_cards = [CardFrame() for _ in range(3)]
        cards_layout = QHBoxLayout()
        for card in self.player_cards:
            cards_layout.addWidget(card)
        player_layout.addLayout(cards_layout)
        player_layout.addWidget(QLabel("點數: 0", alignment=Qt.AlignCenter))
        player_frame.setLayout(player_layout)
        table_layout.addWidget(player_frame)
        
        # 莊家區域
        banker_frame = QFrame()
        banker_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        banker_layout = QVBoxLayout()
        banker_layout.addWidget(QLabel("莊家", alignment=Qt.AlignCenter))
        self.banker_cards = [CardFrame() for _ in range(3)]
        cards_layout = QHBoxLayout()
        for card in self.banker_cards:
            cards_layout.addWidget(card)
        banker_layout.addLayout(cards_layout)
        banker_layout.addWidget(QLabel("點數: 0", alignment=Qt.AlignCenter))
        banker_frame.setLayout(banker_layout)
        table_layout.addWidget(banker_frame)
        
        layout.addLayout(table_layout)
        
        # 下注控制區域
        bet_layout = QHBoxLayout()
        
        # 下注類型選擇
        self.bet_type_combo = QComboBox()
        bet_types = self.game.get_bet_types()
        for bet_type, info in bet_types.items():
            self.bet_type_combo.addItem(info["name"], bet_type)
        bet_layout.addWidget(QLabel("下注類型:"))
        bet_layout.addWidget(self.bet_type_combo)
        
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
        
    def place_bet(self):
        """下注"""
        bet_type = self.bet_type_combo.currentData()
        bet_amount = self.bet_amount_spin.value()
        
        # 下注
        success, message = self.game.place_bet(
            self.user_id, bet_type, bet_amount
        )
        
        if not success:
            QMessageBox.warning(self, "下注失敗", message)
            return
            
        # 開始遊戲
        self.bet_button.setEnabled(False)
        self.play_game(bet_type, bet_amount)
        
    def play_game(self, bet_type: str, bet_amount: int):
        """開始遊戲"""
        result = self.game.play(self.user_id, bet_type, bet_amount)
        if result:
            self.show_result(result)
            
    def show_result(self, result_data: dict):
        """顯示遊戲結果"""
        self.bet_button.setEnabled(True)
        
        # 顯示閒家牌
        for i, card in enumerate(result_data["player_cards"]):
            self.player_cards[i].set_card(card)
            
        # 顯示莊家牌
        for i, card in enumerate(result_data["banker_cards"]):
            self.banker_cards[i].set_card(card)
            
        # 顯示點數
        player_points = result_data["player_points"]
        banker_points = result_data["banker_points"]
        
        # 顯示結果
        result = result_data["result"]
        win = result_data["win"]
        payout = result_data["payout"]
        
        message = f"閒家點數: {player_points} 莊家點數: {banker_points}\n"
        message += f"結果: {result}\n"
        if win:
            message += f"恭喜中獎！獲得 {payout} 積分"
        else:
            message += "未中獎"
            
        self.result_label.setText(message)
        
    def update_points_display(self, points: int):
        """更新積分顯示"""
        # 這裡可以添加更新積分顯示的邏輯
        pass 