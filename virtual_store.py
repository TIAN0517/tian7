import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QScrollArea, QFrame, QMessageBox,
                            QGridLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont

class ItemCard(QFrame):
    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setup_ui()
    
    def setup_ui(self):
        self.setObjectName("itemCard")
        self.setFixedSize(200, 250)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 物品圖標
        icon_label = QLabel()
        icon_label.setFixedSize(100, 100)
        icon_label.setObjectName("itemIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        # TODO: 加載實際圖標
        icon_label.setStyleSheet("background-color: #2d2d2d; border-radius: 50px;")
        
        # 物品名稱
        name_label = QLabel(self.item_data["name"])
        name_label.setObjectName("itemName")
        name_label.setAlignment(Qt.AlignCenter)
        
        # 物品描述
        desc_label = QLabel(self.item_data["description"])
        desc_label.setObjectName("itemDescription")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        
        # 物品價格
        price_label = QLabel(f"{self.item_data['price']} 積分")
        price_label.setObjectName("itemPrice")
        price_label.setAlignment(Qt.AlignCenter)
        
        # 購買按鈕
        buy_button = QPushButton("購買")
        buy_button.setObjectName("buyButton")
        buy_button.clicked.connect(self.handle_buy)
        
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        layout.addWidget(name_label)
        layout.addWidget(desc_label)
        layout.addWidget(price_label)
        layout.addWidget(buy_button)
    
    def handle_buy(self):
        self.parent().parent().handle_item_purchase(self.item_data)

class VirtualStoreWindow(QWidget):
    def __init__(self, user_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.setup_ui()
        self.load_items()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # 頂部欄
        top_bar = QHBoxLayout()
        
        # 用戶積分
        points_label = QLabel("積分: 0")
        points_label.setObjectName("pointsLabel")
        self.points_label = points_label
        
        # 購物車按鈕
        cart_button = QPushButton("購物車")
        cart_button.setObjectName("cartButton")
        cart_button.clicked.connect(self.show_cart)
        
        top_bar.addWidget(points_label)
        top_bar.addStretch()
        top_bar.addWidget(cart_button)
        
        # 分類選擇
        category_layout = QHBoxLayout()
        categories = ["全部", "特權", "道具", "禮包"]
        for category in categories:
            btn = QPushButton(category)
            btn.setObjectName("categoryButton")
            btn.clicked.connect(lambda checked, c=category: self.filter_items(c))
            category_layout.addWidget(btn)
        
        # 物品網格
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("itemScrollArea")
        
        self.items_widget = QWidget()
        self.items_layout = QGridLayout(self.items_widget)
        self.items_layout.setSpacing(20)
        
        scroll_area.setWidget(self.items_widget)
        
        # 添加所有元件到主佈局
        layout.addLayout(top_bar)
        layout.addLayout(category_layout)
        layout.addWidget(scroll_area)
        
        # 設置樣式
        self.load_styles()
    
    def load_items(self):
        """從數據庫加載物品"""
        # TODO: 從數據庫加載物品
        # 臨時使用測試數據
        test_items = [
            {
                "id": 1,
                "name": "VIP會員",
                "description": "獲得VIP特權30天",
                "price": 500,
                "category": "特權"
            },
            {
                "id": 2,
                "name": "幸運符",
                "description": "增加遊戲幸運值",
                "price": 100,
                "category": "道具"
            },
            {
                "id": 3,
                "name": "經驗加倍",
                "description": "遊戲經驗值加倍24小時",
                "price": 200,
                "category": "道具"
            }
        ]
        
        self.display_items(test_items)
    
    def display_items(self, items):
        """顯示物品列表"""
        # 清除現有物品
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加新物品
        row = 0
        col = 0
        max_cols = 4
        
        for item in items:
            card = ItemCard(item, self)
            self.items_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def filter_items(self, category):
        """根據分類過濾物品"""
        # TODO: 實現分類過濾
        pass
    
    def show_cart(self):
        """顯示購物車"""
        # TODO: 實現購物車功能
        QMessageBox.information(self, "購物車", "購物車功能開發中...")
    
    def handle_item_purchase(self, item):
        """處理物品購買"""
        # TODO: 實現購買邏輯
        reply = QMessageBox.question(
            self,
            "確認購買",
            f"確定要購買 {item['name']} 嗎？\n價格: {item['price']} 積分",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # TODO: 檢查用戶積分是否足夠
            # TODO: 扣除積分並添加物品到用戶物品欄
            QMessageBox.information(self, "購買成功", f"成功購買 {item['name']}！")
    
    def update_points(self, points):
        """更新顯示的積分"""
        self.points_label.setText(f"積分: {points}")
    
    def load_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            
            #pointsLabel {
                font-size: 16px;
                font-weight: bold;
            }
            
            #cartButton {
                background-color: #363636;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
            }
            
            #cartButton:hover {
                background-color: #4a4a4a;
            }
            
            #categoryButton {
                background-color: #2d2d2d;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
            }
            
            #categoryButton:hover {
                background-color: #363636;
            }
            
            #categoryButton:checked {
                background-color: #00ff00;
                color: #000000;
            }
            
            #itemScrollArea {
                border: none;
                background-color: transparent;
            }
            
            #itemCard {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
            }
            
            #itemIcon {
                background-color: #363636;
                border-radius: 50px;
            }
            
            #itemName {
                font-size: 16px;
                font-weight: bold;
            }
            
            #itemDescription {
                font-size: 12px;
                color: #cccccc;
            }
            
            #itemPrice {
                font-size: 14px;
                color: #00ff00;
            }
            
            #buyButton {
                background-color: #00ff00;
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            
            #buyButton:hover {
                background-color: #00cc00;
            }
            
            #buyButton:pressed {
                background-color: #009900;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VirtualStoreWindow()
    window.show()
    sys.exit(app.exec_()) 