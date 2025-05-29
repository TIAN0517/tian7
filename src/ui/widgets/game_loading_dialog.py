from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer

class GameLoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("遊戲加載中")
        self.setFixedSize(400, 150)
        self.progress = 0

        self.label = QLabel("正在加載遊戲...", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)  # 平滑過渡

    def update_progress(self):
        if self.progress < 100:
            self.progress += 1
            self.progress_bar.setValue(self.progress)
        else:
            self.timer.stop()
            self.accept()  # 關閉加載窗口 