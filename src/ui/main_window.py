from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QTextEdit, QProgressBar,
    QTabWidget, QGridLayout, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from pathlib import Path
import sys
import os

from ..core.config import config
from ..core.logger import get_logger
from ..core.auth import Auth
from ..core.updater import Updater
from .widgets.ai_chat_dialog import AIChatDialog
from .widgets.login_dialog import LoginDialog
from .widgets.virtual_items_dialog import VirtualItemsDialog
from .widgets.game_loading_dialog import GameLoadingDialog
from .widgets.game_main_window import GameMainWindow
from .widgets.casino_game_window import CasinoGameWindow

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    """主窗口類"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config['APP_NAME'])
        self.setMinimumSize(1200, 800)
        
        # 用戶狀態
        self.current_user = None
        
        # 初始化組件
        self.init_ui()
        self.load_styles()
        self.setup_connections()
        
        # 初始化更新器
        self.updater = Updater()
        
        # 顯示登錄對話框
        self.show_login()
        
    def show_login(self):
        """顯示登錄對話框"""
        dialog = LoginDialog(self)
        if dialog.exec_() == Dialog.Accepted: # type: ignore
            # 登錄成功，更新用戶信息
            self.current_user = Auth.get_current_user()
            self.update_user_info()
            # 檢查更新
            self.check_updates()
        else:
            # 登錄取消，關閉程序
            self.close()
            
    def update_user_info(self):
        """更新用戶信息顯示"""
        if self.current_user:
            self.user_info_label.setText(
                f"用戶名：{self.current_user.username}\n"
                f"積分：{self.current_user.credits}"
            )
        else:
            self.user_info_label.setText("未登錄")
            
    def init_ui(self):
        """初始化 UI 組件"""
        # 創建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 頂部區域
        top_area = self.create_top_area()
        main_layout.addWidget(top_area)
        
        # 遊戲區域
        game_area = self.create_game_area()
        main_layout.addWidget(game_area)
        
        # 底部區域
        bottom_area = self.create_bottom_area()
        main_layout.addWidget(bottom_area)
        
        # 狀態欄
        self.statusBar().showMessage("就緒")
        
    def create_top_area(self) -> QWidget:
        """創建頂部區域"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 用戶信息
        user_info = QFrame()
        user_info.setObjectName("userInfo")
        user_layout = QVBoxLayout(user_info)
        
        self.username_label = QLabel("遊客")
        self.username_label.setObjectName("title")
        self.credits_label = QLabel("積分: 0")
        self.credits_label.setObjectName("subtitle")
        
        # 添加虛寶兌換按鈕
        virtual_items_button = QPushButton("虛寶兌換")
        virtual_items_button.setObjectName("virtualItemsButton")
        virtual_items_button.clicked.connect(self.show_virtual_items)
        
        # 添加登出按鈕
        self.logout_button = QPushButton("登出")
        self.logout_button.setObjectName("logoutButton")
        self.logout_button.clicked.connect(self.handle_logout)
        
        user_layout.addWidget(self.username_label)
        user_layout.addWidget(self.credits_label)
        user_layout.addWidget(virtual_items_button)
        user_layout.addWidget(self.logout_button)
        
        # 系統公告
        announcement = QFrame()
        announcement.setObjectName("announcement")
        announcement_layout = QVBoxLayout(announcement)
        
        self.announcement_label = QLabel("系統公告：歡迎使用 N.L.Online 遊戲啟動器")
        self.announcement_label.setObjectName("announcement")
        announcement_layout.addWidget(self.announcement_label)
        
        # 添加到布局
        layout.addWidget(user_info, 1)
        layout.addWidget(announcement, 2)
        
        return widget
        
    def create_game_area(self) -> QWidget:
        """創建遊戲區域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 遊戲標籤頁
        tab_widget = QTabWidget()
        tab_widget.setObjectName("gameTabs")
        
        # 主遊戲標籤
        main_game_tab = QWidget()
        main_game_layout = QGridLayout(main_game_tab)
        
        # 創建遊戲卡片
        for i in range(6):  # 示例：6個遊戲卡片
            game_card = self.create_game_card(f"遊戲 {i+1}")
            main_game_layout.addWidget(game_card, i//3, i%3)
            
        # 賭場遊戲標籤
        casino_tab = QWidget()
        casino_layout = QGridLayout(casino_tab)
        
        # 創建賭場遊戲卡片
        for i in range(4):  # 示例：4個賭場遊戲
            casino_card = self.create_casino_card(f"賭場遊戲 {i+1}")
            casino_layout.addWidget(casino_card, i//2, i%2)
            
        # 添加標籤頁
        tab_widget.addTab(main_game_tab, "主遊戲")
        tab_widget.addTab(casino_tab, "賭場遊戲")
        
        layout.addWidget(tab_widget)
        return widget
        
    def create_bottom_area(self) -> QWidget:
        """創建底部區域"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # AI 客服按鈕
        self.ai_chat_btn = QPushButton("啟動 AI 小幫手")
        self.ai_chat_btn.setObjectName("aiChatButton")
        
        # 更新進度條
        self.update_progress = QProgressBar()
        self.update_progress.setObjectName("updateProgress")
        self.update_progress.hide()
        
        # 添加到布局
        layout.addWidget(self.ai_chat_btn)
        layout.addWidget(self.update_progress)
        
        return widget
        
    def create_game_card(self, title: str) -> QFrame:
        """創建遊戲卡片"""
        card = QFrame()
        card.setObjectName("gameCard")
        card.setMinimumSize(300, 200)
        
        layout = QVBoxLayout(card)
        
        # 遊戲標題
        title_label = QLabel(title)
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        
        # 遊戲描述
        desc_label = QLabel("點擊開始遊戲")
        desc_label.setObjectName("subtitle")
        desc_label.setAlignment(Qt.AlignCenter)
        
        # 開始按鈕
        start_btn = QPushButton("開始遊戲")
        start_btn.setObjectName("startGameButton")
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(start_btn)
        
        return card
        
    def create_casino_card(self, title: str) -> QFrame:
        """創建賭場遊戲卡片"""
        card = QFrame()
        card.setObjectName("casinoGame")
        card.setMinimumSize(400, 250)
        
        layout = QVBoxLayout(card)
        
        # 遊戲標題
        title_label = QLabel(title)
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        
        # 遊戲描述
        desc_label = QLabel("進入賭場遊戲")
        desc_label.setObjectName("subtitle")
        desc_label.setAlignment(Qt.AlignCenter)
        
        # 開始按鈕
        start_btn = QPushButton("進入遊戲")
        start_btn.setObjectName("enterCasinoButton")
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(start_btn)
        
        return card
        
    def load_styles(self):
        """加載樣式表"""
        style_path = Path(__file__).parent / "styles" / "main.qss"
        with open(style_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
            
    def setup_connections(self):
        """設置信號連接"""
        # AI 客服按鈕點擊事件
        self.ai_chat_btn.clicked.connect(self.show_ai_chat)
        
        # 遊戲卡片點擊事件
        for game_card in self.findChildren(QFrame, "gameCard"):
            start_btn = game_card.findChild(QPushButton, "startGameButton")
            if start_btn:
                start_btn.clicked.connect(lambda checked, card=game_card: self.start_game(card))
                
        for casino_card in self.findChildren(QFrame, "casinoGame"):
            enter_btn = casino_card.findChild(QPushButton, "enterCasinoButton")
            if enter_btn:
                enter_btn.clicked.connect(lambda checked, card=casino_card: self.enter_casino(card))
                
    def handle_logout(self):
        """處理登出"""
        reply = QMessageBox.question(
            self, "確認登出",
            "確定要登出嗎？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_user = None
            self.update_user_info()
            self.show_login()
            
    def start_game(self, game_card):
        """啟動遊戲"""
        if not self.current_user:
            QMessageBox.warning(self, "錯誤", "請先登錄")
            return
        # 1. 顯示加載窗口
        loading_dialog = GameLoadingDialog(self)
        if loading_dialog.exec_() == QDialog.Accepted: # type: ignore
            # 2. 加載完成，進入遊戲主界面
            game_window = GameMainWindow(self.current_user, self)
            game_window.exec_()
            # 3. 遊戲結束後自動返回主界面並刷新積分
            self.update_user_info()
        
    def enter_casino(self, casino_card):
        """進入賭場遊戲"""
        if not self.current_user:
            QMessageBox.warning(self, "錯誤", "請先登錄")
            return
        if self.current_user.credits < 100:
            QMessageBox.warning(self, "錯誤", "積分不足，無法進入賭場遊戲")
            return
        casino_window = CasinoGameWindow(self.current_user, self)
        casino_window.exec_()
        self.update_user_info()
        
    def show_ai_chat(self):
        """顯示 AI 客服對話框"""
        if not self.current_user:
            QMessageBox.warning(self, "錯誤", "請先登錄")
            return
            
        dialog = AIChatDialog(self)
        dialog.exec_()
        
    def check_updates(self):
        """檢查更新"""
        if not self.current_user:
            return
            
        success, error = self.updater.run_update_check()
        if not success:
            QMessageBox.warning(self, "更新失敗", f"更新檢查失敗：{error}")
            return
            
        # 顯示更新進度
        self.update_progress.show()
        self.update_progress.setValue(0)
        
        # 模擬更新進度
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_progress_value)
        self.update_timer.start(100)
        
    def update_progress_value(self):
        """更新進度條值"""
        current = self.update_progress.value()
        if current < 100:
            self.update_progress.setValue(current + 1)
        else:
            self.update_timer.stop()
            self.update_progress.hide()
            QMessageBox.information(self, "更新完成", "更新完成，開始遊戲！")
            
    def show_virtual_items(self):
        """顯示虛寶兌換對話框"""
        if not self.current_user:
            QMessageBox.warning(self, "提示", "請先登錄")
            self.show_login()
            return
            
        dialog = VirtualItemsDialog(self)
        dialog.exec_()
        
        # 更新用戶積分顯示
        self.update_user_info()
        
    def closeEvent(self, event):
        """關閉窗口事件"""
        if self.current_user:
            reply = QMessageBox.question(
                self, "確認退出",
                "確定要退出遊戲啟動器嗎？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept() 