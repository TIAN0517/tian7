from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
from typing import Optional

class BetWindow(QDialog):
    """下注窗口"""
    
    bet_placed = pyqtSignal(float)  # 下注信號
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("下注")
        self.setup_ui()
        
    def setup_ui(self):
        """設置UI"""
        layout = QVBoxLayout()
        
        # 下注金額輸入
        bet_layout = QHBoxLayout()
        bet_label = QLabel("下注金額:")
        self.bet_input = QLineEdit()
        self.bet_input.setPlaceholderText("請輸入下注金額")
        bet_layout.addWidget(bet_label)
        bet_layout.addWidget(self.bet_input)
        layout.addLayout(bet_layout)
        
        # 按鈕
        button_layout = QHBoxLayout()
        confirm_button = QPushButton("確認")
        cancel_button = QPushButton("取消")
        confirm_button.clicked.connect(self.confirm_bet)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def confirm_bet(self):
        """確認下注"""
        try:
            bet_amount = float(self.bet_input.text())
            if bet_amount <= 0:
                QMessageBox.warning(self, "錯誤", "下注金額必須大於0")
                return
                
            self.bet_placed.emit(bet_amount)
            self.accept()
            
        except ValueError:
            QMessageBox.warning(self, "錯誤", "請輸入有效的金額")
            
    def get_bet_amount(self) -> Optional[float]:
        """獲取下注金額"""
        try:
            return float(self.bet_input.text())
        except ValueError:
            return None 