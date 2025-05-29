from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon
from ...core.auth import Auth
from ...core.logger import get_logger
from .register_dialog import RegisterDialog

logger = get_logger(__name__)

class LoginDialog(QDialog):
    """登錄對話框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("登錄")
        self.setMinimumSize(400, 300)
        self.setup_ui()
        self.load_saved_credentials()
        
    def setup_ui(self):
        """設置 UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 標題
        title = QLabel("歡迎登錄")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 用戶名輸入
        username_layout = QHBoxLayout()
        username_label = QLabel("用戶名：")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("請輸入用戶名")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # 密碼輸入
        password_layout = QHBoxLayout()
        password_label = QLabel("密碼：")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("請輸入密碼")
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # 記住我選項
        remember_layout = QHBoxLayout()
        self.remember_checkbox = QCheckBox("記住我")
        remember_layout.addStretch()
        remember_layout.addWidget(self.remember_checkbox)
        layout.addLayout(remember_layout)
        
        # 按鈕區域
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("登錄")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.handle_login)
        
        self.register_button = QPushButton("註冊")
        self.register_button.setObjectName("registerButton")
        self.register_button.clicked.connect(self.show_register)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        layout.addLayout(button_layout)
        
        # 設置回車鍵觸發登錄
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)
        
    def load_saved_credentials(self):
        """加載保存的憑證"""
        settings = QSettings("N.L.Online", "GameLauncher")
        if settings.value("remember_me", False, type=bool):
            self.username_input.setText(settings.value("username", ""))
            self.password_input.setText(settings.value("password", ""))
            self.remember_checkbox.setChecked(True)
            
    def save_credentials(self):
        """保存憑證"""
        settings = QSettings("N.L.Online", "GameLauncher")
        if self.remember_checkbox.isChecked():
            settings.setValue("username", self.username_input.text())
            settings.setValue("password", self.password_input.text())
            settings.setValue("remember_me", True)
        else:
            settings.remove("username")
            settings.remove("password")
            settings.setValue("remember_me", False)
            
    def handle_login(self):
        """處理登錄"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "錯誤", "請輸入用戶名和密碼")
            return
            
        try:
            # 驗證用戶
            user = Auth.authenticate_user(username, password)
            if user:
                # 保存憑證
                self.save_credentials()
                # 發送登錄成功信號
                self.accept()
            else:
                QMessageBox.warning(self, "錯誤", "用戶名或密碼錯誤")
        except Exception as e:
            logger.error(f"登錄失敗: {str(e)}")
            QMessageBox.critical(self, "錯誤", f"登錄失敗：{str(e)}")
            
    def show_register(self):
        """顯示註冊對話框"""
        dialog = RegisterDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 註冊成功，自動填充用戶名
            username = dialog.username_input.text().strip()
            self.username_input.setText(username)
            self.password_input.setFocus()
            
    def keyPressEvent(self, event):
        """按鍵事件"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event) 