from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QColor

class CasinoTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """設置娛樂城UI"""
        # 創建主佈局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 標題
        title = QLabel("娛樂城")
        title.setFont(QFont("'Noto Sans TC', 'Microsoft JhengHei'", 24, QFont.Bold))
        title.setStyleSheet("color: #FFD700;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # 遊戲區域
        games_layout = QHBoxLayout()
        games_layout.setSpacing(20)
        
        # 創建遊戲卡片
        games = [
            ("幸運輪盤", "assets/icons/wheel.png", "經典幸運輪盤遊戲，轉動命運之輪！"),
            ("撲克王", "assets/icons/poker.png", "德州撲克、21點等多種撲克遊戲"),
            ("老虎機", "assets/icons/slot.png", "經典老虎機，體驗刺激的拉霸樂趣"),
            ("骰寶", "assets/icons/dice.png", "傳統骰寶遊戲，考驗你的運氣")
        ]
        
        for game_name, icon_path, description in games:
            game_card = self.create_game_card(game_name, icon_path, description)
            games_layout.addWidget(game_card)
        
        main_layout.addLayout(games_layout)
        
        # 設置背景
        self.setStyleSheet("""
            QWidget {
                background-color: #23243a;
                color: #ffffff;
            }
            QFrame {
                background-color: #2a2b45;
                border-radius: 10px;
            }
            QFrame:hover {
                background-color: #32334f;
            }
            QPushButton {
                background-color: #B31217;
                color: #F7E7CE;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D4131D;
            }
        """)
        
    def create_game_card(self, name, icon_path, description):
        """創建遊戲卡片"""
        card = QFrame()
        card.setMinimumSize(200, 300)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 遊戲圖標
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(64, 64)))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # 遊戲名稱
        name_label = QLabel(name)
        name_label.setFont(QFont("'Noto Sans TC', 'Microsoft JhengHei'", 16, QFont.Bold))
        name_label.setStyleSheet("color: #F7E7CE;")
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # 遊戲描述
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #ffffff;")
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)
        
        # 進入遊戲按鈕
        enter_button = QPushButton("進入遊戲")
        enter_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(enter_button)
        
        # 添加發光效果
        glow = QGraphicsDropShadowEffect()
        glow.setColor(QColor(255, 215, 0, 100))
        glow.setBlurRadius(20)
        card.setGraphicsEffect(glow)
        
        return card 