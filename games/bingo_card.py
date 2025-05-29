from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class PatternType(Enum):
    """中獎模式類型"""
    SINGLE_LINE = "single_line"
    DOUBLE_LINE = "double_line"
    TRIPLE_LINE = "triple_line"
    QUAD_LINE = "quad_line"
    BLACKOUT = "blackout"
    FOUR_CORNERS = "four_corners"
    X_PATTERN = "x_pattern"

@dataclass
class WinningPattern:
    """中獎模式數據類"""
    type: PatternType
    positions: List[tuple]  # 中獎位置列表
    multiplier: int  # 賠率倍數

class BingoCard:
    """單張賓果卡片邏輯"""
    
    def __init__(self, card_data: List[List[int]]):
        self.numbers = card_data
        self.marked = [[False] * 5 for _ in range(5)]
        self.marked[2][2] = True  # 中央FREE格
        self.winning_patterns: List[WinningPattern] = []
        self.completion_rate = 0.0
        
    def mark_number(self, number: int) -> bool:
        """標記號碼，返回是否找到"""
        found = False
        for i in range(5):
            for j in range(5):
                if self.numbers[i][j] == number:
                    self.marked[i][j] = True
                    found = True
        if found:
            self.update_completion_rate()
        return found
        
    def check_line_win(self) -> List[WinningPattern]:
        """檢查線型中獎"""
        patterns = []
        
        # 檢查行
        for i in range(5):
            if all(self.marked[i]):
                positions = [(i, j) for j in range(5)]
                patterns.append(WinningPattern(
                    PatternType.SINGLE_LINE,
                    positions,
                    5
                ))
                
        # 檢查列
        for j in range(5):
            if all(self.marked[i][j] for i in range(5)):
                positions = [(i, j) for i in range(5)]
                patterns.append(WinningPattern(
                    PatternType.SINGLE_LINE,
                    positions,
                    5
                ))
                
        # 檢查對角線
        if all(self.marked[i][i] for i in range(5)):
            positions = [(i, i) for i in range(5)]
            patterns.append(WinningPattern(
                PatternType.SINGLE_LINE,
                positions,
                5
            ))
            
        if all(self.marked[i][4-i] for i in range(5)):
            positions = [(i, 4-i) for i in range(5)]
            patterns.append(WinningPattern(
                PatternType.SINGLE_LINE,
                positions,
                5
            ))
            
        return patterns
        
    def check_pattern_win(self) -> List[WinningPattern]:
        """檢查圖案中獎"""
        patterns = []
        
        # 檢查四角
        if (self.marked[0][0] and self.marked[0][4] and 
            self.marked[4][0] and self.marked[4][4]):
            positions = [(0, 0), (0, 4), (4, 0), (4, 4)]
            patterns.append(WinningPattern(
                PatternType.FOUR_CORNERS,
                positions,
                25
            ))
            
        # 檢查X型
        if (all(self.marked[i][i] for i in range(5)) and 
            all(self.marked[i][4-i] for i in range(5))):
            positions = [(i, i) for i in range(5)] + [(i, 4-i) for i in range(5)]
            patterns.append(WinningPattern(
                PatternType.X_PATTERN,
                positions,
                75
            ))
            
        # 檢查滿卡
        if all(all(row) for row in self.marked):
            positions = [(i, j) for i in range(5) for j in range(5)]
            patterns.append(WinningPattern(
                PatternType.BLACKOUT,
                positions,
                500
            ))
            
        return patterns
        
    def get_completion_rate(self) -> float:
        """獲取完成率"""
        marked_count = sum(sum(row) for row in self.marked)
        total_cells = 25  # 5x5
        return marked_count / total_cells
        
    def update_completion_rate(self):
        """更新完成率"""
        self.completion_rate = self.get_completion_rate()
        
    def is_blackout(self) -> bool:
        """檢查是否滿卡"""
        return all(all(row) for row in self.marked)
        
    def get_winning_patterns(self) -> List[WinningPattern]:
        """獲取所有中獎模式"""
        self.winning_patterns = []
        
        # 檢查線型中獎
        line_patterns = self.check_line_win()
        self.winning_patterns.extend(line_patterns)
        
        # 檢查圖案中獎
        pattern_wins = self.check_pattern_win()
        self.winning_patterns.extend(pattern_wins)
        
        return self.winning_patterns
        
    def get_highest_multiplier(self) -> int:
        """獲取最高賠率倍數"""
        if not self.winning_patterns:
            return 0
        return max(pattern.multiplier for pattern in self.winning_patterns)
        
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            "numbers": self.numbers,
            "marked": self.marked,
            "completion_rate": self.completion_rate,
            "winning_patterns": [
                {
                    "type": pattern.type.value,
                    "positions": pattern.positions,
                    "multiplier": pattern.multiplier
                }
                for pattern in self.winning_patterns
            ]
        } 