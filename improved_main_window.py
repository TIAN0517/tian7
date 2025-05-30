import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QTextEdit, QProgressBar,
    QTabWidget, QGridLayout, QLineEdit, QMessageBox, QStackedWidget,
    QApplication
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap
from database import DatabaseManager, UserManager

class EnhancedGameCard(QFrame):
    """增強版遊戲卡片"""
    
    def __init__(self, game_data, parent=None):
        super().__init__(parent)
        self.game_data = game_data
        self.parent_window = parent
        self.setup_ui()
    
    def setup_ui(self):
        self.setObjectName("enhancedGameCard")
        self.setFixedSize(280, 320)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 遊戲圖標
        icon_label = QLabel()
        icon_label.setFixedSize(120, 120)
        icon_label.setObjectName("gameIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: #3d3d3d;
                border-radius: 60px;
                border: 3px solid #5a5a5a;
            }
        """)
        
        # 遊戲名稱
        name_label = QLabel(self.game_data["name"])
        name_label.setObjectName("gameName")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                margin: 5px 0;
            }
        """)
        
        # 遊戲描述
        desc_label = QLabel(self.game_data["description"])
        desc_label.setObjectName("gameDescription")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #cccccc;
                margin: 5px 0;
            }
        """)
        
        # 下注範圍
        if "min_bet" in self.game_data and "max_bet" in self.game_data:
            bet_range_label = QLabel(f"下注範圍: {self.game_data['min_bet']}-{self.game_data['max_bet']}")
            bet_range_label.setAlignment(Qt.AlignCenter)
            bet_range_label.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    color: #ffd700;
                    margin: 2px 0;
                }
            """)
        
        # 啟動按鈕
        launch_button = QPushButton("🎮 啟動遊戲")
        launch_button.setObjectName("launchButton")
        launch_button.clicked.connect(self.handle_launch)
        launch_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        # 添加組件到佈局
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        layout.addWidget(name_label)
        layout.addWidget(desc_label)
        if "min_bet" in self.game_data:
            layout.addWidget(bet_range_label)
        layout.addWidget(launch_button)
    
    def handle_launch(self):
        """處理遊戲啟動"""
        if self.parent_window:
            self.parent_window.launch_game(self.game_data)

class EnhancedMainWindow(QMainWindow):
    """增強版主視窗"""
    
    def __init__(self, user_manager=None):
        super().__init__()
        self.user_manager = user_manager or UserManager()
        self.db_manager = None
        self.games_data = []
        self.current_user = None
        self.setup_ui()
        self.load_default_games()
    
    def set_database_managers(self, db_manager, user_manager):
        """設置資料庫管理器"""
        self.db_manager = db_manager
        self.user_manager = user_manager
    
    def set_games_data(self, games_data):
        """設置遊戲資料"""
        self.games_data = games_data
        self.refresh_games_display()
    
    def setup_ui(self):
        self.setWindowTitle("RanNL Game Launcher - 完整整合版")
        self.setMinimumSize(1400, 900)
        
        # 創建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主佈局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左側邊欄
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # 右側內容區域
        content_area = self.create_content_area()
        main_layout.addWidget(content_area)
        
        # 載入樣式
        self.load_styles()
    
    def create_sidebar(self):
        """創建側邊欄"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(300)
        
        layout = QVBoxLayout(sidebar)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 應用程式標題
        title_label = QLabel("🎮 RanNL")
        title_label.setObjectName("appTitle")
        title_label.setAlignment(Qt.AlignCenter)
        
        # 用戶信息區域
        user_info_frame = self.create_user_info_frame()
        
        # 導航按鈕
        nav_frame = self.create_navigation_frame()
        
        # 系統信息
        system_info_frame = self.create_system_info_frame()
        
        layout.addWidget(title_label)
        layout.addWidget(user_info_frame)
        layout.addWidget(nav_frame)
        layout.addStretch()
        layout.addWidget(system_info_frame)
        
        return sidebar
    
    def create_user_info_frame(self):
        """創建用戶信息框架"""
        frame = QFrame()
        frame.setObjectName("userInfoFrame")
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        
        # 頭像
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(100, 100)
        self.avatar_label.setObjectName("avatar")
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setText("👤")
        
        # 用戶名
        self.username_label = QLabel("遊客")
        self.username_label.setObjectName("username")
        self.username_label.setAlignment(Qt.AlignCenter)
        
        # 積分
        self.points_label = QLabel("積分: 0")
        self.points_label.setObjectName("points")
        self.points_label.setAlignment(Qt.AlignCenter)
        
        # 登入/登出按鈕
        self.login_button = QPushButton("🔑 登入")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.handle_login_logout)
        
        layout.addWidget(self.avatar_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.username_label)
        layout.addWidget(self.points_label)
        layout.addWidget(self.login_button)
        
        return frame
    
    def create_navigation_frame(self):
        """創建導航框架"""
        frame = QFrame()
        frame.setObjectName("navigationFrame")
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        
        nav_buttons = [
            ("🎮 遊戲庫", "gameLibrary"),
            ("🏪 虛擬商店", "virtualStore"),
            ("🏆 成就系統", "achievements"),
            ("📊 統計資料", "statistics"),
            ("⚙️ 設置", "settings"),
            ("🤖 AI客服", "customerService")
        ]
        
        for text, name in nav_buttons:
            btn = QPushButton(text)
            btn.setObjectName(f"nav_{name}")
            btn.clicked.connect(lambda checked, n=name: self.switch_page(n))
            layout.addWidget(btn)
        
        return frame
    
    def create_system_info_frame(self):
        """創建系統信息框架"""
        frame = QFrame()
        frame.setObjectName("systemInfoFrame")
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(5)
        
        # 版本信息
        version_label = QLabel("版本: v2.0.0")
        version_label.setObjectName("versionLabel")
        
        # 連接狀態
        self.connection_label = QLabel("🔴 離線模式")
        self.connection_label.setObjectName("connectionLabel")
        
        # 更新按鈕
        update_button = QPushButton("🔄 檢查更新")
        update_button.setObjectName("updateButton")
        update_button.clicked.connect(self.check_updates)
        
        layout.addWidget(version_label)
        layout.addWidget(self.connection_label)
        layout.addWidget(update_button)
        
        return frame
    
    def create_content_area(self):
        """創建內容區域"""
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("contentStack")
        
        # 遊戲庫頁面
        games_page = self.create_games_page()
        self.content_stack.addWidget(games_page)
        
        # 其他頁面（暫時使用佔位符）
        for page_name in ["虛擬商店", "成就系統", "統計資料", "設置", "AI客服"]:
            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_layout.addWidget(QLabel(f"{page_name} - 功能開發中..."))
            self.content_stack.addWidget(placeholder)
        
        return self.content_stack
    
    def create_games_page(self):
        """創建遊戲頁面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 頁面標題
        title_label = QLabel("🎮 遊戲庫")
        title_label.setObjectName("pageTitle")
        
        # 搜索欄
        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_layout = QHBoxLayout(search_frame)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索遊戲...")
        self.search_input.setObjectName("searchInput")
        
        search_button = QPushButton("🔍")
        search_button.setObjectName("searchButton")
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        
        # 遊戲網格滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("gamesScrollArea")
        
        self.games_container = QWidget()
        self.games_layout = QGridLayout(self.games_container)
        self.games_layout.setSpacing(25)
        self.games_layout.setContentsMargins(20, 20, 20, 20)
        
        scroll_area.setWidget(self.games_container)
        
        layout.addWidget(title_label)
        layout.addWidget(search_frame)
        layout.addWidget(scroll_area)
        
        return page
    
    def load_default_games(self):
        """載入預設遊戲"""
        if not self.games_data:
            # 如果沒有外部傳入的遊戲資料，使用預設資料
            self.games_data = [
                {
                    "id": 1,
                    "name": "幸運輪盤",
                    "description": "經典賭場遊戲，轉動輪盤贏取獎勵",
                    "category": "casino",
                    "min_bet": 10,
                    "max_bet": 1000
                },
                {
                    "id": 2,
                    "name": "百家樂",
                    "description": "經典撲克遊戲，體驗真實賭場氛圍",
                    "category": "casino",
                    "min_bet": 50,
                    "max_bet": 5000
                },
                # ... 其他遊戲
            ]
        self.refresh_games_display()
    
    def refresh_games_display(self):
        """刷新遊戲顯示"""
        # 清除現有遊戲卡片
        while self.games_layout.count():
            item = self.games_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加新遊戲卡片
        row = 0
        col = 0
        max_cols = 4
        
        for game in self.games_data:
            card = EnhancedGameCard(game, self)
            self.games_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def launch_game(self, game_data):
        """啟動遊戲"""
        print(f"🎮 啟動遊戲: {game_data['name']}")
        QMessageBox.information(self, "遊戲啟動", f"正在啟動 {game_data['name']}")
    
    def handle_login_logout(self):
        """處理登入/登出"""
        if self.current_user:
            # 登出
            self.current_user = None
            self.username_label.setText("遊客")
            self.points_label.setText("積分: 0")
            self.login_button.setText("🔑 登入")
        else:
            # 登入（這裡可以整合你的登入系統）
            QMessageBox.information(self, "登入", "登入功能整合中...")
    
    def switch_page(self, page_name):
        """切換頁面"""
        page_mapping = {
            "gameLibrary": 0,
            "virtualStore": 1,
            "achievements": 2,
            "statistics": 3,
            "settings": 4,
            "customerService": 5
        }
        
        if page_name in page_mapping:
            self.content_stack.setCurrentIndex(page_mapping[page_name])
    
    def check_updates(self):
        """檢查更新"""
        QMessageBox.information(self, "更新檢查", "正在檢查更新...")
    
    def load_styles(self):
        """載入樣式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            
            QWidget {
                color: #ffffff;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
            }
            
            #sidebar {
                background-color: #2d2d2d;
                border-right: 2px solid #3d3d3d;
            }
            
            #appTitle {
                font-size: 24px;
                font-weight: bold;
                color: #ffd700;
                margin: 10px 0;
            }
            
            #userInfoFrame {
                background-color: #363636;
                border-radius: 15px;
                padding: 20px;
                border: 2px solid #4a4a4a;
            }
            
            #avatar {
                background-color: #4a4a4a;
                border: 3px solid #5a5a5a;
                border-radius: 50px;
                font-size: 36px;
            }
            
            #username {
                font-size: 18px;
                font-weight: bold;
                margin: 10px 0;
            }
            
            #points {
                font-size: 16px;
                color: #ffd700;
                margin: 5px 0;
            }
            
            QPushButton {
                background-color: #363636;
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                color: #ffffff;
                text-align: left;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background-color: #4a4a4a;
                border-color: #5a5a5a;
            }
            
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            
            #loginButton {
                background-color: #4CAF50;
                text-align: center;
                font-weight: bold;
            }
            
            #loginButton:hover {
                background-color: #45a049;
            }
            
            #pageTitle {
                font-size: 28px;
                font-weight: bold;
                color: #ffd700;
                margin-bottom: 20px;
            }
            
            #searchFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
            }
            
            #searchInput {
                background-color: #363636;
                border: 2px solid #4a4a4a;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            
            #enhancedGameCard {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 15px;
                margin: 10px;
            }
            
            #enhancedGameCard:hover {
                border-color: #ffd700;
                background-color: #363636;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EnhancedMainWindow()
    window.show()
    sys.exit(app.exec_())