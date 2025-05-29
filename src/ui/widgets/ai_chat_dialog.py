from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from ...core.logger import get_logger

logger = get_logger(__name__)

class AIChatDialog(QDialog):
    """AI 客服對話框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI 客服小幫手")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        
    def setup_ui(self):
        """設置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 聊天記錄區域
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setObjectName("chatArea")
        
        chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(chat_widget)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setAlignment(Qt.AlignTop)
        
        self.chat_area.setWidget(chat_widget)
        
        # 輸入區域
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.message_input = QTextEdit()
        self.message_input.setObjectName("chatInput")
        self.message_input.setPlaceholderText("輸入您的問題...")
        self.message_input.setMaximumHeight(100)
        
        self.send_button = QPushButton("發送")
        self.send_button.setObjectName("sendButton")
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        # 添加到主布局
        layout.addWidget(self.chat_area)
        layout.addWidget(input_widget)
        
        # 添加歡迎消息
        self.add_ai_message("您好！我是 AI 客服小幫手，有什麼可以幫您的嗎？")
        
    def add_user_message(self, message: str):
        """添加用戶消息"""
        message_widget = QWidget()
        message_layout = QHBoxLayout(message_widget)
        message_layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(message)
        label.setObjectName("userMessage")
        label.setWordWrap(True)
        label.setTextFormat(Qt.PlainText)
        
        message_layout.addStretch()
        message_layout.addWidget(label)
        
        self.chat_layout.addWidget(message_widget)
        self.scroll_to_bottom()
        
    def add_ai_message(self, message: str):
        """添加 AI 消息"""
        message_widget = QWidget()
        message_layout = QHBoxLayout(message_widget)
        message_layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(message)
        label.setObjectName("aiMessage")
        label.setWordWrap(True)
        label.setTextFormat(Qt.PlainText)
        
        message_layout.addWidget(label)
        message_layout.addStretch()
        
        self.chat_layout.addWidget(message_widget)
        self.scroll_to_bottom()
        
    def send_message(self):
        """發送消息"""
        message = self.message_input.toPlainText().strip()
        if not message:
            return
            
        # 清空輸入框
        self.message_input.clear()
        
        # 添加用戶消息
        self.add_user_message(message)
        
        # 模擬 AI 回應
        QTimer.singleShot(1000, lambda: self.simulate_ai_response(message))
        
    def simulate_ai_response(self, message: str):
        """模擬 AI 回應"""
        # TODO: 實現真實的 AI 回應邏輯
        response = "我收到了您的消息：" + message + "\n\n這是一個模擬的回應。"
        self.add_ai_message(response)
        
    def scroll_to_bottom(self):
        """滾動到底部"""
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )
        
    def keyPressEvent(self, event):
        """按鍵事件"""
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            self.send_message()
        else:
            super().keyPressEvent(event) 