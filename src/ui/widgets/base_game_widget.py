from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class BaseGameWidget(QDialog):
    def __init__(self, game_name, game_desc, parent=None):
        super().__init__(parent)
        self.setWindowTitle(game_name)
        self.setFixedSize(900, 600)
        self.setStyleSheet("""
        QDialog, QWidget {
            font-family: 'Noto Sans TC', 'Microsoft JhengHei', 'Arial', 'sans-serif';
        }
        QLabel#title {
            font-size: 30px;
            font-weight: 900;
            color: #FFD700;
            text-shadow: 0 2px 18px #000, 0 0 18px #FFD700;
        }
        QLabel#desc {
            font-size: 17px;
            font-weight: 500;
            color: #e0e0e0;
            margin: 18px 0;
            text-shadow: 0 1px 8px #000;
        }
        QPushButton#backBtn {
            font-size: 18px;
            font-weight: 800;
            text-shadow: 0 1px 8px #000;
        }
        QDialog, QMessageBox {
            font-family: 'Noto Sans TC', 'Microsoft JhengHei', 'Arial', 'sans-serif';
            font-size: 18px;
            font-weight: 800;
            color: #FFD700;
            text-shadow: 0 2px 16px #000, 0 0 16px #FFD700;
        }
        QMessageBox QLabel, QDialog QLabel {
            font-size: 17px;
            font-weight: 700;
            color: #FFD700;
            text-shadow: 0 2px 16px #000, 0 0 16px #FFD700;
        }
        QMessageBox QPushButton, QDialog QPushButton {
            font-size: 16px;
            font-weight: 700;
            text-shadow: 0 1px 8px #000;
        }
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel(game_name)
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        desc = QLabel(game_desc)
        desc.setObjectName("desc")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        back_btn = QPushButton("返回遊戲大廳")
        back_btn.setObjectName("backBtn")
        back_btn.clicked.connect(self.accept)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addWidget(back_btn) 