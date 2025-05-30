from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QMessageBox, QDialog,
    QLineEdit, QSpinBox, QTabWidget, QTextEdit, QProgressBar,
    QSlider, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon
import random
from datetime import datetime
import sqlite3
import os

class GameWindow(QMainWindow):
    """賭場遊戲主系統"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RanNL Casino - 賭場系統")
        self.setFixedSize(900, 600)
        
        # 玩家數據
        self.player_credits = 1000.0  # 初始積分
        self.player_name = "Player"
        
        # 初始化數據庫
        self.init_database()
        
        # 初始化組件
        self.init_ui()
        self.load_styles()
        self.setup_connections()
        
        # 載入玩家數據
        self.load_player_data()
        
    def init_database(self):
        """初始化數據庫"""
        try:
            self.db_path = "casino_data.db"
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 創建玩家數據表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    credits REAL DEFAULT 1000.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 創建遊戲記錄表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    game_type TEXT NOT NULL,
                    bet_amount REAL NOT NULL,
                    win_amount REAL DEFAULT 0.0,
                    result TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"數據庫初始化失敗: {e}")
            
    def load_player_data(self):
        """載入玩家數據"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT credits FROM players WHERE name = ?", (self.player_name,))
            result = cursor.fetchone()
            
            if result:
                self.player_credits = result[0]
            else:
                # 創建新玩家
                cursor.execute("INSERT INTO players (name, credits) VALUES (?, ?)", 
                             (self.player_name, self.player_credits))
                conn.commit()
                
            conn.close()
            self.update_credits_display()
            
        except Exception as e:
            print(f"載入玩家數據失敗: {e}")
            
    def save_player_data(self):
        """保存玩家數據"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE players 
                SET credits = ?, last_updated = CURRENT_TIMESTAMP 
                WHERE name = ?
            """, (self.player_credits, self.player_name))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"保存玩家數據失敗: {e}")
            
    def init_ui(self):
        """初始化 UI 組件"""
        # 創建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 頂部信息欄
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)
        
        # 遊戲區域
        game_area = self.create_game_area()
        main_layout.addWidget(game_area)
        
        # 底部控制欄
        bottom_bar = self.create_bottom_bar()
        main_layout.addWidget(bottom_bar)
        
    def create_top_bar(self) -> QWidget:
        """創建頂部信息欄"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # 玩家信息
        player_info = QGroupBox("玩家資訊")
        player_layout = QVBoxLayout(player_info)
        
        self.player_name_label = QLabel(f"玩家: {self.player_name}")
        self.player_name_label.setObjectName("playerName")
        
        self.credits_label = QLabel(f"積分: {self.player_credits:.2f}")
        self.credits_label.setObjectName("credits")
        
        player_layout.addWidget(self.player_name_label)
        player_layout.addWidget(self.credits_label)
        
        # 充值區域
        recharge_group = QGroupBox("充值中心")
        recharge_layout = QVBoxLayout(recharge_group)
        
        recharge_info = QLabel("選擇充值金額:")
        recharge_layout.addWidget(recharge_info)
        
        recharge_buttons_layout = QHBoxLayout()
        recharge_amounts = [100, 500, 1000, 5000]
        
        for amount in recharge_amounts:
            btn = QPushButton(f"${amount}")
            btn.setObjectName("rechargeButton")
            btn.clicked.connect(lambda checked, amt=amount: self.recharge_credits(amt))
            recharge_buttons_layout.addWidget(btn)
            
        recharge_layout.addLayout(recharge_buttons_layout)
        
        # 返回啟動器按鈕
        back_button = QPushButton("返回啟動器")
        back_button.setObjectName("backButton")
        back_button.clicked.connect(self.back_to_launcher)
        
        layout.addWidget(player_info, 2)
        layout.addWidget(recharge_group, 3)
        layout.addWidget(back_button, 1)
        
        return widget
        
    def create_game_area(self) -> QWidget:
        """創建遊戲區域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 遊戲標籤頁
        tab_widget = QTabWidget()
        tab_widget.setObjectName("gameTabs")
        
        # 老虎機遊戲
        slot_machine_tab = self.create_slot_machine()
        tab_widget.addTab(slot_machine_tab, "🎰 老虎機")
        
        # 輪盤遊戲
        roulette_tab = self.create_roulette()
        tab_widget.addTab(roulette_tab, "🎡 輪盤")
        
        # 二十一點
        blackjack_tab = self.create_blackjack()
        tab_widget.addTab(blackjack_tab, "🃏 二十一點")
        
        # 遊戲記錄
        records_tab = self.create_game_records()
        tab_widget.addTab(records_tab, "📊 遊戲記錄")
        
        layout.addWidget(tab_widget)
        return widget
        
    def create_slot_machine(self) -> QWidget:
        """創建老虎機遊戲"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        
        # 遊戲標題
        title = QLabel("🎰 老虎機遊戲")
        title.setObjectName("gameTitle")
        title.setAlignment(Qt.AlignCenter)
        
        # 老虎機顯示
        slot_area = QFrame()
        slot_area.setObjectName("slotMachine")
        slot_layout = QHBoxLayout(slot_area)
        
        self.slot_reels = []
        symbols = ["🍒", "🍊", "🍇", "⭐", "💎", "7️⃣"]
        
        for i in range(3):
            reel = QLabel("🍒")
            reel.setObjectName("slotReel")
            reel.setAlignment(Qt.AlignCenter)
            reel.setMinimumSize(100, 100)
            self.slot_reels.append(reel)
            slot_layout.addWidget(reel)
            
        # 下注控制
        bet_area = QFrame()
        bet_layout = QHBoxLayout(bet_area)
        
        bet_layout.addWidget(QLabel("下注金額:"))
        
        self.slot_bet_input = QSpinBox()
        self.slot_bet_input.setMinimum(10)
        self.slot_bet_input.setMaximum(1000)
        self.slot_bet_input.setValue(50)
        bet_layout.addWidget(self.slot_bet_input)
        
        self.slot_spin_button = QPushButton("旋轉!")
        self.slot_spin_button.setObjectName("spinButton")
        self.slot_spin_button.clicked.connect(self.play_slot_machine)
        bet_layout.addWidget(self.slot_spin_button)
        
        # 結果顯示
        self.slot_result = QLabel("準備開始遊戲!")
        self.slot_result.setObjectName("gameResult")
        self.slot_result.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(slot_area)
        layout.addWidget(bet_area)
        layout.addWidget(self.slot_result)
        
        return widget
        
    def create_roulette(self) -> QWidget:
        """創建輪盤遊戲"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("🎡 輪盤遊戲")
        title.setObjectName("gameTitle")
        title.setAlignment(Qt.AlignCenter)
        
        # 輪盤顯示
        roulette_area = QFrame()
        roulette_area.setObjectName("roulette")
        roulette_layout = QVBoxLayout(roulette_area)
        
        self.roulette_result = QLabel("0")
        self.roulette_result.setObjectName("rouletteNumber")
        self.roulette_result.setAlignment(Qt.AlignCenter)
        self.roulette_result.setMinimumSize(150, 150)
        
        # 下注選項
        bet_options = QFrame()
        bet_layout = QGridLayout(bet_options)
        
        # 顏色下注
        red_btn = QPushButton("紅色 (2x)")
        red_btn.setObjectName("redBet")
        red_btn.clicked.connect(lambda: self.place_roulette_bet("red"))
        
        black_btn = QPushButton("黑色 (2x)")
        black_btn.setObjectName("blackBet")
        black_btn.clicked.connect(lambda: self.place_roulette_bet("black"))
        
        # 奇偶下注
        odd_btn = QPushButton("奇數 (2x)")
        odd_btn.setObjectName("oddBet")
        odd_btn.clicked.connect(lambda: self.place_roulette_bet("odd"))
        
        even_btn = QPushButton("偶數 (2x)")
        even_btn.setObjectName("evenBet")
        even_btn.clicked.connect(lambda: self.place_roulette_bet("even"))
        
        bet_layout.addWidget(red_btn, 0, 0)
        bet_layout.addWidget(black_btn, 0, 1)
        bet_layout.addWidget(odd_btn, 1, 0)
        bet_layout.addWidget(even_btn, 1, 1)
        
        # 下注金額
        bet_control = QHBoxLayout()
        bet_control.addWidget(QLabel("下注金額:"))
        
        self.roulette_bet_input = QSpinBox()
        self.roulette_bet_input.setMinimum(10)
        self.roulette_bet_input.setMaximum(1000)
        self.roulette_bet_input.setValue(50)
        bet_control.addWidget(self.roulette_bet_input)
        
        # 結果顯示
        self.roulette_game_result = QLabel("選擇下注選項!")
        self.roulette_game_result.setObjectName("gameResult")
        self.roulette_game_result.setAlignment(Qt.AlignCenter)
        
        roulette_layout.addWidget(self.roulette_result)
        
        layout.addWidget(title)
        layout.addWidget(roulette_area)
        layout.addWidget(bet_options)
        layout.addLayout(bet_control)
        layout.addWidget(self.roulette_game_result)
        
        return widget
        
    def create_blackjack(self) -> QWidget:
        """創建二十一點遊戲"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("🃏 二十一點")
        title.setObjectName("gameTitle")
        title.setAlignment(Qt.AlignCenter)
        
        info = QLabel("簡化版二十一點 - 目標接近21點但不超過")
        info.setAlignment(Qt.AlignCenter)
        
        # 遊戲區域
        game_area = QFrame()
        game_layout = QVBoxLayout(game_area)
        
        # 玩家手牌
        self.player_cards = QLabel("玩家手牌: 等待開始")
        self.player_cards.setObjectName("cardDisplay")
        
        # 電腦手牌
        self.dealer_cards = QLabel("莊家手牌: 等待開始")
        self.dealer_cards.setObjectName("cardDisplay")
        
        # 控制按鈕
        controls = QHBoxLayout()
        
        self.blackjack_bet_input = QSpinBox()
        self.blackjack_bet_input.setMinimum(10)
        self.blackjack_bet_input.setMaximum(1000)
        self.blackjack_bet_input.setValue(50)
        
        deal_btn = QPushButton("發牌")
        deal_btn.clicked.connect(self.deal_blackjack)
        
        hit_btn = QPushButton("要牌")
        hit_btn.clicked.connect(self.hit_blackjack)
        
        stand_btn = QPushButton("停牌")
        stand_btn.clicked.connect(self.stand_blackjack)
        
        controls.addWidget(QLabel("下注:"))
        controls.addWidget(self.blackjack_bet_input)
        controls.addWidget(deal_btn)
        controls.addWidget(hit_btn)
        controls.addWidget(stand_btn)
        
        # 結果
        self.blackjack_result = QLabel("點擊發牌開始遊戲!")
        self.blackjack_result.setObjectName("gameResult")
        self.blackjack_result.setAlignment(Qt.AlignCenter)
        
        game_layout.addWidget(self.player_cards)
        game_layout.addWidget(self.dealer_cards)
        
        layout.addWidget(title)
        layout.addWidget(info)
        layout.addWidget(game_area)
        layout.addLayout(controls)
        layout.addWidget(self.blackjack_result)
        
        return widget
        
    def create_game_records(self) -> QWidget:
        """創建遊戲記錄"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title = QLabel("📊 遊戲記錄")
        title.setObjectName("gameTitle")
        title.setAlignment(Qt.AlignCenter)
        
        self.records_text = QTextEdit()
        self.records_text.setReadOnly(True)
        self.load_game_records()
        
        refresh_btn = QPushButton("刷新記錄")
        refresh_btn.clicked.connect(self.load_game_records)
        
        layout.addWidget(title)
        layout.addWidget(self.records_text)
        layout.addWidget(refresh_btn)
        
        return widget
        
    def create_bottom_bar(self) -> QWidget:
        """創建底部控制欄"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # 遊戲狀態
        status_label = QLabel("遊戲狀態: 就緒")
        status_label.setObjectName("statusLabel")
        
        # 自動保存提示
        auto_save_label = QLabel("💾 自動保存已啟用")
        auto_save_label.setObjectName("autoSaveLabel")
        
        layout.addWidget(status_label)
        layout.addStretch()
        layout.addWidget(auto_save_label)
        
        return widget
        
    def load_styles(self):
        """載入樣式"""
        self.setStyleSheet("""
        QMainWindow, QWidget {
            font-family: 'Noto Sans TC', 'Microsoft JhengHei', 'Arial', 'sans-serif';
        }
        #gameTitle {
            font-size: 26px;
            font-weight: 800;
            color: #FFD700;
            text-shadow: 0 2px 16px #000, 0 0 16px #FFD700;
        }
        #playerName {
            font-size: 16px;
            font-weight: 700;
            color: #FFD700;
            text-shadow: 0 2px 12px #000, 0 0 12px #FFD700;
        }
        #credits {
            font-size: 17px;
            font-weight: 700;
            color: #8fd3f4;
            text-shadow: 0 1px 8px #000;
        }
        #rechargeButton, #backButton {
            font-size: 16px;
            font-weight: 700;
            text-shadow: 0 1px 8px #000;
        }
        #slotReel {
            font-size: 34px;
            font-weight: 700;
            color: #23243a;
        }
        #spinButton {
            font-size: 18px;
            font-weight: 800;
            text-shadow: 0 1px 8px #000;
        }
        #rouletteNumber {
            font-size: 34px;
            font-weight: 800;
            color: #FFD700;
            text-shadow: 0 2px 16px #000, 0 0 16px #FFD700;
        }
        #redBet, #blackBet, #oddBet, #evenBet {
            font-size: 15px;
            font-weight: 700;
            text-shadow: 0 1px 8px #000;
        }
        #cardDisplay {
            font-size: 15px;
            font-weight: 600;
            color: #FFD700;
            text-shadow: 0 1px 8px #000;
        }
        #gameResult {
            font-size: 17px;
            font-weight: 800;
            color: #FFD700;
            text-shadow: 0 2px 16px #000, 0 0 16px #FFD700;
        }
        QGroupBox {
            font-size: 17px;
            font-weight: 700;
            color: #FFD700;
        }
        QGroupBox::title {
            font-size: 16px;
            font-weight: 800;
            color: #FFD700;
            text-shadow: 0 2px 16px #000, 0 0 16px #FFD700;
        }
        QDialog, QMessageBox {
            font-family: 'Noto Sans TC', 'Microsoft JhengHei', 'Arial', 'sans-serif';
            font-size: 18px;
            font-weight: 800;
            color: #FFD700;
            text-shadow: 0 2px 16px #000, 0 0 16px #FFD700;
        }
        QMessageBox QLabel, QDialog QLabel {
            font-size: 17px;
            font-weight: 700;
            color: #FFD700;
            text-shadow: 0 2px 16px #000, 0 0 16px #FFD700;
        }
        QMessageBox QPushButton, QDialog QPushButton {
            font-size: 16px;
            font-weight: 700;
            text-shadow: 0 1px 8px #000;
        }
        """)
        
    def setup_connections(self):
        """設置信號連接"""
        # 自動保存定時器
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.save_player_data)
        self.auto_save_timer.start(30000)  # 每30秒保存一次
        
    def update_credits_display(self):
        """更新積分顯示"""
        self.credits_label.setText(f"積分: {self.player_credits:.2f}")
        
    def recharge_credits(self, amount):
        """充值積分"""
        reply = QMessageBox.question(
            self, "確認充值",
            f"確定要充值 ${amount} 嗎？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.player_credits += amount
            self.update_credits_display()
            self.save_player_data()
            QMessageBox.information(self, "充值成功", f"成功充值 ${amount}！\n當前積分: {self.player_credits}")
            
    def play_slot_machine(self):
        """玩老虎機"""
        bet_amount = self.slot_bet_input.value()
        
        if self.player_credits < bet_amount:
            QMessageBox.warning(self, "積分不足", "積分不足，無法下注！")
            return
            
        # 扣除下注金額
        self.player_credits -= bet_amount
        
        # 隨機結果
        symbols = ["🍒", "🍊", "🍇", "⭐", "💎", "7️⃣"]
        results = [random.choice(symbols) for _ in range(3)]
        
        # 更新顯示
        for i, result in enumerate(results):
            self.slot_reels[i].setText(result)
            
        # 計算獎金
        win_amount = 0
        if results[0] == results[1] == results[2]:
            if results[0] == "💎":
                win_amount = bet_amount * 50  # 鑽石最高倍率
            elif results[0] == "7️⃣":
                win_amount = bet_amount * 20
            elif results[0] == "⭐":
                win_amount = bet_amount * 10
            else:
                win_amount = bet_amount * 5
        elif results[0] == results[1] or results[1] == results[2] or results[0] == results[2]:
            win_amount = bet_amount * 2  # 兩個相同
            
        self.player_credits += win_amount
        
        # 顯示結果
        if win_amount > 0:
            self.slot_result.setText(f"🎉 恭喜！獲得 {win_amount} 積分！")
        else:
            self.slot_result.setText("很遺憾，沒有中獎")
            
        self.update_credits_display()
        self.save_game_record("老虎機", bet_amount, win_amount, f"結果: {' '.join(results)}")
        
    def place_roulette_bet(self, bet_type):
        """下輪盤賭注"""
        bet_amount = self.roulette_bet_input.value()
        
        if self.player_credits < bet_amount:
            QMessageBox.warning(self, "積分不足", "積分不足，無法下注！")
            return
            
        # 扣除下注金額
        self.player_credits -= bet_amount
        
        # 隨機號碼 (0-36)
        number = random.randint(0, 36)
        self.roulette_result.setText(str(number))
        
        # 判斷結果
        win = False
        if bet_type == "red" and number in [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]:
            win = True
        elif bet_type == "black" and number in [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]:
            win = True
        elif bet_type == "odd" and number % 2 == 1 and number != 0:
            win = True
        elif bet_type == "even" and number % 2 == 0 and number != 0:
            win = True
            
        win_amount = 0
        if win:
            win_amount = bet_amount * 2
            self.player_credits += win_amount
            self.roulette_game_result.setText(f"🎉 恭喜！{bet_type} 中獎！獲得 {win_amount} 積分！")
        else:
            self.roulette_game_result.setText(f"很遺憾，號碼 {number} 沒有中 {bet_type}")
            
        self.update_credits_display()
        self.save_game_record("輪盤", bet_amount, win_amount, f"{bet_type} - 結果: {number}")
        
    def deal_blackjack(self):
        """發牌二十一點"""
        bet_amount = self.blackjack_bet_input.value()
        
        if self.player_credits < bet_amount:
            QMessageBox.warning(self, "積分不足", "積分不足，無法下注！")
            return
            
        # 簡化版：直接計算點數
        self.player_total = random.randint(12, 21)
        self.dealer_total = random.randint(17, 21)
        
        self.player_cards.setText(f"玩家手牌: {self.player_total} 點")
        self.dealer_cards.setText("莊家手牌: ? 點 (隱藏)")
        
        self.current_bet = bet_amount
        self.player_credits -= bet_amount
        self.update_credits_display()
        
        if self.player_total == 21:
            self.finish_blackjack()
        else:
            self.blackjack_result.setText("選擇要牌或停牌")
            
    def hit_blackjack(self):
        """要牌"""
        if hasattr(self, 'player_total'):
            self.player_total += random.randint(1, 10)
            self.player_cards.setText(f"玩家手牌: {self.player_total} 點")
            
            if self.player_total > 21:
                self.blackjack_result.setText("💥 爆牌！莊家獲勝！")
                self.save_game_record("二十一點", self.current_bet, 0, f"玩家: {self.player_total} (爆牌)")
            elif self.player_total == 21:
                self.finish_blackjack()
                
    def stand_blackjack(self):
        """停牌"""
        self.finish_blackjack()
        
    def finish_blackjack(self):
        """結束二十一點"""
        if hasattr(self, 'player_total') and hasattr(self, 'dealer_total'):
            self.dealer_cards.setText(f"莊家手牌: {self.dealer_total} 點")
            
            win_amount = 0
            if self.player_total > 21:
                result = "爆牌失敗"
            elif self.dealer_total > 21:
                win_amount = self.current_bet * 2
                result = "莊家爆牌，玩家獲勝！"
            elif self.player_total > self.dealer_total:
                win_amount = self.current_bet * 2
                result = "玩家獲勝！"
            elif self.player_total == self.dealer_total:
                win_amount = self.current_bet
                result = "平局！"
            else:
                result = "莊家獲勝！"
                
            self.player_credits += win_amount
            self.update_credits_display()
            self.blackjack_result.setText(result)
            
            self.save_game_record("二十一點", self.current_bet, win_amount, 
                                f"玩家: {self.player_total}, 莊家: {self.dealer_total}")
                                
    def save_game_record(self, game_type, bet_amount, win_amount, result):
        """保存遊戲記錄"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO game_records (player_name, game_type, bet_amount, win_amount, result)
                VALUES (?, ?, ?, ?, ?)
            """, (self.player_name, game_type, bet_amount, win_amount, result))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"保存遊戲記錄失敗: {e}")
            
    def load_game_records(self):
        """載入遊戲記錄"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT game_type, bet_amount, win_amount, result, timestamp 
                FROM game_records 
                WHERE player_name = ? 
                ORDER BY timestamp DESC 
                LIMIT 50
            """, (self.player_name,))
            
            records = cursor.fetchall()
            conn.close()
            
            text = "最近50場遊戲記錄:\n\n"
            for record in records:
                game_type, bet, win, result, timestamp = record
                profit = win - bet
                text += f"[{timestamp}] {game_type}\n"
                text += f"  下注: {bet}, 獲得: {win}, 盈虧: {profit:+.2f}\n"
                text += f"  結果: {result}\n\n"
                
            self.records_text.setText(text)
            
        except Exception as e:
            self.records_text.setText(f"載入記錄失敗: {e}")
            
    def back_to_launcher(self):
        """返回啟動器"""
        self.save_player_data()
        
        # 獲取父窗口引用並顯示
        try:
            # 尋找MainWindow實例
            import sys
            for widget in sys.app.allWidgets() if hasattr(sys, 'app') else []:
                if widget.__class__.__name__ in ['MainWindow', 'GameEmpireMainWindow']:
                    widget.show()
                    break
            else:
                # 如果找不到，創建新的主窗口
                from ..main_window import GameEmpireMainWindow
                main_window = GameEmpireMainWindow()
                main_window.show()
        except Exception as e:
            print(f"返回啟動器失敗: {e}")
            # 備用方案：直接創建新主窗口
            try:
                from ..main_window import GameEmpireMainWindow
                main_window = GameEmpireMainWindow()
                main_window.show()
            except:
                pass
        
        # 關閉當前遊戲窗口
        self.close()
            
    def closeEvent(self, event):
        """關閉事件"""
        self.save_player_data()
        
        # 當遊戲窗口關閉時，確保主窗口顯示
        try:
            import sys
            for widget in sys.app.allWidgets() if hasattr(sys, 'app') else []:
                if widget.__class__.__name__ in ['MainWindow', 'GameEmpireMainWindow']:
                    widget.show()
                    break
        except:
            pass
            
        event.accept() 