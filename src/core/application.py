import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from src.ui.main_window import MainWindow

class RanOnlineApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setup_application()
        
    def setup_application(self):
        """設置應用程式全局配置"""
        # 設置應用程式樣式
        self.app.setStyle('Fusion')
        
        # 設置全局字體
        font = self.app.font()
        font.setFamily("'Noto Sans TC', 'Microsoft JhengHei', 'PingFang TC', 'Helvetica Neue', Arial, sans-serif")
        self.app.setFont(font)
        
        # 設置高DPI支持
        self.app.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
    def run(self):
        """運行應用程式"""
        window = MainWindow()
        window.show()
        return self.app.exec_()

if __name__ == '__main__':
    app = RanOnlineApp()
    sys.exit(app.run()) 