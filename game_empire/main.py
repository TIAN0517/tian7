import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow
from utils.music_player import MusicPlayer
from utils.sound_utils import SoundManager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    # 啟動主視窗
    main_win = MainWindow(player_points=10000)
    main_win.show()
    # 啟動背景音樂
    main_win.music = MusicPlayer("assets/music/lobby_theme.mp3")
    # 初始化音效管理器
    main_win.sound_mgr = SoundManager()
    sys.exit(app.exec_()) 