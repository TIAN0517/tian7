from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
import re
from ...core.auth import Auth
from ...core.logger import get_logger

logger = get_logger(__name__)

class RegisterDialog(QDialog):
    """註冊對話框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("註冊新帳號")
        self.setMinimumSize(500, 400)
        self.setup_ui()
        
    def setup_ui(self):
        """設置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 標題
        title = QLabel("創建新帳號")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 用戶名輸入
        username_layout = QHBoxLayout()
        username_label = QLabel("用戶名：")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("請輸入用戶名（3-20個字符）")
        self.username_input.textChanged.connect(self.validate_username)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # 用戶名提示
        self.username_hint = QLabel("")
        self.username_hint.setObjectName("hint")
        layout.addWidget(self.username_hint)
        
        # 密碼輸入
        password_layout = QHBoxLayout()
        password_label = QLabel("密碼：")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("請輸入密碼（至少8位，包含大小寫字母和數字）")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.validate_password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # 密碼提示
        self.password_hint = QLabel("")
        self.password_hint.setObjectName("hint")
        layout.addWidget(self.password_hint)
        
        # 確認密碼
        confirm_layout = QHBoxLayout()
        confirm_label = QLabel("確認密碼：")
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("請再次輸入密碼")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.textChanged.connect(self.validate_confirm_password)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        layout.addLayout(confirm_layout)
        
        # 確認密碼提示
        self.confirm_hint = QLabel("")
        self.confirm_hint.setObjectName("hint")
        layout.addWidget(self.confirm_hint)
        
        # 註冊按鈕
        self.register_button = QPushButton("註冊")
        self.register_button.setObjectName("registerButton")
        self.register_button.clicked.connect(self.handle_register)
        self.register_button.setEnabled(False)
        layout.addWidget(self.register_button)
        
        # 返回登錄按鈕
        back_button = QPushButton("返回登錄")
        back_button.setObjectName("backButton")
        back_button.clicked.connect(self.reject)
        layout.addWidget(back_button)
        
        # 進度條（用於郵箱驗證）
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("verifyProgress")
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
    def validate_username(self) -> bool:
        """驗證用戶名"""
        username = self.username_input.text().strip()
        if not username:
            self.username_hint.setText("用戶名不能為空")
            self.username_hint.setStyleSheet("color: #e94560;")
            return False
            
        if len(username) < 3:
            self.username_hint.setText("用戶名長度不能小於3個字符")
            self.username_hint.setStyleSheet("color: #e94560;")
            return False
            
        if len(username) > 20:
            self.username_hint.setText("用戶名長度不能超過20個字符")
            self.username_hint.setStyleSheet("color: #e94560;")
            return False
            
        if not username.isalnum():
            self.username_hint.setText("用戶名只能包含字母和數字")
            self.username_hint.setStyleSheet("color: #e94560;")
            return False
            
        # 檢查用戶名是否已存在
        if Auth.check_username_exists(username):
            self.username_hint.setText("用戶名已存在")
            self.username_hint.setStyleSheet("color: #e94560;")
            return False
            
        self.username_hint.setText("用戶名可用")
        self.username_hint.setStyleSheet("color: #4CAF50;")
        return True
        
    def validate_password(self) -> bool:
        """驗證密碼"""
        password = self.password_input.text()
        if not password:
            self.password_hint.setText("密碼不能為空")
            self.password_hint.setStyleSheet("color: #e94560;")
            return False
            
        if len(password) < 8:
            self.password_hint.setText("密碼長度必須至少8位")
            self.password_hint.setStyleSheet("color: #e94560;")
            return False
            
        if not re.search(r'[A-Z]', password):
            self.password_hint.setText("密碼必須包含大寫字母")
            self.password_hint.setStyleSheet("color: #e94560;")
            return False
            
        if not re.search(r'[a-z]', password):
            self.password_hint.setText("密碼必須包含小寫字母")
            self.password_hint.setStyleSheet("color: #e94560;")
            return False
            
        if not re.search(r'\d', password):
            self.password_hint.setText("密碼必須包含數字")
            self.password_hint.setStyleSheet("color: #e94560;")
            return False
            
        self.password_hint.setText("密碼強度良好")
        self.password_hint.setStyleSheet("color: #4CAF50;")
        return True
        
    def validate_confirm_password(self) -> bool:
        """驗證確認密碼"""
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if not confirm:
            self.confirm_hint.setText("請確認密碼")
            self.confirm_hint.setStyleSheet("color: #e94560;")
            return False
            
        if password != confirm:
            self.confirm_hint.setText("兩次輸入的密碼不一致")
            self.confirm_hint.setStyleSheet("color: #e94560;")
            return False
            
        self.confirm_hint.setText("密碼確認成功")
        self.confirm_hint.setStyleSheet("color: #4CAF50;")
        return True
        
    def update_register_button(self):
        """更新註冊按鈕狀態"""
        is_valid = (
            self.validate_username() and
            self.validate_password() and
            self.validate_confirm_password()
        )
        self.register_button.setEnabled(is_valid)
        
    def handle_register(self):
        """處理註冊"""
        if not self.register_button.isEnabled():
            return
        try:
            # 收集註冊信息
            username = self.username_input.text().strip()
            password = self.password_input.text()
            # 不再收集 email
            # 顯示進度條
            self.progress_bar.show()
            self.progress_bar.setValue(0)
            # 模擬郵箱驗證過程
            self.verify_timer = QTimer()
            self.verify_timer.timeout.connect(self.update_verify_progress)
            self.verify_timer.start(100)
            # 註冊用戶（不傳 email）
            if Auth.register(username, password, None):
                QMessageBox.information(self, "註冊成功", "帳號註冊成功！")
                self.accept()
            else:
                QMessageBox.warning(self, "註冊失敗", "註冊失敗，請稍後重試")
        except Exception as e:
            logger.error(f"註冊失敗: {str(e)}")
            QMessageBox.critical(self, "錯誤", f"註冊失敗：{str(e)}")
            
    def update_verify_progress(self):
        """更新郵箱驗證進度"""
        current = self.progress_bar.value()
        if current < 100:
            self.progress_bar.setValue(current + 10)
        else:
            self.verify_timer.stop()
            self.progress_bar.hide()
            
    def keyPressEvent(self, event):
        """按鍵事件"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event) 