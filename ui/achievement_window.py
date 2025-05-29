from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QScrollArea, QFrame
from PyQt5.QtCore import Qt
from typing import List, Dict

class AchievementWindow(QMainWindow):
    """成就窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("成就")
        self.setup_ui()
        
    def setup_ui(self):
        """設置UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 成就列表
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.achievement_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
    def update_achievements(self, achievements: List[Dict]):
        """更新成就列表"""
        # 清除現有成就
        while self.achievement_layout.count():
            item = self.achievement_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # 添加新成就
        for achievement in achievements:
            achievement_frame = QFrame()
            achievement_frame.setFrameStyle(QFrame.StyledPanel)
            frame_layout = QVBoxLayout(achievement_frame)
            
            # 成就名稱和描述
            name_label = QLabel(achievement["name"])
            name_label.setStyleSheet("font-weight: bold;")
            desc_label = QLabel(achievement["description"])
            frame_layout.addWidget(name_label)
            frame_layout.addWidget(desc_label)
            
            # 進度條
            progress_layout = QHBoxLayout()
            progress_label = QLabel("進度:")
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(int(achievement.get("progress", 0) * 100))
            progress_layout.addWidget(progress_label)
            progress_layout.addWidget(progress_bar)
            frame_layout.addLayout(progress_layout)
            
            # 獎勵點數
            points_label = QLabel(f"獎勵: {achievement['points']} 點")
            frame_layout.addWidget(points_label)
            
            # 解鎖時間（如果已解鎖）
            if "unlocked_at" in achievement:
                unlock_label = QLabel(f"解鎖時間: {achievement['unlocked_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                frame_layout.addWidget(unlock_label)
                
            self.achievement_layout.addWidget(achievement_frame)
            
        # 添加彈性空間
        self.achievement_layout.addStretch()
        
    def update_achievement_progress(self, achievement_id: str, progress: float):
        """更新成就進度"""
        for i in range(self.achievement_layout.count()):
            frame = self.achievement_layout.itemAt(i).widget()
            if isinstance(frame, QFrame):
                # 查找對應的進度條
                for j in range(frame.layout().count()):
                    item = frame.layout().itemAt(j)
                    if isinstance(item, QHBoxLayout):
                        progress_bar = item.itemAt(1).widget()
                        if isinstance(progress_bar, QProgressBar):
                            progress_bar.setValue(int(progress * 100))
                            break 