from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal
from typing import Dict

class ResultWindow(QDialog):
    """結果窗口"""
    
    continue_clicked = pyqtSignal()  # 繼續按鈕信號
    
    def __init__(self, result: Dict, parent=None):
        super().__init__(parent)
        self.result = result
        self.setWindowTitle("遊戲結果")
        self.setup_ui()
        
    def setup_ui(self):
        """設置UI"""
        layout = QVBoxLayout()
        
        # 結果顯示
        result_label = QLabel()
        if self.result.get("won", False):
            result_label.setText(f"恭喜獲勝！\n贏得 {self.result.get('win_amount', 0)} 點")
        else:
            result_label.setText("很遺憾，這次沒有獲勝")
        layout.addWidget(result_label)
        
        # 按鈕
        button_layout = QHBoxLayout()
        continue_button = QPushButton("繼續")
        continue_button.clicked.connect(self.continue_game)
        button_layout.addWidget(continue_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def continue_game(self):
        """繼續遊戲"""
        self.continue_clicked.emit()
        self.accept()
        
    def get_result(self) -> Dict:
        """獲取結果"""
        return self.result 