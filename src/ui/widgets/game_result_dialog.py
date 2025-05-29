from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class GameResultDialog(QDialog):
    def __init__(self, user, win, points_change, parent=None):
        super().__init__(parent)
        self.setWindowTitle("遊戲結果")
        self.setFixedSize(400, 200)

        result = "勝利！" if win else "失敗"
        color = "#4CAF50" if win else "#e94560"
        self.result_label = QLabel(f"<b style='color:{color}'>{result}</b>", self)
        self.result_label.setAlignment(Qt.AlignCenter)

        self.points_label = QLabel(f"本局積分變化：{points_change}，當前積分：{user.credits}", self)
        self.points_label.setAlignment(Qt.AlignCenter)

        self.ok_button = QPushButton("返回主界面", self)
        self.ok_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.result_label)
        layout.addWidget(self.points_label)
        layout.addWidget(self.ok_button)
        self.setLayout(layout) 