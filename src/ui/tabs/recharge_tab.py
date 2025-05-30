from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class RechargeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        title = QLabel("USDT 充值")
        title.setFont(QFont("'Noto Sans TC', 'Microsoft JhengHei'", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        network_label = QLabel("選擇網絡：")
        network_combo = QComboBox()
        network_combo.addItems(["TRC20", "ERC20", "BEP20"])
        amount_label = QLabel("充值金額：")
        amount_input = QLineEdit()
        amount_input.setPlaceholderText("請輸入金額")
        recharge_btn = QPushButton("立即充值")
        layout.addWidget(network_label)
        layout.addWidget(network_combo)
        layout.addWidget(amount_label)
        layout.addWidget(amount_input)
        layout.addWidget(recharge_btn)