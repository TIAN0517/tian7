from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer, QRect, QSize, QUrl
from PyQt5.QtGui import QPixmap, QColor, QFont, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os

class HomeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 影片清單
        self.video_list = [
            'assets/videos/ran1.mp4',
            'assets/videos/ran2.mp4',
            'assets/videos/ran3.mp4',
            'assets/videos/trailer1.mp4',
            'assets/videos/trailer2.mp4',
            'assets/videos/trailer3.mp4',
        ]
        self.current_video_index = 0
        self.is_muted = True
        self.setup_ui()
        self.init_animations()
        self.setup_video_autoplay()
        
    def setup_ui(self):
        """設置主遊戲首頁UI"""
        # 創建主佈局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 創建影片播放器
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumHeight(400)
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background-color: #0a0a0a;
                border: none;
            }
        """)
        
        # 設置影片播放器
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setMuted(self.is_muted)
        
        # 創建控制按鈕
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(20, 10, 20, 10)
        
        # 播放按鈕
        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon("assets/icons/play.png"))
        self.play_button.setIconSize(QSize(32, 32))
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
        """)
        self.play_button.clicked.connect(self.toggle_play)
        
        # 音量控制
        self.volume_button = QPushButton()
        self.volume_button.setIcon(QIcon("assets/icons/volume.png"))
        self.volume_button.setIconSize(QSize(32, 32))
        self.volume_button.setStyleSheet(self.play_button.styleSheet())
        self.volume_button.clicked.connect(self.toggle_mute)
        
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.volume_button)
        controls_layout.addStretch()
        
        # 輪播切換按鈕
        self.prev_button = QPushButton("上一部")
        self.next_button = QPushButton("下一部")
        self.prev_button.setFixedHeight(36)
        self.next_button.setFixedHeight(36)
        self.prev_button.setStyleSheet("background:#23243a;color:#FFD700;border-radius:8px;font-size:16px;")
        self.next_button.setStyleSheet("background:#23243a;color:#FFD700;border-radius:8px;font-size:16px;")
        self.prev_button.clicked.connect(self.play_prev_video)
        self.next_button.clicked.connect(self.play_next_video)
        switch_layout = QHBoxLayout()
        switch_layout.addStretch()
        switch_layout.addWidget(self.prev_button)
        switch_layout.addWidget(self.next_button)
        switch_layout.addStretch()
        
        # 添加影片和控制到主佈局
        main_layout.addWidget(self.video_widget)
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(switch_layout)
        
        # 創建公告區域
        self.create_announcement_area(main_layout)
        
        # 設置背景
        self.setStyleSheet("""
            QWidget {
                background-color: #0a0a0a;
                color: #ffffff;
            }
        """)
        
    def create_announcement_area(self, parent_layout):
        """創建公告區域"""
        announcement_frame = QFrame()
        announcement_frame.setStyleSheet("""
            QFrame {
                background-color: #1a2238;
                border-radius: 10px;
                margin: 20px;
            }
        """)
        
        announcement_layout = QVBoxLayout(announcement_frame)
        
        # 公告標題
        title = QLabel("最新公告")
        title.setFont(QFont("'Noto Sans TC', 'Microsoft JhengHei'", 16, QFont.Bold))
        title.setStyleSheet("color: #FFD700;")
        announcement_layout.addWidget(title)
        
        # 公告內容
        content = QLabel("歡迎來到 RanOnline！\n\n"
                        "1. 新版本更新：全新職業系統上線\n"
                        "2. 限時活動：雙倍經驗值\n"
                        "3. 新地圖開放：神秘森林")
        content.setFont(QFont("'Noto Sans TC', 'Microsoft JhengHei'", 12))
        content.setStyleSheet("color: #ffffff;")
        content.setWordWrap(True)
        announcement_layout.addWidget(content)
        
        parent_layout.addWidget(announcement_frame)
        
    def setup_video_autoplay(self):
        # 載入第一部影片
        self.set_video_source(self.video_list[self.current_video_index])
        self.media_player.play()
        # 自動輪播定時器
        self.video_timer = QTimer(self)
        self.video_timer.timeout.connect(self.play_next_video)
        self.video_timer.start(30000)  # 30秒自動切換
        # 影片播完自動切換
        self.media_player.mediaStatusChanged.connect(self.handle_media_status)
    def handle_media_status(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.play_next_video()
    def play_prev_video(self):
        self.current_video_index = (self.current_video_index - 1) % len(self.video_list)
        self.set_video_source(self.video_list[self.current_video_index])
        self.media_player.play()
        self.update_play_button()
        self.video_timer.start(30000)
    def play_next_video(self):
        self.current_video_index = (self.current_video_index + 1) % len(self.video_list)
        self.set_video_source(self.video_list[self.current_video_index])
        self.media_player.play()
        self.update_play_button()
        self.video_timer.start(30000)
    def set_video_source(self, video_path):
        if not os.path.exists(video_path):
            return
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(video_path))))
        self.update_play_button()
    def toggle_play(self):
        """切換影片播放狀態"""
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
            self.update_play_button()
        else:
            self.media_player.play()
            self.update_play_button()
    def update_play_button(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(QIcon("assets/icons/pause.png"))
        else:
            self.play_button.setIcon(QIcon("assets/icons/play.png"))
    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.media_player.setMuted(self.is_muted)
        if self.is_muted:
            self.volume_button.setIcon(QIcon("assets/icons/volume.png"))
        else:
            self.volume_button.setIcon(QIcon("assets/icons/volume-on.png"))
        
    def init_animations(self):
        """初始化動畫效果"""
        # LOGO發光效果
        self.logo_glow = QGraphicsDropShadowEffect()
        self.logo_glow.setColor(QColor(255, 215, 0, 180))
        self.logo_glow.setBlurRadius(20)
        if hasattr(self, 'logo_label'):
            self.logo_label.setGraphicsEffect(self.logo_glow)
        
        # 公告滾動動畫
        self.announcement_timer = QTimer()
        self.announcement_timer.timeout.connect(self.update_announcement)
        self.announcement_timer.start(3000)  # 每3秒更新一次
        
    def update_announcement(self):
        """更新公告內容"""
        announcements = [
            "歡迎來到 RanOnline！",
            "新版本更新：新增世界BOSS系統",
            "公會戰報名開始，請盡快報名！",
            "限時活動：雙倍經驗值進行中"
        ]
        
        if hasattr(self, 'announcement_label'):
            current_text = self.announcement_label.text()
            current_index = announcements.index(current_text) if current_text in announcements else -1
            next_index = (current_index + 1) % len(announcements)
            self.announcement_label.setText(announcements[next_index]) 