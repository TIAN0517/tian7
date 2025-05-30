from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QTextEdit, QProgressBar,
    QTabWidget, QGridLayout, QLineEdit, QMessageBox, QGroupBox,
    QSlider, QSplitter, QListWidget, QListWidgetItem, QSpacerItem, QSizePolicy, QComboBox
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap, QMovie
from pathlib import Path
import sys
import os
from datetime import datetime
from .tabs.home_tab import HomeTab
from .tabs.casino_tab import CasinoTab
from .tabs.market_tab import MarketTab
from .tabs.recharge_tab import RechargeTab
from .tabs.ranking_tab import RankingTab
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from src.games.game_data import ALL_GAMES_INFO
import pyodbc

logger = None  # 簡化版本

class GameEmpireMainWindow(QMainWindow):
    """🎮 Jy技術團隊 遊戲帝國 v3.0.0 主視窗"""
    
    # 信號定義
    game_launched = pyqtSignal(str)  # 遊戲啟動信號
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎮 Jy技術團隊 遊戲帝國 v3.0.0 - Gaming Empire")
        self.setFixedSize(1100, 700)
        
        # 設置窗口屬性
        self.setWindowFlags(Qt.Window)
        
        # 用戶數據
        self.current_user = {
            'username': 'TIAN0517',
            'credits': 10000.0,
            'vip_level': 5,
            'total_games': 247,
            'achievements': 18
        }
        
        # 遊戲數據
        self.games_data = self.load_games_data()
        
        # 存儲遊戲窗口引用
        self.game_windows = {}
        
        # 初始化組件
        self.init_ui()
        self.load_styles()
        self.setup_timers()
        
        # 將自己設為全局引用
        if hasattr(sys, 'app'):
            sys.main_window = self
        
    def load_games_data(self):
        """載入24款遊戲數據"""
        return {
            # 賭場類 (8款)
            'casino': [
                {'id': 'lucky_wheel', 'name': '🎡 幸運輪盤', 'desc': '數字、顏色、奇偶下注', 'hot': True},
                {'id': 'baccarat', 'name': '🃏 百家樂', 'desc': '莊家vs閒家經典對戰', 'hot': True},
                {'id': 'blackjack', 'name': '♠️ 二十一點', 'desc': '與莊家比大小', 'hot': False},
                {'id': 'slot_machine', 'name': '🎰 老虎機', 'desc': '3x3網格多線獎勵', 'hot': True},
                {'id': 'russian_roulette', 'name': '🔫 俄羅斯輪盤', 'desc': '高風險高回報', 'hot': False},
                {'id': 'fruit_slots', 'name': '🍎 水果老虎機', 'desc': '水果主題老虎機', 'hot': False},
                {'id': 'quick_21', 'name': '⚡ 快速21點', 'desc': '簡化版21點遊戲', 'hot': False},
                {'id': 'sic_bo', 'name': '🎲 骰寶', 'desc': '三骰子大小單雙', 'hot': True}
            ],
            # 撲克類 (4款)
            'poker': [
                {'id': 'texas_holdem', 'name': '🤠 德州撲克', 'desc': '2+5張牌經典撲克', 'hot': True},
                {'id': 'five_card_poker', 'name': '🃏 五張牌撲克', 'desc': '經典撲克換牌', 'hot': False},
                {'id': 'stud_poker', 'name': '🎴 梭哈', 'desc': '5張牌比大小', 'hot': False},
                {'id': 'golden_flower', 'name': '🌸 炸金花', 'desc': '中式3張牌撲克', 'hot': True}
            ],
            # 技巧類 (6款)
            'skill': [
                {'id': 'mahjong', 'name': '🀄 麻將', 'desc': '簡化版麻將胡牌', 'hot': True},
                {'id': 'fishing', 'name': '🐠 捕魚遊戲', 'desc': '瞄準射擊得分', 'hot': True},
                {'id': 'fruit_ninja', 'name': '🥝 水果忍者', 'desc': '切水果避炸彈', 'hot': False},
                {'id': 'guess_number', 'name': '🔢 猜數字', 'desc': '邏輯推理遊戲', 'hot': False},
                {'id': 'deep_sea_fishing', 'name': '🌊 深海捕魚', 'desc': '深海捕魚冒險', 'hot': False},
                {'id': 'fruit_master', 'name': '🍓 切水果大師', 'desc': '水果忍者增強版', 'hot': True}
            ],
            # 骰子類 (2款)
            'dice': [
                {'id': 'quick_dice', 'name': '🎲 快速骰子', 'desc': '骰寶簡化版', 'hot': False},
                {'id': 'dice_guess', 'name': '🎯 骰子單雙', 'desc': '預測骰子結果', 'hot': False}
            ],
            # 彩票類 (2款)
            'lottery': [
                {'id': 'lottery', 'name': '🎫 彩票', 'desc': '選號中獎系統', 'hot': False},
                {'id': 'k3_lottery', 'name': '⚡ 快3彩票', 'desc': '快速彩票遊戲', 'hot': True}
            ],
            # 休閒類 (1款)
            'casual': [
                {'id': 'coin_flip', 'name': '🪙 拋硬幣', 'desc': '正反面預測', 'hot': False}
            ]
        }
        
    def init_ui(self):
        """初始化UI組件（重構為分頁Tab設計）"""
        self.setFixedSize(950, 650)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # 頂部用戶信息欄
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        # 分頁TabWidget
        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setStyleSheet("QTabBar::tab { min-width: 120px; min-height: 36px; margin: 0 8px; font-size: 16px; font-weight: 700; } QTabBar::tab:selected { background: #FFD700; color: #23243a; }")
        main_layout.addWidget(self.tabs, 1)

        # 首頁Tab
        self.tabs.addTab(self.create_home_tab(), "🏠 首頁")
        # Casino專頁
        self.tabs.addTab(self.create_casino_tab(), "🎰 賭場系統")
        # 拍賣場專頁
        self.tabs.addTab(self.create_auction_tab(), "🏆 拍賣場")
        # USDT充值專頁
        self.tabs.addTab(self.create_usdt_tab(), "💵 USDT充值")
        # 排行榜專頁
        self.tabs.addTab(self.create_rank_tab(), "🏅 排行榜")

    def create_home_tab(self):
        """首頁：現代化卡片設計風格"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(25)
        layout.setContentsMargins(25, 25, 25, 25)

        # 頂部歡迎區域
        welcome_section = QFrame()
        welcome_section.setFixedHeight(120)
        welcome_section.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                           stop:0 rgba(255,215,0,0.15), stop:1 rgba(143,211,244,0.15));
                border: 2px solid #FFD700;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        
        welcome_layout = QHBoxLayout(welcome_section)
        welcome_layout.setSpacing(20)
        
        # 左側歡迎文字
        welcome_text_layout = QVBoxLayout()
        welcome_title = QLabel("🎮 歡迎來到 Jy技術團隊 遊戲帝國")
        welcome_title.setStyleSheet("""
            font-size: 24px; 
            font-weight: 900; 
            color: #FFD700;
            margin: 0px;
        """)
        
        welcome_desc = QLabel("24款精品遊戲 • 企業級安全 • 7x24客服支持")
        welcome_desc.setStyleSheet("""
            font-size: 14px; 
            color: #8fd3f4;
            margin: 5px 0px;
        """)
        
        user_info = QLabel(f"👋 {self.current_user['username']} | 💰 {self.current_user['credits']:,.0f} 積分 | 👑 VIP {self.current_user['vip_level']}")
        user_info.setStyleSheet("""
            font-size: 16px; 
            font-weight: 700;
            color: #e0e0e0;
            margin: 5px 0px;
        """)
        
        welcome_text_layout.addWidget(welcome_title)
        welcome_text_layout.addWidget(welcome_desc)
        welcome_text_layout.addWidget(user_info)
        welcome_text_layout.addStretch()
        
        # 右側快速動作
        quick_actions = QHBoxLayout()
        quick_actions.setSpacing(15)
        
        casino_btn = QPushButton("🎰\n賭場")
        casino_btn.setFixedSize(80, 70)
        casino_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px; 
                font-weight: 700;
                border-radius: 15px; 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: 2px solid #e74c3c;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ec7063, stop:1 #e74c3c);
            }
        """)
        casino_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        
        market_btn = QPushButton("🏆\n拍賣場")
        market_btn.setFixedSize(80, 70)
        market_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px; 
                font-weight: 700;
                border-radius: 15px; 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f39c12, stop:1 #e67e22);
                color: white;
                border: 2px solid #f39c12;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8c471, stop:1 #f39c12);
            }
        """)
        market_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        
        recharge_btn = QPushButton("💰\nUSDT")
        recharge_btn.setFixedSize(80, 70)
        recharge_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px; 
                font-weight: 700;
                border-radius: 15px; 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2ecc71, stop:1 #27ae60);
                color: white;
                border: 2px solid #2ecc71;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #58d68d, stop:1 #2ecc71);
            }
        """)
        recharge_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(3))
        
        quick_actions.addWidget(casino_btn)
        quick_actions.addWidget(market_btn)
        quick_actions.addWidget(recharge_btn)
        
        welcome_layout.addLayout(welcome_text_layout, 1)
        welcome_layout.addLayout(quick_actions)
        
        layout.addWidget(welcome_section)

        # 主要內容區域
        content_layout = QHBoxLayout()
        content_layout.setSpacing(25)

        # 左側：遊戲預告片區域
        left_section = QVBoxLayout()
        left_section.setSpacing(20)

        # 影片播放器
        video_card = QFrame()
        video_card.setStyleSheet("""
            QFrame {
                background: rgba(30,40,60,0.8);
                border: 2px solid #8fd3f4;
                border-radius: 20px;
                padding: 15px;
            }
        """)
        video_layout = QVBoxLayout(video_card)
        video_layout.setSpacing(15)
        
        video_title = QLabel("🎬 遊戲預告片")
        video_title.setStyleSheet("""
            font-size: 18px; 
            font-weight: 800; 
            color: #8fd3f4;
            text-align: center;
        """)
        video_title.setAlignment(Qt.AlignCenter)
        video_layout.addWidget(video_title)

        self.home_video_player = QMediaPlayer()
        self.home_video_widget = QVideoWidget()
        self.home_video_player.setVideoOutput(self.home_video_widget)
        self.home_video_widget.setFixedSize(450, 250)
        self.home_video_widget.setStyleSheet("""
            QVideoWidget {
                border: 2px solid #FFD700;
                border-radius: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                           stop:0 #23243a, stop:1 #2c3e50);
            }
        """)
        video_layout.addWidget(self.home_video_widget, alignment=Qt.AlignCenter)

        # 預告片選擇器
        self.current_trailer_index = 0
        self.trailer_videos = [
            {"title": "🎮 RanOnline 經典回歸", "path": "assets/videos/ran1.mp4"},
            {"title": "⚔️ 全新PVP戰鬥系統", "path": "assets/videos/ran2.mp4"},
            {"title": "🏰 豐富副本等你探索", "path": "assets/videos/ran3.mp4"},
            {"title": "👑 公會戰爭即將開啟", "path": "assets/videos/trailer1.mp4"},
            {"title": "🆕 全新職業搶先體驗", "path": "assets/videos/trailer2.mp4"},
            {"title": "💎 頂級裝備等你來拿", "path": "assets/videos/trailer3.mp4"}
        ]
        
        trailer_control = QFrame()
        trailer_control.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.05);
                border: 1px solid #8fd3f4;
                border-radius: 15px;
                padding: 12px;
            }
        """)
        control_layout = QHBoxLayout(trailer_control)
        control_layout.setSpacing(10)
        
        self.trailer_title_label = QLabel(self.trailer_videos[0]["title"])
        self.trailer_title_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: 700; 
            color: #FFD700;
        """)
        
        prev_btn = QPushButton("⬅️")
        prev_btn.setFixedSize(40, 35)
        prev_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                border-radius: 17px; 
                background: rgba(143, 211, 244, 0.3);
                color: #8fd3f4;
                border: 1px solid #8fd3f4;
            }
            QPushButton:hover {
                background: rgba(143, 211, 244, 0.6);
            }
        """)
        prev_btn.clicked.connect(self.prev_trailer)
        
        play_btn = QPushButton("▶️")
        play_btn.setFixedSize(45, 35)
        play_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                border-radius: 17px; 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFD700, stop:1 #f1c40f);
                color: #23243a;
                border: 2px solid #FFD700;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #ffe066;
            }
        """)
        play_btn.clicked.connect(self.play_current_trailer)
        
        next_btn = QPushButton("➡️")
        next_btn.setFixedSize(40, 35)
        next_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                border-radius: 17px; 
                background: rgba(143, 211, 244, 0.3);
                color: #8fd3f4;
                border: 1px solid #8fd3f4;
            }
            QPushButton:hover {
                background: rgba(143, 211, 244, 0.6);
            }
        """)
        next_btn.clicked.connect(self.next_trailer)
        
        control_layout.addWidget(self.trailer_title_label, 1)
        control_layout.addWidget(prev_btn)
        control_layout.addWidget(play_btn)
        control_layout.addWidget(next_btn)
        
        video_layout.addWidget(trailer_control)
        left_section.addWidget(video_card)

        # 右側：公告和主遊戲
        right_section = QVBoxLayout()
        right_section.setSpacing(20)

        # 公告區域
        announcement_card = QFrame()
        announcement_card.setFixedHeight(280)
        announcement_card.setStyleSheet("""
            QFrame {
                background: rgba(30,40,60,0.8);
                border: 2px solid #FFD700;
                border-radius: 20px;
                padding: 15px;
            }
        """)
        
        ann_layout = QVBoxLayout(announcement_card)
        ann_layout.setSpacing(12)
        
        ann_title = QLabel("📢 最新公告")
        ann_title.setStyleSheet("""
            font-size: 18px; 
            font-weight: 800; 
            color: #FFD700;
            text-align: center;
        """)
        ann_title.setAlignment(Qt.AlignCenter)
        ann_layout.addWidget(ann_title)
        
        announcements = [
            {"title": "🎉 遊戲帝國v3.0正式上線", "content": "24款精品遊戲等你體驗"},
            {"title": "🎴 百家樂遊戲現已開放", "content": "真實賭場體驗，立即遊玩"},
            {"title": "💰 USDT充值系統升級", "content": "支援TRC20/ERC20/BEP20"},
            {"title": "🏆 每日登入送好禮", "content": "連續登入獲得更多獎勵"}
        ]
        
        for ann in announcements:
            ann_item = QFrame()
            ann_item.setFixedHeight(45)
            ann_item.setStyleSheet("""
                QFrame {
                    background: rgba(255,255,255,0.08);
                    border: 1px solid #8fd3f4;
                    border-radius: 10px;
                    padding: 8px;
                    margin: 2px;
                }
                QFrame:hover {
                    background: rgba(255,215,0,0.1);
                    border: 1px solid #FFD700;
                }
            """)
            
            ann_item_layout = QVBoxLayout(ann_item)
            ann_item_layout.setSpacing(2)
            ann_item_layout.setContentsMargins(10, 5, 10, 5)
            
            title = QLabel(ann["title"])
            title.setStyleSheet("font-size: 13px; font-weight: 700; color: #FFD700;")
            ann_item_layout.addWidget(title)
            
            content = QLabel(ann["content"])
            content.setStyleSheet("font-size: 11px; color: #e0e0e0;")
            ann_item_layout.addWidget(content)
            
            ann_layout.addWidget(ann_item)
        
        right_section.addWidget(announcement_card)

        # 主遊戲按鈕
        main_game_card = QFrame()
        main_game_card.setFixedHeight(150)
        main_game_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                           stop:0 rgba(255,215,0,0.2), stop:1 rgba(241,196,15,0.2));
                border: 3px solid #FFD700;
                border-radius: 20px;
                padding: 20px;
            }
        """)
        
        main_game_layout = QVBoxLayout(main_game_card)
        main_game_layout.setSpacing(15)
        
        main_game_title = QLabel("🚀 主遊戲入口")
        main_game_title.setStyleSheet("""
            font-size: 18px; 
            font-weight: 800; 
            color: #FFD700;
            text-align: center;
        """)
        main_game_title.setAlignment(Qt.AlignCenter)
        main_game_layout.addWidget(main_game_title)
        
        main_btn = QPushButton("進入主遊戲")
        main_btn.setFixedHeight(60)
        main_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px; 
                font-weight: 800; 
                border-radius: 15px; 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFD700, stop:1 #f1c40f); 
                color: #23243a;
                border: 3px solid #FFD700;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffe066, stop:1 #FFD700);
            }
            QPushButton:pressed {
                background: #e67e22;
            }
        """)
        main_btn.clicked.connect(lambda: self.launch_game('main_game'))
        main_game_layout.addWidget(main_btn)
        
        right_section.addWidget(main_game_card)

        content_layout.addLayout(left_section, 3)
        content_layout.addLayout(right_section, 2)
        
        layout.addLayout(content_layout)
        return widget
    
    def prev_trailer(self):
        """上一個預告片"""
        self.current_trailer_index = (self.current_trailer_index - 1) % len(self.trailer_videos)
        self.update_trailer_display()
    
    def next_trailer(self):
        """下一個預告片"""
        self.current_trailer_index = (self.current_trailer_index + 1) % len(self.trailer_videos)
        self.update_trailer_display()
    
    def update_trailer_display(self):
        """更新預告片顯示"""
        current = self.trailer_videos[self.current_trailer_index]
        self.trailer_title_label.setText(current["title"])
    
    def play_current_trailer(self):
        """播放當前預告片"""
        current = self.trailer_videos[self.current_trailer_index]
        self.play_home_video(current["path"])

    def play_home_video(self, video_path):
        """播放首頁預告片"""
        from PyQt5.QtCore import QUrl
        from PyQt5.QtMultimedia import QMediaContent
        self.home_video_player.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(video_path))))
        self.home_video_player.play()

    def create_casino_tab(self):
        """Casino專頁，動態顯示24款遊戲卡片"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 標題
        title = QLabel("娛樂城遊戲")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFD700; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 創建滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.1);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #FFD700;
                border-radius: 6px;
                min-height: 20px;
            }
        """)
        
        # 滾動內容容器
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_layout.setSpacing(20)
        
        # 遊戲卡片網格 - 每行3個
        grid = QGridLayout()
        grid.setSpacing(25)  # 增加間距
        grid.setContentsMargins(15, 15, 15, 15)
        
        for idx, game in enumerate(ALL_GAMES_INFO):
            card = QFrame()
            card.setObjectName("gameCard")
            card.setFixedSize(280, 160)  # 增大卡片尺寸
            card.setStyleSheet("""
                QFrame#gameCard {
                    background: rgba(30,40,60,0.85);
                    border: 3px solid #8fd3f4;
                    border-radius: 15px;
                    margin: 5px;
                    padding: 15px;
                }
                QFrame#gameCard:hover {
                    border: 3px solid #FFD700;
                    background: rgba(255,255,255,0.15);
                }
            """)
            
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 10, 12, 10)
            card_layout.setSpacing(8)
            
            # 遊戲圖標
            icon = QLabel(game["icon"])
            icon.setAlignment(Qt.AlignCenter)
            icon.setStyleSheet("font-size: 42px; margin-bottom: 5px;")
            card_layout.addWidget(icon)
            
            # 遊戲名稱
            name = QLabel(game["name"])
            name.setAlignment(Qt.AlignCenter)
            name.setStyleSheet("""
                font-size: 18px; 
                font-weight: 800; 
                color: #FFD700;
                margin: 3px 0px;
                text-align: center;
                line-height: 1.2;
            """)
            name.setWordWrap(True)
            card_layout.addWidget(name)
            
            # 遊戲描述
            desc = QLabel(game["description"])
            desc.setAlignment(Qt.AlignCenter)
            desc.setStyleSheet("""
                font-size: 14px; 
                color: #e0e0e0;
                margin: 2px 0px;
                text-align: center;
                line-height: 1.1;
            """)
            desc.setWordWrap(True)
            card_layout.addWidget(desc)
            
            # 進入遊戲按鈕
            btn = QPushButton("進入遊戲")
            btn.setFixedHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 16px; 
                    font-weight: 700;
                    border-radius: 10px; 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8fd3f4, stop:1 #5dade2);
                    color: #23243a;
                    border: 2px solid #8fd3f4;
                    margin-top: 5px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFD700, stop:1 #f1c40f);
                    border: 2px solid #FFD700;
                    color: #23243a;
                }
                QPushButton:pressed {
                    background: #e67e22;
                }
            """)
            btn.clicked.connect(lambda checked, gid=game["id"]: self.launch_game(gid))
            card_layout.addWidget(btn)
            
            # 每行3個卡片
            row = idx // 3
            col = idx % 3
            grid.addWidget(card, row, col)
        
        scroll_layout.addLayout(grid)
        scroll_layout.addStretch(1)
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        return widget

    def create_auction_tab(self):
        """拍賣場專頁，連接資料庫顯示物品"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # 標題
        title = QLabel("主遊戲拍賣場（數據庫同步）")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFD700; margin-bottom: 15px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 連接資料庫查詢物品
        try:
            conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=RanUser;UID=sa;PWD=your_password")
            cursor = conn.cursor()
            cursor.execute("SELECT TOP 10 ItemName, Price FROM AuctionItems ORDER BY Price DESC")
            items = cursor.fetchall()
        except Exception as e:
            items = [
                ("神聖武器 +15", 15000), ("稀有裝備 +12", 8500), ("傳說戒指 +10", 6200),
                ("黃金盔甲 +8", 4800), ("鑽石項鍊 +6", 3500), ("魔法法杖 +7", 2900),
                ("精靈弓箭 +9", 2100), ("龍鱗盾牌 +5", 1800), ("祝福卷軸 x10", 1200), ("經驗藥水 x50", 800)
            ]
        
        # 創建滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.1);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #FFD700;
                border-radius: 6px;
            }
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(15, 15, 15, 15)
        scroll_layout.setSpacing(12)
        
        for name, price in items:
            card = QFrame()
            card.setObjectName("auctionCard")
            card.setFixedHeight(90)
            card.setStyleSheet("""
                QFrame#auctionCard {
                    background: rgba(30,40,60,0.8);
                    border: 2px solid #8fd3f4;
                    border-radius: 12px;
                    margin: 3px;
                    padding: 12px;
                }
                QFrame#auctionCard:hover {
                    border: 3px solid #FFD700;
                    background: rgba(255,255,255,0.1);
                }
            """)
            
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(15, 10, 15, 10)
            card_layout.setSpacing(15)
            
            # 物品圖標
            icon = QLabel("💎")
            icon.setFixedSize(50, 50)
            icon.setAlignment(Qt.AlignCenter)
            icon.setStyleSheet("font-size: 24px; background: rgba(255,215,0,0.2); border-radius: 8px; border: 2px solid #FFD700;")
            card_layout.addWidget(icon)
            
            # 物品名稱
            name_label = QLabel(str(name))
            name_label.setStyleSheet("font-size: 18px; font-weight: 800; color: #8fd3f4; line-height: 1.2;")
            card_layout.addWidget(name_label)
            
            card_layout.addStretch(1)
            
            # 價格
            price_label = QLabel(f"當前價: {price:,} 積分")
            price_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFD700; margin-right: 10px;")
            card_layout.addWidget(price_label)
            
            # 出價按鈕
            bid_btn = QPushButton("出價")
            bid_btn.setFixedSize(80, 35)
            bid_btn.setStyleSheet("""
                QPushButton {
                    font-size: 15px; 
                    font-weight: 700;
                    border-radius: 8px; 
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFD700, stop:1 #f1c40f);
                    color: #23243a;
                    border: 2px solid #FFD700;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffe066, stop:1 #FFD700);
                }
            """)
            bid_btn.clicked.connect(lambda checked, n=name: QMessageBox.information(self, "出價", f"你對 {n} 出價成功！（模擬）"))
            card_layout.addWidget(bid_btn)
            
            scroll_layout.addWidget(card)
        
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        return widget

    def create_usdt_tab(self):
        """USDT充值專頁（表單+API模擬）"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        # 標題
        title = QLabel("USDT 充值系統")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #FFD700; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 表單容器
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background: rgba(30,40,60,0.7);
                border: 3px solid #8fd3f4;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        form_container.setFixedWidth(500)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(20)
        
        # 網絡選擇
        network_label = QLabel("選擇網絡：")
        network_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFD700; margin-bottom: 5px;")
        form_layout.addWidget(network_label)
        
        network_combo = QComboBox()
        network_combo.addItems(["TRC20", "ERC20", "BEP20"])
        network_combo.setFixedHeight(45)
        network_combo.setStyleSheet("""
            QComboBox {
                font-size: 16px;
                font-weight: 600;
                padding: 8px 12px;
                border: 2px solid #8fd3f4;
                border-radius: 8px;
                background: rgba(255,255,255,0.9);
                color: #23243a;
            }
            QComboBox:hover {
                border: 2px solid #FFD700;
            }
        """)
        form_layout.addWidget(network_combo)
        
        # 金額輸入
        amount_label = QLabel("充值金額：")
        amount_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFD700; margin-bottom: 5px;")
        form_layout.addWidget(amount_label)
        
        amount_input = QLineEdit()
        amount_input.setPlaceholderText("請輸入USDT金額")
        amount_input.setFixedHeight(45)
        amount_input.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                font-weight: 600;
                padding: 8px 12px;
                border: 2px solid #8fd3f4;
                border-radius: 8px;
                background: rgba(255,255,255,0.9);
                color: #23243a;
            }
            QLineEdit:focus {
                border: 2px solid #FFD700;
            }
        """)
        form_layout.addWidget(amount_input)
        
        # 充值按鈕
        recharge_btn = QPushButton("立即充值")
        recharge_btn.setFixedSize(150, 55)
        recharge_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px; 
                font-weight: 800;
                border-radius: 12px; 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #8fd3f4, stop:1 #5dade2);
                color: #23243a;
                border: 3px solid #8fd3f4;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFD700, stop:1 #f1c40f);
                border: 3px solid #FFD700;
            }
        """)
        recharge_btn.clicked.connect(lambda: QMessageBox.information(self, "充值", f"充值成功！（模擬）\n網絡：{network_combo.currentText()}\n金額：{amount_input.text()} USDT"))
        form_layout.addWidget(recharge_btn, alignment=Qt.AlignCenter)
        
        layout.addWidget(form_container, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        return widget

    def create_rank_tab(self):
        """排行榜專頁（查詢真實數據）"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 標題
        title = QLabel("積分排行榜")
        title.setStyleSheet("font-size: 26px; font-weight: 800; color: #FFD700; margin-bottom: 15px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 連接資料庫查詢排行榜
        try:
            conn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=RanUser;UID=sa;PWD=your_password")
            cursor = conn.cursor()
            cursor.execute("SELECT TOP 10 UserName, Points FROM RanUser ORDER BY Points DESC")
            rows = cursor.fetchall()
        except Exception as e:
            rows = [
                ("TIAN0517", 50000), ("遊戲大師", 45000), ("黃金玩家", 38000), ("鑽石會員", 32000), ("白金玩家", 28000),
                ("精英玩家", 25000), ("高級會員", 22000), ("資深玩家", 18000), ("普通會員", 15000), ("新手玩家", 12000)
            ]
        
        # 排行榜容器
        rank_container = QFrame()
        rank_container.setStyleSheet("""
            QFrame {
                background: rgba(30,40,60,0.6);
                border: 3px solid #FFD700;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        rank_layout = QVBoxLayout(rank_container)
        rank_layout.setSpacing(12)
        
        for i, (name, points) in enumerate(rows):
            rank_item = QFrame()
            rank_item.setFixedHeight(65)
            rank_item.setStyleSheet("""
                QFrame {
                    background: rgba(255,255,255,0.05);
                    border: 2px solid #8fd3f4;
                    border-radius: 10px;
                    margin: 2px;
                }
                QFrame:hover {
                    background: rgba(255,255,255,0.1);
                    border: 2px solid #FFD700;
                }
            """)
            
            item_layout = QHBoxLayout(rank_item)
            item_layout.setContentsMargins(20, 10, 20, 10)
            
            # 排名
            rank_num = QLabel(f"NO.{i+1}")
            if i < 3:  # 前三名特殊顏色
                colors = ["#FFD700", "#C0C0C0", "#CD7F32"]  # 金、銀、銅
                rank_num.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {colors[i]}; min-width: 80px;")
            else:
                rank_num.setStyleSheet("font-size: 18px; font-weight: 700; color: #8fd3f4; min-width: 80px;")
            item_layout.addWidget(rank_num)
            
            # 玩家名稱
            player_name = QLabel(str(name))
            player_name.setStyleSheet("font-size: 18px; font-weight: 700; color: #e0e0e0;")
            item_layout.addWidget(player_name)
            
            item_layout.addStretch(1)
            
            # 積分
            score = QLabel(f"{points:,} 積分")
            score.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFD700;")
            item_layout.addWidget(score)
            
            rank_layout.addWidget(rank_item)
        
        layout.addWidget(rank_container)
        layout.addStretch(1)
        return widget

    def create_top_bar(self) -> QWidget:
        """創建頂部用戶信息欄"""
        widget = QWidget()
        widget.setObjectName("topBar")
        widget.setFixedHeight(80)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # 左側：平台標題
        title_area = QHBoxLayout()
        
        logo_label = QLabel("🎮")
        logo_label.setObjectName("logoIcon")
        logo_label.setFixedSize(60, 60)
        
        title_info = QVBoxLayout()
        platform_name = QLabel("Jy技術團隊 遊戲帝國")
        platform_name.setObjectName("platformName")
        
        version_label = QLabel("Gaming Empire v3.0.0")
        version_label.setObjectName("versionLabel")
        
        title_info.addWidget(platform_name)
        title_info.addWidget(version_label)
        
        title_area.addWidget(logo_label)
        title_area.addLayout(title_info)
        
        # 中間：搜索框
        search_area = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setObjectName("searchInput")
        search_input.setPlaceholderText("🔍 搜索遊戲...")
        search_input.setFixedWidth(300)
        
        search_btn = QPushButton("搜索")
        search_btn.setObjectName("searchButton")
        
        search_area.addWidget(search_input)
        search_area.addWidget(search_btn)
        
        # 右側：用戶信息
        user_area = QHBoxLayout()
        
        # 用戶頭像
        avatar_label = QLabel("👤")
        avatar_label.setObjectName("userAvatar")
        avatar_label.setFixedSize(50, 50)
        
        # 用戶信息
        user_info = QVBoxLayout()
        username_label = QLabel(f"👋 {self.current_user['username']}")
        username_label.setObjectName("username")
        
        credits_label = QLabel(f"💰 {self.current_user['credits']:,.0f} 積分")
        credits_label.setObjectName("userCredits")
        
        user_info.addWidget(username_label)
        user_info.addWidget(credits_label)
        
        # VIP等級
        vip_label = QLabel(f"👑 VIP {self.current_user['vip_level']}")
        vip_label.setObjectName("vipLevel")
        
        # 設置按鈕
        settings_btn = QPushButton("⚙️")
        settings_btn.setObjectName("settingsButton")
        settings_btn.setFixedSize(40, 40)
        settings_btn.clicked.connect(self.open_settings)
        
        user_area.addWidget(avatar_label)
        user_area.addLayout(user_info)
        user_area.addWidget(vip_label)
        user_area.addWidget(settings_btn)
        
        layout.addLayout(title_area)
        layout.addStretch()
        layout.addLayout(search_area)
        layout.addStretch()
        layout.addLayout(user_area)
        
        return widget
        
    def create_status_bar(self):
        """創建底部狀態欄"""
        status_bar = self.statusBar()
        
        # 在線狀態
        online_label = QLabel("🟢 在線")
        status_bar.addWidget(online_label)
        
        # 遊戲統計
        games_count = sum(len(games) for games in self.games_data.values())
        stats_label = QLabel(f"�� {games_count}款遊戲 | 👥 1,247在線用戶")
        status_bar.addPermanentWidget(stats_label)
        
        # 版本信息
        version_label = QLabel("v3.0.0 - Powered by Jy技術團隊")
        status_bar.addPermanentWidget(version_label)
        
    def darken_color(self, color: str) -> str:
        """加深顏色"""
        color_map = {
            "#E74C3C": "#C0392B",
            "#3498DB": "#2980B9", 
            "#2ECC71": "#27AE60",
            "#F39C12": "#E67E22",
            "#9B59B6": "#8E44AD",
            "#1ABC9C": "#16A085"
        }
        return color_map.get(color, color)
        
    def lighten_color(self, color: str) -> str:
        """加亮顏色"""
        color_map = {
            "#E74C3C": "#EC7063",
            "#3498DB": "#5DADE2",
            "#2ECC71": "#58D68D", 
            "#F39C12": "#F8C471",
            "#9B59B6": "#BB8FCE",
            "#1ABC9C": "#48C9B0"
        }
        return color_map.get(color, color)
        
    def setup_timers(self):
        """設置定時器"""
        # 公告滾動定時器
        # self.announcement_timer = QTimer()
        # self.announcement_timer.timeout.connect(self.scroll_announcements)
        # self.announcement_timer.start(5000)  # 每5秒滾動一次
        
    def scroll_announcements(self):
        """滾動公告"""
        # current_row = self.announcements_list.currentRow()
        # next_row = (current_row + 1) % self.announcements_list.count()
        # self.announcements_list.setCurrentRow(next_row)
        pass
        
    def launch_game(self, game_id: str):
        """啟動遊戲"""
        if game_id == "casino_suite":
            # 啟動原有的賭場套件
            try:
                from .widgets.game_window import GameWindow
                self.game_window = GameWindow()
                self.game_windows[game_id] = self.game_window
                self.game_window.show()
                self.hide()  # 隱藏主窗口
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"無法啟動賭場套件：{str(e)}")
        elif game_id == "baccarat":
            # 啟動百家樂遊戲
            try:
                from .widgets.baccarat_widget import BaccaratWidget
                baccarat_game = BaccaratWidget(self)
                self.game_windows[game_id] = baccarat_game
                baccarat_game.exec_()
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"無法啟動百家樂遊戲：{str(e)}")
        elif game_id == "main_game":
            # 啟動主遊戲
            QMessageBox.information(self, "主遊戲", "主遊戲即將開放，敬請期待！\n\n🎮 目前可體驗：\n• 百家樂遊戲已上線\n• 更多遊戲正在開發中...")
        else:
            # 其他遊戲彈出模板視窗或啟動對應遊戲
            game_info = self.get_game_info(game_id)
            if game_info:
                # 檢查是否有對應的遊戲實作
                if game_id in ["roulette", "blackjack", "texas_holdem"]:
                    QMessageBox.information(self, "遊戲開發中", f"🎮 {game_info['name']}\n\n該遊戲正在開發中，即將上線！\n敬請期待更多精彩內容。")
                else:
                    from .widgets.base_game_widget import BaseGameWidget
                    dlg = BaseGameWidget(game_info['name'], game_info['desc'], self)
                    dlg.exec_()
            else:
                QMessageBox.information(self, "遊戲啟動", f"即將啟動遊戲：{game_id}\n\n功能開發中，敬請期待！")
        
        # 發射遊戲啟動信號
        self.game_launched.emit(game_id)
        
    def get_game_info(self, game_id: str):
        """獲取遊戲信息"""
        for category, games in self.games_data.items():
            for game in games:
                if game['id'] == game_id:
                    game['category'] = category
                    return game
        return None
        
    def get_category_name(self, category: str) -> str:
        """獲取分類名稱"""
        category_names = {
            'casino': '🎰 賭場類',
            'poker': '🃏 撲克類', 
            'skill': '🎯 技巧類',
            'dice': '🎲 骰子類',
            'lottery': '🎫 彩票類',
            'casual': '🎪 休閒類'
        }
        return category_names.get(category, '🎮 其他')
        
    def open_settings(self):
        """打開設置"""
        QMessageBox.information(self, "設置", "系統設置功能即將推出！\n\n可設置項目：\n- 音效設置\n- 顯示設置\n- 帳戶設置\n- 遊戲偏好")
        
    def show_more_announcements(self):
        """顯示更多公告"""
        QMessageBox.information(
            self, "公告中心", 
            "📢 Jy技術團隊遊戲帝國公告中心\n\n"
            "🎮 平台功能：\n"
            "- 24款精品遊戲\n"
            "- 完整用戶系統\n"
            "- 積分管理\n"
            "- VIP特權\n\n"
            "🔧 技術支持：\n"
            "- 7x24小時在線客服\n"
            "- 專業技術團隊\n"
            "- 定期功能更新\n\n"
            "📞 聯絡我們：support@jytech.com"
        )
        
    def show_launcher(self):
        """顯示啟動器（從遊戲返回時調用）"""
        self.show()
        
    def load_styles(self):
        """載入樣式表"""
        self.setStyleSheet("""
        QMainWindow, QWidget {
            font-family: 'Noto Sans TC', 'Microsoft JhengHei', 'Arial', 'sans-serif';
        }
        QMainWindow {
            background: qradialgradient(cx:0.5, cy:0.3, radius:1.0, fx:0.5, fy:0.3, stop:0 #23243a, stop:0.5 #181c24, stop:1 #101018),
                        qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #23243a, stop:1 #181c24);
        }
        #topBar {
            background: rgba(30,40,60,0.92);
            border-bottom: 0px;
            border-radius: 0px 0px 22px 22px;
            box-shadow: 0 6px 32px 0 #FFD70040, 0 1.5px 0 #FFD700 inset;
            outline: 2.5px solid #FFD70080;
            outline-offset: -2px;
        }
        #logoIcon {
            font-size: 40px;
            border-radius: 18px;
            border: 2.5px solid #FFD700;
            background: rgba(255,255,255,0.10);
            box-shadow: 0 2px 12px #FFD70040;
        }
        #platformName {
            font-size: 28px;
            font-weight: 800;
            color: #FFD700;
            text-shadow: 0 2px 16px #000, 0 0 16px #FFD700;
        }
        #versionLabel {
            font-size: 15px;
            color: #8fd3f4;
            font-weight: 600;
            text-shadow: 0 1px 8px #000;
        }
        #searchInput {
            padding: 8px 16px;
            border: 2.5px solid #FFD700;
            border-radius: 20px;
            font-size: 14px;
            background: rgba(255,255,255,0.90);
            color: #23243a;
        }
        #searchButton {
            padding: 8px 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFD700, stop:1 #f1c40f);
            color: #23243a;
            border: none;
            border-radius: 16px;
            font-weight: bold;
            font-size: 14px;
            box-shadow: 0 2px 12px #FFD70080;
        }
        #searchButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ffe066, stop:1 #FFD700);
            color: #181c24;
        }
        #userAvatar {
            font-size: 30px;
            border: 2.5px solid #FFD700;
            border-radius: 18px;
            background: rgba(255,255,255,0.14);
            padding: 2px;
            box-shadow: 0 2px 12px #FFD70040;
        }
        #username {
            font-size: 16px;
            font-weight: 700;
            color: #FFD700;
            text-shadow: 0 2px 12px #000, 0 0 12px #FFD700;
        }
        #userCredits {
            font-size: 15px;
            color: #8fd3f4;
            font-weight: 600;
            text-shadow: 0 1px 8px #000;
        }
        #vipLevel {
            font-size: 15px;
            font-weight: 700;
        }
        #settingsButton {
            background: rgba(255,255,255,0.14);
            border: 2px solid #FFD700;
            border-radius: 16px;
            color: #FFD700;
            font-size: 16px;
            box-shadow: 0 2px 12px #FFD70040;
        }
        #settingsButton:hover {
            background: #FFD700;
            color: #23243a;
        }
        QGroupBox {
            font-size: 18px;
            font-weight: 700;
            color: #FFD700;
            border: 2.5px solid #FFD70080;
            border-radius: 16px;
            margin: 12px 2px;
            padding-top: 18px;
            background: rgba(30,40,60,0.72);
            box-shadow: 0 2px 20px #FFD70020;
        }
        QGroupBox::title {
            font-size: 17px;
            font-weight: 800;
            color: #FFD700;
            text-shadow: 0 2px 16px #000, 0 0 16px #FFD700;
        }
        #announcementsList {
            background: rgba(255,255,255,0.90);
            border: 2px solid #FFD70080;
            border-radius: 10px;
            font-size: 14px;
            color: #23243a;
            padding: 6px;
        }
        #trailerCard {
            background: rgba(52, 152, 219, 0.22);
            border: 2.5px solid #8fd3f4;
            border-radius: 12px;
            padding: 12px;
            margin: 6px 0px;
            box-shadow: 0 2px 16px #8fd3f480;
        }
        #trailerTitle {
            font-size: 15px;
            font-weight: bold;
            color: #8fd3f4;
            text-shadow: 0 2px 12px #000, 0 0 12px #8fd3f4;
        }
        #trailerDesc {
            font-size: 13px;
            color: #e0e0e0;
            line-height: 1.2;
            text-shadow: 0 1px 6px #000;
        }
        #trailerDate {
            font-size: 12px;
            color: #FFD700;
        }
        #mainGameButton {
            font-size: 18px;
            font-weight: 700;
            text-shadow: 0 2px 12px #000, 0 0 12px #FFD700;
        }
        QFrame#gameCard {
            min-width: 220px;
            max-width: 270px;
            min-height: 130px;
            max-height: 170px;
            margin: 6px;
            padding: 14px;
            background: rgba(30,40,60,0.65);
            border: 2.5px solid #8fd3f4;
            border-radius: 20px;
            box-shadow: 0 2px 20px #8fd3f480;
            transition: all 0.2s;
        }
        QFrame#gameCard:hover {
            border: 3.5px solid #FFD700;
            background: rgba(255,255,255,0.13);
            box-shadow: 0 4px 32px #FFD70080;
        }
        #gameName {
            font-size: 17px;
            font-weight: 700;
            color: #FFD700;
            text-shadow: 0 2px 16px #000, 0 0 16px #FFD700;
        }
        #gameDesc {
            font-size: 15px;
            font-weight: 500;
            color: #e0e0e0;
            text-shadow: 0 1px 8px #000;
        }
        #hotLabel {
            font-size: 13px;
            font-weight: 700;
        }
        #launchButton, #moreButton {
            font-size: 16px;
            font-weight: 700;
            text-shadow: 0 1px 8px #000;
        }
        QTabWidget::pane {
            border: 2.5px solid #FFD70080;
            border-radius: 14px;
            background: rgba(30,40,60,0.45);
            box-shadow: 0 2px 20px #FFD70020;
        }
        QTabBar::tab {
            font-size: 15px;
            font-weight: 700;
            text-shadow: 0 2px 12px #000, 0 0 12px #FFD700;
        }
        QTabBar::tab:selected {
            font-size: 16px;
            font-weight: 800;
        }
        QStatusBar {
            font-size: 14px;
            font-weight: 600;
        }
        /* 全局彈窗與小視窗美化 */
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
        """ )
        
    def closeEvent(self, event):
        """關閉窗口事件"""
        reply = QMessageBox.question(
            self, "確認退出",
            "確定要退出 Jy技術團隊遊戲帝國 嗎？\n\n您的遊戲數據已自動保存。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

# 為了向後兼容，保留原來的類名
MainWindow = GameEmpireMainWindow 