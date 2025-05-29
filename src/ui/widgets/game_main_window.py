from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
from .game_result_dialog import GameResultDialog

class GameMainWindow(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.setWindowTitle("遊戲主界面")
        self.setFixedSize(600, 400)
        self.user = user

        self.info_label = QLabel(f"歡迎進入遊戲，{self.user.username}！", self)
        self.info_label.setAlignment(Qt.AlignCenter)

        self.play_button = QPushButton("結束遊戲", self)
        self.play_button.clicked.connect(self.end_game)

        layout = QVBoxLayout()
        layout.addWidget(self.info_label)
        layout.addWidget(self.play_button)
        self.setLayout(layout)

    def end_game(self):
        import random
        win = random.choice([True, False])
        points_change = random.randint(50, 200) * (1 if win else -1)
        self.user.credits += points_change

        result_dialog = GameResultDialog(self.user, win, points_change, self)
        result_dialog.exec_()
        self.accept()  # 關閉遊戲主界面 