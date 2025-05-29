from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt
from typing import List, Dict

class RankingWindow(QMainWindow):
    """排行榜窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("排行榜")
        self.setup_ui()
        
    def setup_ui(self):
        """設置UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 類別選擇
        category_layout = QHBoxLayout()
        category_label = QLabel("類別:")
        self.category_combo = QComboBox()
        self.category_combo.addItems(["總排行榜", "輪盤", "百家樂", "賓果", "基諾"])
        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)
        
        # 排行榜表格
        self.ranking_table = QTableWidget()
        self.ranking_table.setColumnCount(4)
        self.ranking_table.setHorizontalHeaderLabels(["排名", "用戶", "積分", "更新時間"])
        self.ranking_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.ranking_table)
        
        # 刷新按鈕
        refresh_button = QPushButton("刷新")
        refresh_button.clicked.connect(self.refresh_ranking)
        layout.addWidget(refresh_button)
        
    def update_ranking(self, rankings: List[Dict]):
        """更新排行榜"""
        self.ranking_table.setRowCount(len(rankings))
        for i, ranking in enumerate(rankings):
            # 排名
            rank_item = QTableWidgetItem(str(i + 1))
            rank_item.setTextAlignment(Qt.AlignCenter)
            self.ranking_table.setItem(i, 0, rank_item)
            
            # 用戶
            user_item = QTableWidgetItem(ranking["user_id"])
            self.ranking_table.setItem(i, 1, user_item)
            
            # 積分
            points_item = QTableWidgetItem(str(ranking["points"]))
            points_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.ranking_table.setItem(i, 2, points_item)
            
            # 更新時間
            time_item = QTableWidgetItem(ranking["updated_at"].strftime("%Y-%m-%d %H:%M:%S"))
            self.ranking_table.setItem(i, 3, time_item)
            
        self.ranking_table.resizeColumnsToContents()
        
    def on_category_changed(self, index: int):
        """類別變更處理"""
        categories = ["total", "roulette", "baccarat", "bingo", "keno"]
        if 0 <= index < len(categories):
            self.refresh_ranking(categories[index])
            
    def refresh_ranking(self, category: str = None):
        """刷新排行榜"""
        if category is None:
            category = self.category_combo.currentText().lower()
        # 這裡需要實現從RankingManager獲取數據的邏輯 