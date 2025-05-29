from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
import random

class CasinoGameWindow(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.setWindowTitle("賭場遊戲")
        self.setFixedSize(600, 400)
        self.user = user

        self.bet_label = QLabel(f"當前積分：{self.user.credits}", self)
        self.bet_label.setAlignment(Qt.AlignCenter)

        self.bet_button = QPushButton("下注", self)
        self.bet_button.clicked.connect(self.place_bet)

        layout = QVBoxLayout()
        layout.addWidget(self.bet_label)
        layout.addWidget(self.bet_button)
        self.setLayout(layout)

    def place_bet(self):
        if self.user.credits >= 100:
            self.user.credits -= 100
            result = random.choice(["贏", "輸"])
            if result == "贏":
                self.user.credits += 200
                QMessageBox.information(self, "結果", "恭喜你贏了！獲得200積分。")
            else:
                QMessageBox.information(self, "結果", "很遺憾，你輸了。")
            self.bet_label.setText(f"當前積分：{self.user.credits}")
        else:
            QMessageBox.warning(self, "積分不足", "積分不足，無法下注！") 