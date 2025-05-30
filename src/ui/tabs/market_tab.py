from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QSizePolicy, QGraphicsDropShadowEffect,
                            QScrollArea, QGridLayout, QLineEdit, QComboBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QColor, QPixmap

class MarketTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """設置裝備市場UI"""
        # 創建主佈局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 標題
        title = QLabel("裝備市場")
        title.setFont(QFont("'Noto Sans TC', 'Microsoft JhengHei'", 24, QFont.Bold))
        title.setStyleSheet("color: #FFD700;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # 搜索和過濾區域
        filter_layout = QHBoxLayout()
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索裝備...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #2a2b45;
                color: #ffffff;
                border: 2px solid #3a3b55;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #FFD700;
            }
        """)
        filter_layout.addWidget(self.search_input)
        
        # 分類過濾
        self.category_combo = QComboBox()
        self.category_combo.addItems(["全部", "武器", "防具", "飾品", "消耗品"])
        self.category_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2b45;
                color: #ffffff;
                border: 2px solid #3a3b55;
                border-radius: 5px;
                padding: 8px;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(assets/icons/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        filter_layout.addWidget(self.category_combo)
        
        # 價格排序
        self.price_combo = QComboBox()
        self.price_combo.addItems(["價格排序", "從低到高", "從高到低"])
        self.price_combo.setStyleSheet(self.category_combo.styleSheet())
        filter_layout.addWidget(self.price_combo)
        
        main_layout.addLayout(filter_layout)
        
        # 創建滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #2a2b45;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3a3b55;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #4a4b65;
            }
        """)
        
        # 創建商品網格
        self.items_widget = QWidget()
        self.items_layout = QGridLayout(self.items_widget)
        self.items_layout.setSpacing(20)
        
        # 添加示例商品
        self.add_sample_items()
        
        scroll_area.setWidget(self.items_widget)
        main_layout.addWidget(scroll_area)
        
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
                background-color: #2ecc71;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        
    def add_sample_items(self):
        """添加示例商品"""
        items = [
            ("+15 傳說之劍", "assets/items/sword.png", "傳說級武器", "1000 USDT"),
            ("+12 龍鱗護甲", "assets/items/armor.png", "史詩級防具", "800 USDT"),
            ("+10 天使之翼", "assets/items/wings.png", "稀有級飾品", "500 USDT"),
            ("+9 惡魔之眼", "assets/items/accessory.png", "稀有級飾品", "400 USDT"),
            ("+8 戰神之靴", "assets/items/boots.png", "高級防具", "300 USDT"),
            ("+7 魔法戒指", "assets/items/ring.png", "高級飾品", "200 USDT")
        ]
        
        row = 0
        col = 0
        for name, icon_path, quality, price in items:
            item_card = self.create_item_card(name, icon_path, quality, price)
            self.items_layout.addWidget(item_card, row, col)
            col += 1
            if col > 2:  # 每行3個商品
                col = 0
                row += 1
                
    def create_item_card(self, name, icon_path, quality, price):
        """創建商品卡片"""
        card = QFrame()
        card.setMinimumSize(250, 350)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 商品圖標
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(icon_path).pixmap(QSize(128, 128)))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # 商品名稱
        name_label = QLabel(name)
        name_label.setFont(QFont("'Noto Sans TC', 'Microsoft JhengHei'", 14, QFont.Bold))
        name_label.setStyleSheet("color: #FFD700;")
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # 品質
        quality_label = QLabel(quality)
        quality_label.setStyleSheet("color: #2ecc71;")
        quality_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(quality_label)
        
        # 價格
        price_label = QLabel(price)
        price_label.setFont(QFont("'Noto Sans TC', 'Microsoft JhengHei'", 16, QFont.Bold))
        price_label.setStyleSheet("color: #ffffff;")
        price_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(price_label)
        
        # 購買按鈕
        buy_button = QPushButton("立即購買")
        buy_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(buy_button)
        
        # 添加發光效果
        glow = QGraphicsDropShadowEffect()
        glow.setColor(QColor(255, 215, 0, 100))
        glow.setBlurRadius(20)
        card.setGraphicsEffect(glow)
        
        return card 