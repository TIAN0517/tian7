import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QCheckBox, QMessageBox,
                            QStackedWidget, QWidget)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont
from database import UserManager

class LoginPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Logo
        logo_label = QLabel()
        logo_label.setFixedSize(120, 120)
        logo_label.setObjectName("logo")
        logo_label.setAlignment(Qt.AlignCenter)
        
        # 標題
        title_label = QLabel("歡迎回來")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        
        # 帳號輸入
        account_layout = QVBoxLayout()
        account_label = QLabel("帳號")
        account_label.setObjectName("inputLabel")
        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("請輸入帳號")
        self.account_input.setObjectName("accountInput")
        account_layout.addWidget(account_label)
        account_layout.addWidget(self.account_input)
        
        # 密碼輸入
        password_layout = QVBoxLayout()
        password_label = QLabel("密碼")
        password_label.setObjectName("inputLabel")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("請輸入密碼")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("passwordInput")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        # 記住我選項
        remember_layout = QHBoxLayout()
        self.remember_checkbox = QCheckBox("記住我")
        self.remember_checkbox.setObjectName("rememberCheckbox")
        remember_layout.addWidget(self.remember_checkbox)
        remember_layout.addStretch()
        
        # 登入按鈕
        self.login_button = QPushButton("登入")
        self.login_button.setObjectName("loginButton")
        self.login_button.setFixedHeight(45)
        self.login_button.clicked.connect(self.handle_login)
        
        # 註冊按鈕
        register_button = QPushButton("還沒有帳號？立即註冊")
        register_button.setObjectName("registerButton")
        register_button.clicked.connect(lambda: self.parent.switch_page("register"))
        
        # 添加所有元件到主佈局
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addLayout(account_layout)
        layout.addLayout(password_layout)
        layout.addLayout(remember_layout)
        layout.addWidget(self.login_button)
        layout.addWidget(register_button)
        layout.addStretch()
    
    def handle_login(self):
        account = self.account_input.text()
        password = self.password_input.text()
        
        if not account or not password:
            QMessageBox.warning(self, "錯誤", "請輸入帳號和密碼")
            return
        
        success, result = self.parent.user_manager.login(
            account, 
            password, 
            self.remember_checkbox.isChecked()
        )
        
        if success:
            self.parent.accept()
        else:
            QMessageBox.warning(self, "錯誤", result)

class RegisterPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # 標題
        title_label = QLabel("創建新帳號")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        
        # 帳號輸入
        account_layout = QVBoxLayout()
        account_label = QLabel("帳號")
        account_label.setObjectName("inputLabel")
        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("請輸入帳號")
        self.account_input.setObjectName("accountInput")
        account_layout.addWidget(account_label)
        account_layout.addWidget(self.account_input)
        
        # 密碼輸入
        password_layout = QVBoxLayout()
        password_label = QLabel("密碼")
        password_label.setObjectName("inputLabel")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("請輸入密碼")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("passwordInput")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        
        # 確認密碼
        confirm_layout = QVBoxLayout()
        confirm_label = QLabel("確認密碼")
        confirm_label.setObjectName("inputLabel")
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("請再次輸入密碼")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setObjectName("passwordInput")
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        
        # 郵箱輸入
        email_layout = QVBoxLayout()
        email_label = QLabel("郵箱")
        email_label.setObjectName("inputLabel")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("請輸入郵箱")
        self.email_input.setObjectName("emailInput")
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        
        # 註冊按鈕
        self.register_button = QPushButton("註冊")
        self.register_button.setObjectName("registerButton")
        self.register_button.setFixedHeight(45)
        self.register_button.clicked.connect(self.handle_register)
        
        # 返回登入按鈕
        back_button = QPushButton("返回登入")
        back_button.setObjectName("backButton")
        back_button.clicked.connect(lambda: self.parent.switch_page("login"))
        
        # 添加所有元件到主佈局
        layout.addWidget(title_label)
        layout.addLayout(account_layout)
        layout.addLayout(password_layout)
        layout.addLayout(confirm_layout)
        layout.addLayout(email_layout)
        layout.addWidget(self.register_button)
        layout.addWidget(back_button)
        layout.addStretch()
    
    def handle_register(self):
        account = self.account_input.text()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        email = self.email_input.text()
        
        if not all([account, password, confirm, email]):
            QMessageBox.warning(self, "錯誤", "請填寫所有欄位")
            return
        
        if password != confirm:
            QMessageBox.warning(self, "錯誤", "兩次輸入的密碼不一致")
            return
        
        success, message = self.parent.user_manager.register(account, password, email)
        
        if success:
            QMessageBox.information(self, "成功", message)
            self.parent.switch_page("login")
        else:
            QMessageBox.warning(self, "錯誤", message)

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("遊戲啟動器 - 登入")
        self.setFixedSize(400, 600)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        
        # 初始化用戶管理器
        self.user_manager = UserManager()
        
        # 創建堆疊部件
        self.stacked_widget = QStackedWidget()
        
        # 創建登入和註冊頁面
        self.login_page = LoginPage(self)
        self.register_page = RegisterPage(self)
        
        # 添加頁面到堆疊部件
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.register_page)
        
        # 主佈局
        layout = QVBoxLayout(self)
        layout.addWidget(self.stacked_widget)
        
        # 設置樣式
        self.load_styles()
        
        # 檢查是否有保存的登入信息
        self.check_saved_credentials()
    
    def switch_page(self, page_name):
        if page_name == "login":
            self.stacked_widget.setCurrentWidget(self.login_page)
        elif page_name == "register":
            self.stacked_widget.setCurrentWidget(self.register_page)
    
    def check_saved_credentials(self):
        credentials = self.user_manager.load_credentials()
        if credentials:
            self.login_page.account_input.setText(credentials["username"])
            self.login_page.password_input.setText(credentials["password"])
            self.login_page.remember_checkbox.setChecked(True)
    
    def load_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1a1a;
            }
            
            #logo {
                background-color: #2d2d2d;
                border-radius: 60px;
            }
            
            #title {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            
            #inputLabel {
                color: #ffffff;
                font-size: 14px;
                margin-bottom: 5px;
            }
            
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
                color: #ffffff;
                font-size: 14px;
            }
            
            QLineEdit:focus {
                border: 1px solid #00ff00;
            }
            
            QLineEdit::placeholder {
                color: #666666;
            }
            
            #rememberCheckbox {
                color: #ffffff;
                font-size: 14px;
            }
            
            #rememberCheckbox::indicator {
                width: 18px;
                height: 18px;
            }
            
            #rememberCheckbox::indicator:unchecked {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
            }
            
            #rememberCheckbox::indicator:checked {
                background-color: #00ff00;
                border: 1px solid #00ff00;
                border-radius: 3px;
            }
            
            #loginButton, #registerButton {
                background-color: #00ff00;
                color: #000000;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            
            #loginButton:hover, #registerButton:hover {
                background-color: #00cc00;
            }
            
            #loginButton:pressed, #registerButton:pressed {
                background-color: #009900;
            }
            
            #backButton {
                background-color: #363636;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            
            #backButton:hover {
                background-color: #4a4a4a;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_()) 