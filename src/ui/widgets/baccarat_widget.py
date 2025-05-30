"""
百家樂遊戲界面模組
提供完整的百家樂遊戲UI體驗
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QMessageBox, QLineEdit,
    QGroupBox, QSplitter, QWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
from src.games.baccarat.baccarat_logic import BaccaratGame, BetType
import sys
import os

class BaccaratWidget(QDialog):
    """百家樂遊戲界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🎴 百家樂 - Jy技術團隊遊戲帝國")
        self.setFixedSize(1200, 800)
        
        # 初始化遊戲邏輯
        self.game = BaccaratGame()
        
        # 設置樣式
        self.setStyleSheet("""
            QDialog {
                background: qradialgradient(cx:0.5, cy:0.3, radius:1.0, fx:0.5, fy:0.3, 
                           stop:0 #1a472a, stop:0.5 #15803d, stop:1 #166534);
                font-family: 'Microsoft JhengHei', 'Arial', sans-serif;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: 700;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 10px;
                margin: 10px 5px;
                padding-top: 15px;
                background: rgba(30,40,60,0.7);
            }
            QGroupBox::title {
                font-size: 14px;
                font-weight: 800;
                color: #FFD700;
                padding: 0 10px;
            }
            QLabel {
                color: #e0e0e0;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton {
                font-size: 14px;
                font-weight: 700;
                padding: 8px 16px;
                border-radius: 8px;
                border: 2px solid #8fd3f4;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                           stop:0 #8fd3f4, stop:1 #5dade2);
                color: #23243a;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                           stop:0 #FFD700, stop:1 #f1c40f);
                border: 2px solid #FFD700;
            }
            QPushButton:pressed {
                background: #e67e22;
            }
            QLineEdit {
                font-size: 14px;
                font-weight: 600;
                padding: 8px;
                border: 2px solid #8fd3f4;
                border-radius: 6px;
                background: rgba(255,255,255,0.9);
                color: #23243a;
            }
        """)
        
        self.init_ui()
        self.update_display()
        
    def init_ui(self):
        """初始化UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 左側：遊戲主區域
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # 牌桌區域
        self.create_table_area(left_panel)
        
        # 下注區域
        self.create_betting_area(left_panel)
        
        # 遊戲控制區域
        self.create_control_area(left_panel)
        
        main_layout.addLayout(left_panel, 3)
        
        # 右側：信息面板
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        # 玩家信息
        self.create_player_info(right_panel)
        
        # 遊戲歷史
        self.create_history_area(right_panel)
        
        # 規則說明
        self.create_rules_area(right_panel)
        
        main_layout.addLayout(right_panel, 1)
    
    def create_table_area(self, parent_layout):
        """創建牌桌區域"""
        table_group = QGroupBox("🎴 牌桌")
        table_layout = QVBoxLayout(table_group)
        table_layout.setSpacing(20)
        
        # 莊家區域
        banker_area = QFrame()
        banker_area.setStyleSheet("""
            QFrame {
                background: rgba(255,0,0,0.1);
                border: 2px solid #dc2626;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        banker_layout = QVBoxLayout(banker_area)
        
        self.banker_title = QLabel("🏛️ 莊家 (BANKER)")
        self.banker_title.setAlignment(Qt.AlignCenter)
        self.banker_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #dc2626;")
        
        self.banker_cards = QLabel("等待發牌...")
        self.banker_cards.setAlignment(Qt.AlignCenter)
        self.banker_cards.setStyleSheet("font-size: 24px; min-height: 80px; background: rgba(255,255,255,0.1); border-radius: 8px; padding: 10px;")
        
        self.banker_value = QLabel("點數: 0")
        self.banker_value.setAlignment(Qt.AlignCenter)
        self.banker_value.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFD700;")
        
        banker_layout.addWidget(self.banker_title)
        banker_layout.addWidget(self.banker_cards)
        banker_layout.addWidget(self.banker_value)
        
        # 閒家區域
        player_area = QFrame()
        player_area.setStyleSheet("""
            QFrame {
                background: rgba(0,0,255,0.1);
                border: 2px solid #2563eb;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        player_layout = QVBoxLayout(player_area)
        
        self.player_title = QLabel("👤 閒家 (PLAYER)")
        self.player_title.setAlignment(Qt.AlignCenter)
        self.player_title.setStyleSheet("font-size: 18px; font-weight: 800; color: #2563eb;")
        
        self.player_cards = QLabel("等待發牌...")
        self.player_cards.setAlignment(Qt.AlignCenter)
        self.player_cards.setStyleSheet("font-size: 24px; min-height: 80px; background: rgba(255,255,255,0.1); border-radius: 8px; padding: 10px;")
        
        self.player_value = QLabel("點數: 0")
        self.player_value.setAlignment(Qt.AlignCenter)
        self.player_value.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFD700;")
        
        player_layout.addWidget(self.player_title)
        player_layout.addWidget(self.player_cards)
        player_layout.addWidget(self.player_value)
        
        table_layout.addWidget(banker_area)
        table_layout.addWidget(player_area)
        
        parent_layout.addWidget(table_group)
    
    def create_betting_area(self, parent_layout):
        """創建下注區域"""
        betting_group = QGroupBox("💰 下注區域")
        betting_layout = QGridLayout(betting_group)
        betting_layout.setSpacing(15)
        
        # 下注按鈕和顯示
        bet_areas = [
            ("莊家", "banker", "#dc2626", "1:0.95"),
            ("閒家", "player", "#2563eb", "1:1"),
            ("和局", "tie", "#16a34a", "1:8")
        ]
        
        self.bet_labels = {}
        self.bet_buttons = {}
        
        for i, (name, bet_type, color, odds) in enumerate(bet_areas):
            # 下注區域框架
            bet_frame = QFrame()
            bet_frame.setStyleSheet(f"""
                QFrame {{
                    background: rgba(255,255,255,0.05);
                    border: 2px solid {color};
                    border-radius: 10px;
                    padding: 10px;
                }}
            """)
            bet_frame_layout = QVBoxLayout(bet_frame)
            
            # 標題
            title = QLabel(f"{name}\n賠率 {odds}")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {color};")
            bet_frame_layout.addWidget(title)
            
            # 當前下注金額顯示
            bet_amount_label = QLabel("下注: $0")
            bet_amount_label.setAlignment(Qt.AlignCenter)
            bet_amount_label.setStyleSheet("font-size: 12px; color: #FFD700;")
            self.bet_labels[bet_type] = bet_amount_label
            bet_frame_layout.addWidget(bet_amount_label)
            
            # 下注按鈕
            bet_button = QPushButton(f"下注 {name}")
            bet_button.clicked.connect(lambda checked, bt=bet_type: self.open_bet_dialog(bt))
            self.bet_buttons[bet_type] = bet_button
            bet_frame_layout.addWidget(bet_button)
            
            betting_layout.addWidget(bet_frame, 0, i)
        
        # 快速下注按鈕
        quick_bet_layout = QHBoxLayout()
        quick_amounts = [100, 500, 1000, 5000]
        for amount in quick_amounts:
            btn = QPushButton(f"${amount}")
            btn.setFixedWidth(80)
            btn.clicked.connect(lambda checked, amt=amount: self.set_quick_bet_amount(amt))
            quick_bet_layout.addWidget(btn)
        
        # 清空下注按鈕
        clear_btn = QPushButton("清空下注")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                           stop:0 #dc2626, stop:1 #b91c1c);
                border: 2px solid #dc2626;
                color: white;
            }
            QPushButton:hover {
                background: #ef4444;
            }
        """)
        clear_btn.clicked.connect(self.clear_all_bets)
        quick_bet_layout.addWidget(clear_btn)
        
        betting_layout.addLayout(quick_bet_layout, 1, 0, 1, 3)
        
        parent_layout.addWidget(betting_group)
    
    def create_control_area(self, parent_layout):
        """創建遊戲控制區域"""
        control_group = QGroupBox("🎮 遊戲控制")
        control_layout = QHBoxLayout(control_group)
        control_layout.setSpacing(15)
        
        # 發牌按鈕
        self.deal_button = QPushButton("🎴 發牌開始")
        self.deal_button.setFixedHeight(50)
        self.deal_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: 800;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                           stop:0 #16a34a, stop:1 #15803d);
                border: 3px solid #16a34a;
                color: white;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                           stop:0 #FFD700, stop:1 #f1c40f);
                border: 3px solid #FFD700;
                color: #23243a;
            }
        """)
        self.deal_button.clicked.connect(self.start_game)
        control_layout.addWidget(self.deal_button)
        
        # 新一局按鈕
        new_game_btn = QPushButton("🔄 新一局")
        new_game_btn.clicked.connect(self.new_game)
        control_layout.addWidget(new_game_btn)
        
        # 返回大廳按鈕
        back_btn = QPushButton("🏠 返回大廳")
        back_btn.clicked.connect(self.close)
        control_layout.addWidget(back_btn)
        
        parent_layout.addWidget(control_group)
    
    def create_player_info(self, parent_layout):
        """創建玩家信息區域"""
        info_group = QGroupBox("💳 玩家信息")
        info_layout = QVBoxLayout(info_group)
        
        self.balance_label = QLabel(f"餘額: ${self.game.player_balance:,.2f}")
        self.balance_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #FFD700;")
        info_layout.addWidget(self.balance_label)
        
        self.total_bet_label = QLabel("總下注: $0.00")
        self.total_bet_label.setStyleSheet("font-size: 14px; color: #8fd3f4;")
        info_layout.addWidget(self.total_bet_label)
        
        parent_layout.addWidget(info_group)
    
    def create_history_area(self, parent_layout):
        """創建遊戲歷史區域"""
        history_group = QGroupBox("📊 遊戲歷史")
        history_layout = QVBoxLayout(history_group)
        
        self.history_scroll = QScrollArea()
        self.history_widget = QWidget()
        self.history_widget_layout = QVBoxLayout(self.history_widget)
        
        self.history_scroll.setWidget(self.history_widget)
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setFixedHeight(200)
        
        history_layout.addWidget(self.history_scroll)
        parent_layout.addWidget(history_group)
    
    def create_rules_area(self, parent_layout):
        """創建規則說明區域"""
        rules_group = QGroupBox("📋 遊戲規則")
        rules_layout = QVBoxLayout(rules_group)
        
        rules_text = """
• 莊家和閒家各發2張牌
• 點數只看個位數(9最大)
• A=1, 2-9=面值, 10/J/Q/K=0
• 閒家≤5點補牌，莊家依規則補牌
• 點數大者勝，相等為和局
• 賠率: 閒家1:1, 莊家1:0.95, 和局1:8
        """
        
        rules_label = QLabel(rules_text)
        rules_label.setStyleSheet("font-size: 11px; color: #e0e0e0; line-height: 1.3;")
        rules_label.setWordWrap(True)
        rules_layout.addWidget(rules_label)
        
        parent_layout.addWidget(rules_group)
    
    def open_bet_dialog(self, bet_type):
        """打開下注對話框"""
        from PyQt5.QtWidgets import QInputDialog
        
        bet_name = {"banker": "莊家", "player": "閒家", "tie": "和局"}[bet_type]
        
        amount, ok = QInputDialog.getDouble(
            self, f"下注 {bet_name}", 
            f"請輸入下注金額:\n(餘額: ${self.game.player_balance:,.2f})",
            min=10.0, max=float(self.game.player_balance), decimals=2
        )
        
        if ok and amount > 0:
            bet_enum = BetType(bet_type)
            if self.game.place_bet(bet_enum, amount):
                self.update_display()
                QMessageBox.information(self, "下注成功", f"成功下注 {bet_name} ${amount:,.2f}")
            else:
                QMessageBox.warning(self, "下注失敗", "餘額不足或下注金額無效")
    
    def set_quick_bet_amount(self, amount):
        """設置快速下注金額"""
        self.quick_bet_amount = amount
        QMessageBox.information(self, "快速下注", f"已設置快速下注金額: ${amount}")
    
    def clear_all_bets(self):
        """清空所有下注"""
        self.game.clear_bets()
        self.update_display()
        QMessageBox.information(self, "清空下注", "已清空所有下注，金額已退還")
    
    def start_game(self):
        """開始遊戲"""
        if not self.game.current_bets:
            QMessageBox.warning(self, "無法開始", "請先下注後再開始遊戲")
            return
        
        # 執行遊戲邏輯
        result = self.game.play_round()
        
        if "error" in result:
            QMessageBox.warning(self, "錯誤", result["error"])
            return
        
        # 更新顯示
        self.update_display()
        self.update_history()
        
        # 顯示結果
        self.show_game_result(result)
    
    def show_game_result(self, result):
        """顯示遊戲結果"""
        winner_text = {"player": "閒家", "banker": "莊家", "tie": "和局"}[result["result"]]
        
        message = f"""
🎉 遊戲結果 🎉

勝負: {winner_text}
閒家: {' '.join(result['player_cards'])} (點數: {result['player_value']})
莊家: {' '.join(result['banker_cards'])} (點數: {result['banker_value']})

本局獲得: ${result['winnings']:,.2f}
當前餘額: ${result['balance']:,.2f}
        """
        
        QMessageBox.information(self, "遊戲結果", message)
    
    def new_game(self):
        """開始新一局"""
        self.game.player_hand.clear()
        self.game.banker_hand.clear()
        self.update_display()
    
    def update_display(self):
        """更新顯示"""
        # 更新玩家信息
        self.balance_label.setText(f"餘額: ${self.game.player_balance:,.2f}")
        total_bet = sum(self.game.current_bets.values())
        self.total_bet_label.setText(f"總下注: ${total_bet:,.2f}")
        
        # 更新下注顯示
        for bet_type, label in self.bet_labels.items():
            bet_enum = BetType(bet_type)
            amount = self.game.current_bets.get(bet_enum, 0)
            label.setText(f"下注: ${amount:,.2f}")
        
        # 更新牌面顯示
        if self.game.player_hand:
            player_cards_text = " ".join(str(card) for card in self.game.player_hand)
            self.player_cards.setText(player_cards_text)
            self.player_value.setText(f"點數: {self.game.calculate_hand_value(self.game.player_hand)}")
        else:
            self.player_cards.setText("等待發牌...")
            self.player_value.setText("點數: 0")
        
        if self.game.banker_hand:
            banker_cards_text = " ".join(str(card) for card in self.game.banker_hand)
            self.banker_cards.setText(banker_cards_text)
            self.banker_value.setText(f"點數: {self.game.calculate_hand_value(self.game.banker_hand)}")
        else:
            self.banker_cards.setText("等待發牌...")
            self.banker_value.setText("點數: 0")
    
    def update_history(self):
        """更新遊戲歷史"""
        # 清除現有歷史
        for i in reversed(range(self.history_widget_layout.count())): 
            self.history_widget_layout.itemAt(i).widget().setParent(None)
        
        # 添加最近的5場遊戲
        recent_games = self.game.game_history[-5:]
        for game in reversed(recent_games):
            history_item = QFrame()
            history_item.setStyleSheet("""
                QFrame {
                    background: rgba(255,255,255,0.05);
                    border: 1px solid #8fd3f4;
                    border-radius: 5px;
                    padding: 5px;
                    margin: 2px;
                }
            """)
            
            item_layout = QVBoxLayout(history_item)
            item_layout.setSpacing(3)
            
            winner = {"player": "閒家勝", "banker": "莊家勝", "tie": "和局"}[game["result"]]
            result_label = QLabel(f"{winner} | 獲得: ${game['winnings']:,.2f}")
            result_label.setStyleSheet("font-size: 12px; font-weight: 700; color: #FFD700;")
            
            details_label = QLabel(f"閒家: {game['player_value']} | 莊家: {game['banker_value']}")
            details_label.setStyleSheet("font-size: 10px; color: #e0e0e0;")
            
            item_layout.addWidget(result_label)
            item_layout.addWidget(details_label)
            
            self.history_widget_layout.addWidget(history_item)
        
        # 添加伸縮項
        self.history_widget_layout.addStretch() 