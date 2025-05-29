import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QScrollArea, QFrame, QStackedWidget,
                            QGridLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtSvg import QSvgWidget
from virtual_store import VirtualStoreWindow

class GameCard(QFrame):
    def __init__(self, game_data, parent=None):
        super().__init__(parent)
        self.game_data = game_data
        self.setup_ui()
    
    def setup_ui(self):
        self.setObjectName("gameCard")
        self.setFixedSize(200, 250)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 遊戲圖標
        icon_label = QLabel()
        icon_label.setFixedSize(100, 100)
        icon_label.setObjectName("gameIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        # TODO: 加載實際圖標
        icon_label.setStyleSheet("background-color: #2d2d2d; border-radius: 50px;")
        
        # 遊戲名稱
        name_label = QLabel(self.game_data["name"])
        name_label.setObjectName("gameName")
        name_label.setAlignment(Qt.AlignCenter)
        
        # 遊戲描述
        desc_label = QLabel(self.game_data["description"])
        desc_label.setObjectName("gameDescription")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        
        # 啟動按鈕
        launch_button = QPushButton("啟動遊戲")
        launch_button.setObjectName("launchButton")
        launch_button.clicked.connect(self.handle_launch)
        
        layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        layout.addWidget(name_label)
        layout.addWidget(desc_label)
        layout.addWidget(launch_button)
    
    def handle_launch(self):
        # 找到主視窗實例
        main_window = self.window()
        if isinstance(main_window, MainWindow):
            main_window.launch_game(self.game_data)

class MainWindow(QMainWindow):
    def __init__(self, user_manager):
        super().__init__()
        self.user_manager = user_manager
        self.setup_ui()
        self.load_games()
    
    def setup_ui(self):
        self.setWindowTitle("遊戲啟動器")
        self.setMinimumSize(1200, 800)
        
        # 創建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主佈局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左側邊欄
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(20)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        
        # 用戶信息
        user_info = QFrame()
        user_info.setObjectName("userInfo")
        user_layout = QVBoxLayout(user_info)
        
        avatar_label = QLabel()
        avatar_label.setFixedSize(80, 80)
        avatar_label.setObjectName("avatar")
        avatar_label.setAlignment(Qt.AlignCenter)
        # TODO: 加載用戶頭像
        avatar_label.setStyleSheet("background-color: #2d2d2d; border-radius: 40px;")
        
        username_label = QLabel("用戶名")
        username_label.setObjectName("username")
        username_label.setAlignment(Qt.AlignCenter)
        
        points_label = QLabel("積分: 0")
        points_label.setObjectName("points")
        points_label.setAlignment(Qt.AlignCenter)
        
        user_layout.addWidget(avatar_label, alignment=Qt.AlignCenter)
        user_layout.addWidget(username_label)
        user_layout.addWidget(points_label)
        
        # 導航按鈕
        nav_buttons = {
            "遊戲庫": "gameLibrary",
            "虛擬物品": "virtualStore",
            "成就": "achievements",
            "設置": "settings",
            "客服": "customerService"
        }
        
        for text, name in nav_buttons.items():
            btn = QPushButton(text)
            btn.setObjectName(name)
            btn.clicked.connect(lambda checked, n=name: self.switch_page(n))
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addWidget(user_info)
        sidebar_layout.addStretch()
        
        # 右側內容區域
        self.contentArea = QStackedWidget()
        self.contentArea.setObjectName("contentArea")
        
        # 遊戲庫頁面
        game_library = QWidget()
        game_layout = QVBoxLayout(game_library)
        
        # 搜索欄
        search_bar = QFrame()
        search_bar.setObjectName("searchBar")
        search_layout = QHBoxLayout(search_bar)
        
        search_label = QLabel("搜索遊戲")
        search_label.setObjectName("searchLabel")
        
        search_layout.addWidget(search_label)
        search_layout.addStretch()
        
        # 遊戲網格
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("gameScrollArea")
        
        self.games_widget = QWidget()
        self.games_layout = QGridLayout(self.games_widget)
        self.games_layout.setSpacing(20)
        
        scroll_area.setWidget(self.games_widget)
        
        game_layout.addWidget(search_bar)
        game_layout.addWidget(scroll_area)
        
        # 虛擬商店頁面
        virtual_store = QWidget()
        virtual_store.setObjectName("virtualStorePage")
        virtual_store_layout = QVBoxLayout(virtual_store)
        virtual_store_layout.addWidget(QLabel("功能開發中..."))
        
        # 成就頁面
        achievements = QWidget()
        achievements.setObjectName("achievementsPage")
        achievements_layout = QVBoxLayout(achievements)
        achievements_layout.addWidget(QLabel("功能開發中..."))
        
        # 設置頁面
        settings = QWidget()
        settings.setObjectName("settingsPage")
        settings_layout = QVBoxLayout(settings)
        settings_layout.addWidget(QLabel("功能開發中..."))
        
        # 客服頁面
        customer_service = QWidget()
        customer_service.setObjectName("customerServicePage")
        customer_service_layout = QVBoxLayout(customer_service)
        customer_service_layout.addWidget(QLabel("功能開發中..."))
        
        # 添加所有頁面到堆疊部件
        self.contentArea.addWidget(game_library)
        self.contentArea.addWidget(virtual_store)
        self.contentArea.addWidget(achievements)
        self.contentArea.addWidget(settings)
        self.contentArea.addWidget(customer_service)
        
        # 添加側邊欄和內容區域到主佈局
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.contentArea)
        
        # 設置樣式
        self.load_styles()
    
    def load_games(self):
        """從數據庫加載遊戲"""
        # TODO: 從數據庫加載遊戲
        # 臨時使用測試數據
        test_games = [
            {
                "id": 1,
                "name": "幸運輪盤",
                "description": "經典賭場遊戲，轉動輪盤贏取獎勵",
                "version": "1.0.0",
                "executable": "games/lucky_wheel.exe"
            },
            {
                "id": 2,
                "name": "百家樂",
                "description": "經典撲克遊戲，體驗真實賭場氛圍",
                "version": "1.0.0",
                "executable": "games/baccarat.exe"
            },
            {
                "id": 3,
                "name": "21點",
                "description": "挑戰莊家，測試你的運氣和策略",
                "version": "1.0.0",
                "executable": "games/blackjack.exe"
            },
            {
                "id": 4,
                "name": "老虎機",
                "description": "簡單刺激的老虎機遊戲",
                "version": "1.0.0",
                "executable": "games/slot_machine.exe"
            },
            {
                "id": 5,
                "name": "骰寶",
                "description": "經典骰子遊戲，猜測點數贏取獎勵",
                "version": "1.0.0",
                "executable": "games/dice_game.exe"
            },
            {
                "id": 6,
                "name": "德州撲克",
                "description": "策略性撲克遊戲，與其他玩家對戰",
                "version": "1.0.0",
                "executable": "games/texas_holdem.exe"
            }
        ]
        self.display_games(test_games)
    
    def display_games(self, games):
        """顯示遊戲列表"""
        # 清除現有遊戲
        while self.games_layout.count():
            item = self.games_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 添加新遊戲
        row = 0
        col = 0
        max_cols = 4
        
        for game in games:
            card = GameCard(game, self)
            self.games_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def switch_page(self, page_name):
        """切換頁面"""
        if page_name == "gameLibrary":
            self.contentArea.setCurrentIndex(0)
        elif page_name == "virtualStore":
            self.contentArea.setCurrentIndex(1)
        elif page_name == "achievements":
            self.contentArea.setCurrentIndex(2)
        elif page_name == "settings":
            self.contentArea.setCurrentIndex(3)
        elif page_name == "customerService":
            self.contentArea.setCurrentIndex(4)
    
    def launch_game(self, game_data):
        """啟動遊戲"""
        # TODO: 實現遊戲啟動邏輯
        print(f"啟動遊戲: {game_data['name']}")
    
    def load_styles(self):
        """加載樣式表"""
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
                border-right: 1px solid #3d3d3d;
            }
            
            #userInfo {
                background-color: #363636;
                border-radius: 10px;
                padding: 10px;
            }
            
            #avatar {
                background-color: #4a4a4a;
                border: 2px solid #5a5a5a;
            }
            
            #username {
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            
            #points {
                font-size: 14px;
                color: #ffd700;
            }
            
            QPushButton {
                background-color: #363636;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                color: #ffffff;
            }
            
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            
            #gameLibrary, #virtualStore, #achievements, #settings, #customerService {
                min-height: 40px;
                text-align: left;
                padding-left: 20px;
            }
            
            #contentArea {
                background-color: #1a1a1a;
            }
            
            #searchBar {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 10px;
                margin: 10px;
            }
            
            #searchLabel {
                font-size: 14px;
                color: #888888;
            }
            
            #gameScrollArea {
                border: none;
                background-color: transparent;
            }
            
            #gameCard {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
            }
            
            #gameIcon {
                background-color: #363636;
                border-radius: 50px;
            }
            
            #gameName {
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            
            #gameDescription {
                font-size: 12px;
                color: #888888;
                margin: 5px 0;
            }
            
            #launchButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            
            #launchButton:hover {
                background-color: #45a049;
            }
            
            #launchButton:pressed {
                background-color: #3d8b40;
            }
        """)

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from database import UserManager
    
    app = QApplication(sys.argv)
    user_manager = UserManager()
    window = MainWindow(user_manager)
    window.show()
    sys.exit(app.exec_()) 