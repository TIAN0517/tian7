from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QWidget, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon, QColor
from ...core.auth import Auth
from ...core.logger import get_logger
from ...core.models import Transaction, TransactionType

logger = get_logger(__name__)

class VirtualItemsDialog(QDialog):
    """虛寶兌換對話框"""
    
    # 虛擬物品列表
    VIRTUAL_ITEMS = [
        {"id": 1, "name": "金幣", "points": 100, "description": "遊戲內通用貨幣"},
        {"id": 2, "name": "鑽石", "points": 500, "description": "高級遊戲貨幣"},
        {"id": 3, "name": "寶箱", "points": 1000, "description": "隨機獲得遊戲道具"},
        {"id": 4, "name": "VIP卡", "points": 2000, "description": "獲得VIP特權"},
        {"id": 5, "name": "限定皮膚", "points": 3000, "description": "獨特角色外觀"},
        {"id": 6, "name": "經驗卡", "points": 800, "description": "提升角色經驗"},
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("虛寶兌換")
        self.setMinimumSize(800, 600)
        self.current_user = Auth.get_current_user()
        self.setup_ui()
        self.load_items()
        self.load_history()
        
    def setup_ui(self):
        """設置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 頂部信息
        info_layout = QHBoxLayout()
        
        # 用戶積分
        points_label = QLabel(f"當前積分：{self.current_user.credits}")
        points_label.setObjectName("pointsLabel")
        self.points_label = points_label
        
        info_layout.addWidget(points_label)
        info_layout.addStretch()
        
        # 查看記錄按鈕
        history_button = QPushButton("查看兌換記錄")
        history_button.setObjectName("historyButton")
        history_button.clicked.connect(self.show_history)
        info_layout.addWidget(history_button)
        
        layout.addLayout(info_layout)
        
        # 標籤頁
        tab_widget = QTabWidget()
        tab_widget.setObjectName("virtualItemsTabs")
        
        # 物品列表標籤
        items_tab = QWidget()
        items_layout = QVBoxLayout(items_tab)
        
        # 物品列表
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["物品名稱", "所需積分", "描述", "操作"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        items_layout.addWidget(self.items_table)
        tab_widget.addTab(items_tab, "可兌換物品")
        
        # 兌換記錄標籤
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        # 兌換記錄表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["物品名稱", "兌換時間", "消耗積分", "狀態"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        history_layout.addWidget(self.history_table)
        tab_widget.addTab(history_tab, "兌換記錄")
        
        layout.addWidget(tab_widget)
        
    def load_items(self):
        """加載物品列表"""
        self.items_table.setRowCount(len(self.VIRTUAL_ITEMS))
        
        for row, item in enumerate(self.VIRTUAL_ITEMS):
            # 物品名稱
            name_item = QTableWidgetItem(item["name"])
            name_item.setTextAlignment(Qt.AlignCenter)
            self.items_table.setItem(row, 0, name_item)
            
            # 所需積分
            points_item = QTableWidgetItem(str(item["points"]))
            points_item.setTextAlignment(Qt.AlignCenter)
            self.items_table.setItem(row, 1, points_item)
            
            # 描述
            desc_item = QTableWidgetItem(item["description"])
            desc_item.setTextAlignment(Qt.AlignCenter)
            self.items_table.setItem(row, 2, desc_item)
            
            # 兌換按鈕
            exchange_button = QPushButton("兌換")
            exchange_button.setObjectName("exchangeButton")
            exchange_button.clicked.connect(lambda checked, item=item: self.exchange_item(item))
            
            # 如果積分不足，禁用按鈕
            if self.current_user.credits < item["points"]:
                exchange_button.setEnabled(False)
                exchange_button.setToolTip("積分不足")
                
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.addWidget(exchange_button)
            button_layout.setAlignment(Qt.AlignCenter)
            button_layout.setContentsMargins(0, 0, 0, 0)
            
            self.items_table.setCellWidget(row, 3, button_widget)
            
    def load_history(self):
        """加載兌換記錄"""
        # 從數據庫獲取兌換記錄
        session = Auth.get_session()
        transactions = session.query(Transaction).filter(
            Transaction.user_id == self.current_user.id,
            Transaction.type == TransactionType.ITEM_EXCHANGE
        ).order_by(Transaction.created_at.desc()).all()
        
        self.history_table.setRowCount(len(transactions))
        
        for row, trans in enumerate(transactions):
            # 物品名稱
            name_item = QTableWidgetItem(trans.description.split(":")[0])
            name_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row, 0, name_item)
            
            # 兌換時間
            time_item = QTableWidgetItem(trans.created_at.strftime("%Y-%m-%d %H:%M:%S"))
            time_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row, 1, time_item)
            
            # 消耗積分
            points_item = QTableWidgetItem(str(abs(trans.amount)))
            points_item.setTextAlignment(Qt.AlignCenter)
            self.history_table.setItem(row, 2, points_item)
            
            # 狀態
            status_item = QTableWidgetItem("成功" if trans.status == "completed" else "處理中")
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(QColor("#4CAF50" if trans.status == "completed" else "#FFA500"))
            self.history_table.setItem(row, 3, status_item)
            
    def exchange_item(self, item):
        """兌換物品"""
        if self.current_user.credits < item["points"]:
            QMessageBox.warning(self, "兌換失敗", "積分不足，無法兌換")
            return
            
        reply = QMessageBox.question(
            self, "確認兌換",
            f"確定要兌換 {item['name']} 嗎？\n將消耗 {item['points']} 積分",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 扣除積分
                self.current_user.credits -= item["points"]
                
                # 記錄交易
                session = Auth.get_session()
                transaction = Transaction(
                    user_id=self.current_user.id,
                    amount=-item["points"],
                    type=TransactionType.ITEM_EXCHANGE,
                    status="completed",
                    description=f"{item['name']}: {item['description']}"
                )
                session.add(transaction)
                session.commit()
                
                # 更新界面
                self.points_label.setText(f"當前積分：{self.current_user.credits}")
                self.load_items()
                self.load_history()
                
                QMessageBox.information(self, "兌換成功", f"成功兌換 {item['name']}！")
                
            except Exception as e:
                logger.error(f"兌換失敗: {str(e)}")
                QMessageBox.critical(self, "錯誤", f"兌換失敗：{str(e)}")
                
    def show_history(self):
        """顯示兌換記錄"""
        self.tab_widget.setCurrentIndex(1)
        
    def keyPressEvent(self, event):
        """按鍵事件"""
        if event.key() == Qt.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(event) 