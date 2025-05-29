from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSpinBox, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QPen
from .roulette import RouletteGame

class RouletteUI(QWidget):
    def __init__(self, user_id: int, db_manager, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.game = RouletteGame(db_manager)
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """設置UI界面"""
        layout = QVBoxLayout()
        
        # 輪盤顯示區域
        self.wheel_label = QLabel()
        self.wheel_label.setFixedSize(300, 300)
        self.wheel_label.setStyleSheet("border: 2px solid black;")
        layout.addWidget(self.wheel_label, alignment=Qt.AlignCenter)
        
        # 下注控制區域
        bet_layout = QHBoxLayout()
        
        # 下注類型選擇
        self.bet_type_combo = QComboBox()
        bet_types = self.game.get_bet_types()
        for bet_type, info in bet_types.items():
            self.bet_type_combo.addItem(info["name"], bet_type)
        bet_layout.addWidget(QLabel("下注類型:"))
        bet_layout.addWidget(self.bet_type_combo)
        
        # 下注值選擇
        self.bet_value_combo = QComboBox()
        self.update_bet_values()
        bet_layout.addWidget(QLabel("下注值:"))
        bet_layout.addWidget(self.bet_value_combo)
        
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
        self.bet_type_combo.currentIndexChanged.connect(self.update_bet_values)
        self.bet_button.clicked.connect(self.place_bet)
        self.game.game_result.connect(self.show_result)
        self.game.points_updated.connect(self.update_points_display)
        
    def update_bet_values(self):
        """更新下注值選項"""
        self.bet_value_combo.clear()
        bet_type = self.bet_type_combo.currentData()
        bet_types = self.game.get_bet_types()
        values = bet_types[bet_type]["values"]
        
        for value in values:
            if bet_type == "number":
                self.bet_value_combo.addItem(str(value), value)
            elif bet_type == "color":
                self.bet_value_combo.addItem("紅色" if value == "red" else "黑色", value)
            elif bet_type == "odd_even":
                self.bet_value_combo.addItem("單" if value == "odd" else "雙", value)
                
    def place_bet(self):
        """下注"""
        bet_type = self.bet_type_combo.currentData()
        bet_value = self.bet_value_combo.currentData()
        bet_amount = self.bet_amount_spin.value()
        
        # 下注
        success, message = self.game.place_bet(
            self.user_id, bet_type, str(bet_value), bet_amount
        )
        
        if not success:
            QMessageBox.warning(self, "下注失敗", message)
            return
            
        # 開始遊戲
        self.bet_button.setEnabled(False)
        self.start_wheel_animation()
        
    def start_wheel_animation(self):
        """開始輪盤動畫"""
        # 這裡可以添加輪盤旋轉動畫
        # 動畫結束後調用 spin 方法
        self.game.spin(
            self.user_id,
            self.bet_type_combo.currentData(),
            str(self.bet_value_combo.currentData()),
            self.bet_amount_spin.value()
        )
        
    def show_result(self, result_data: dict):
        """顯示遊戲結果"""
        self.bet_button.setEnabled(True)
        
        result = result_data["result"]
        win = result_data["win"]
        payout = result_data["payout"]
        
        message = f"開獎號碼: {result}\n"
        if win:
            message += f"恭喜中獎！獲得 {payout} 積分"
        else:
            message += "未中獎"
            
        self.result_label.setText(message)
        
    def update_points_display(self, points: int):
        """更新積分顯示"""
        # 這裡可以添加更新積分顯示的邏輯
        pass
        
    def paintEvent(self, event):
        """繪製輪盤"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 繪製輪盤外圈
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        painter.drawEllipse(50, 50, 200, 200)
        
        # 這裡可以添加更多輪盤繪製邏輯 