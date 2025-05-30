from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class RankingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        title = QLabel("排行榜")
        title.setFont(QFont("'Noto Sans TC', 'Microsoft JhengHei'", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        table = QTableWidget(10, 3)
        table.setHorizontalHeaderLabels(["排名", "玩家名稱", "積分"])
        for i in range(10):
            table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            table.setItem(i, 1, QTableWidgetItem(f"玩家{i+1}"))
            table.setItem(i, 2, QTableWidgetItem(str(1000-i*10)))
        layout.addWidget(table)