"""
遊戲數據定義模塊
定義所有 23 款遊戲的基礎信息
"""

from typing import List, Dict, Any

# 完整的 23 款遊戲信息
ALL_GAMES_INFO: List[Dict[str, Any]] = [
    # 撲克類遊戲 (9款)
    {
        "id": "baccarat",
        "name": "百家樂",
        "category": "card_games",
        "icon": "🎴",
        "description": "經典賭場撲克遊戲，比拚莊家與閒家",
        "module_name": "card_games.baccarat",
        "class_name": "BaccaratGameLogic",
        "min_bet": 10,
        "max_bet": 10000,
        "rtp": 98.94,
        "image_path": "assets/images/games/baccarat.png"
    },
    {
        "id": "poker_texas_holdem",
        "name": "德州撲克",
        "category": "card_games",
        "icon": "♠️",
        "description": "世界最受歡迎的撲克變體",
        "module_name": "card_games.poker",
        "class_name": "TexasHoldemLogic",
        "min_bet": 20,
        "max_bet": 5000,
        "rtp": 97.5,
        "image_path": "assets/images/games/texas_holdem.png"
    },
    {
        "id": "three_card_brag",
        "name": "三公",
        "category": "card_games",
        "icon": "🃏",
        "description": "傳統中式撲克遊戲",
        "module_name": "card_games.three_card_brag",
        "class_name": "ThreeCardBragLogic",
        "min_bet": 5,
        "max_bet": 2000,
        "rtp": 96.8,
        "image_path": "assets/images/games/three_card_brag.png"
    },
    {
        "id": "dragon_tiger",
        "name": "龍虎鬥",
        "category": "card_games",
        "icon": "🐲",
        "description": "簡單刺激的比牌遊戲",
        "module_name": "card_games.dragon_tiger",
        "class_name": "DragonTigerLogic",
        "min_bet": 10,
        "max_bet": 8000,
        "rtp": 96.27,
        "image_path": "assets/images/games/dragon_tiger.png"
    },
    {
        "id": "red_dog",
        "name": "紅狗",
        "category": "card_games",
        "icon": "🐕",
        "description": "預測牌值範圍的撲克遊戲",
        "module_name": "card_games.red_dog",
        "class_name": "RedDogLogic",
        "min_bet": 10,
        "max_bet": 3000,
        "rtp": 97.2,
        "image_path": "assets/images/games/red_dog.png"
    },
    {
        "id": "stud_poker",
        "name": "梭哈",
        "category": "card_games",
        "icon": "💰",
        "description": "經典五張牌梭哈撲克",
        "module_name": "card_games.stud_poker",
        "class_name": "StudPokerLogic",
        "min_bet": 25,
        "max_bet": 6000,
        "rtp": 98.1,
        "image_path": "assets/images/games/stud_poker.png"
    },
    {
        "id": "big_two",
        "name": "大老二",
        "category": "card_games",
        "icon": "✌️",
        "description": "策略性出牌競技遊戲",
        "module_name": "card_games.big_two",
        "class_name": "BigTwoLogic",
        "min_bet": 5,
        "max_bet": 1000,
        "rtp": 95.5,
        "image_path": "assets/images/games/big_two.png"
    },
    {
        "id": "red_black_war",
        "name": "紅黑大戰",
        "category": "card_games",
        "icon": "⚔️",
        "description": "紅黑兩色對決遊戲",
        "module_name": "card_games.red_black_war",
        "class_name": "RedBlackWarLogic",
        "min_bet": 10,
        "max_bet": 5000,
        "rtp": 97.3,
        "image_path": "assets/images/games/red_black_war.png"
    },
    {
        "id": "caribbean_stud",
        "name": "加勒比海撲克",
        "category": "card_games",
        "icon": "🏝️",
        "description": "對戰莊家的五張牌撲克",
        "module_name": "card_games.caribbean_stud",
        "class_name": "CaribbeanStudLogic",
        "min_bet": 15,
        "max_bet": 4000,
        "rtp": 97.8,
        "image_path": "assets/images/games/caribbean_stud.png"
    },
    
    # 骰子類遊戲 (2款)
    {
        "id": "sicbo",
        "name": "骰寶",
        "category": "dice_games",
        "icon": "🎲",
        "description": "預測三顆骰子點數組合",
        "module_name": "dice_games.sicbo",
        "class_name": "SicBoLogic",
        "min_bet": 5,
        "max_bet": 8000,
        "rtp": 97.22,
        "image_path": "assets/images/games/sicbo.png"
    },
    {
        "id": "craps",
        "name": "花旗骰",
        "category": "dice_games",
        "icon": "🎰",
        "description": "西式骰子賭博遊戲",
        "module_name": "dice_games.craps",
        "class_name": "CrapsLogic",
        "min_bet": 10,
        "max_bet": 6000,
        "rtp": 98.6,
        "image_path": "assets/images/games/craps.png"
    },
    
    # 輪盤類遊戲 (1款)
    {
        "id": "roulette",
        "name": "歐式輪盤",
        "category": "wheel_games",
        "icon": "🎯",
        "description": "經典歐式輪盤，0-36號碼",
        "module_name": "wheel_games.roulette",
        "class_name": "RouletteGameLogic",
        "min_bet": 10,
        "max_bet": 10000,
        "rtp": 97.3,
        "image_path": "assets/images/games/roulette.png"
    },
    
    # 老虎機類遊戲 (4款)
    {
        "id": "god_of_war_slots",
        "name": "戰神賽特",
        "category": "slots_games",
        "icon": "⚡",
        "description": "古埃及戰神主題老虎機",
        "module_name": "slots_games.god_of_war",
        "class_name": "GodOfWarSlotsLogic",
        "min_bet": 1,
        "max_bet": 500,
        "rtp": 96.71,
        "image_path": "assets/images/games/god_of_war.png"
    },
    {
        "id": "thors_hammer_slots",
        "name": "雷神之槌",
        "category": "slots_games",
        "icon": "🔨",
        "description": "北歐雷神主題老虎機",
        "module_name": "slots_games.thors_hammer",
        "class_name": "ThorsHammerSlotsLogic",
        "min_bet": 1,
        "max_bet": 400,
        "rtp": 96.98,
        "image_path": "assets/images/games/thors_hammer.png"
    },
    {
        "id": "mahjong_wins_slots",
        "name": "麻將發了",
        "category": "slots_games",
        "icon": "🀄",
        "description": "中式麻將主題老虎機",
        "module_name": "slots_games.mahjong_wins",
        "class_name": "MahjongWinsSlotsLogic",
        "min_bet": 1,
        "max_bet": 300,
        "rtp": 96.52,
        "image_path": "assets/images/games/mahjong_wins.png"
    },
    {
        "id": "wealth_god_slots",
        "name": "聚寶財神",
        "category": "slots_games",
        "icon": "🧧",
        "description": "財神爺主題老虎機",
        "module_name": "slots_games.wealth_god",
        "class_name": "WealthGodSlotsLogic",
        "min_bet": 1,
        "max_bet": 600,
        "rtp": 97.15,
        "image_path": "assets/images/games/wealth_god.png"
    },
    
    # 彩票類遊戲 (2款)
    {
        "id": "bingo",
        "name": "賓果",
        "category": "lottery_games",
        "icon": "🔢",
        "description": "經典數字對獎遊戲",
        "module_name": "lottery_games.bingo",
        "class_name": "BingoLogic",
        "min_bet": 5,
        "max_bet": 200,
        "rtp": 95.8,
        "image_path": "assets/images/games/bingo.png"
    },
    {
        "id": "keno",
        "name": "Keno",
        "category": "lottery_games",
        "icon": "🎟️",
        "description": "選號彩票式遊戲",
        "module_name": "lottery_games.keno",
        "class_name": "KenoLogic",
        "min_bet": 1,
        "max_bet": 100,
        "rtp": 95.0,
        "image_path": "assets/images/games/keno.png"
    },
    
    # 模擬類遊戲 (3款)
    {
        "id": "horse_racing",
        "name": "賽馬",
        "category": "simulation_games",
        "icon": "🐎",
        "description": "虛擬賽馬投注模擬",
        "module_name": "simulation_games.horse_racing",
        "class_name": "HorseRacingLogic",
        "min_bet": 10,
        "max_bet": 2000,
        "rtp": 96.5,
        "image_path": "assets/images/games/horse_racing.png"
    },
    {
        "id": "happy_farm",
        "name": "開心農場",
        "category": "simulation_games",
        "icon": "👨‍🌾",
        "description": "農場經營模擬遊戲",
        "module_name": "simulation_games.happy_farm",
        "class_name": "HappyFarmLogic",
        "min_bet": 5,
        "max_bet": 500,
        "rtp": 94.2,
        "image_path": "assets/images/games/happy_farm.png"
    },
    {
        "id": "fishing_game",
        "name": "捕魚機",
        "category": "simulation_games",
        "icon": "🎣",
        "description": "技巧射擊捕魚遊戲",
        "module_name": "simulation_games.fishing_game",
        "class_name": "FishingGameLogic",
        "min_bet": 1,
        "max_bet": 1000,
        "rtp": 96.8,
        "image_path": "assets/images/games/fishing_game.png"
    },
    
    # 主題類遊戲 (2款)
    {
        "id": "ragnarok_themed",
        "name": "仙境傳說",
        "category": "themed_games",
        "icon": "⚔️",
        "description": "RO主題冒險RPG遊戲",
        "module_name": "themed_games.ragnarok",
        "class_name": "RagnarokThemedLogic",
        "min_bet": 10,
        "max_bet": 1500,
        "rtp": 95.9,
        "image_path": "assets/images/games/ragnarok.png"
    },
    {
        "id": "martial_arts_themed",
        "name": "武俠風雲",
        "category": "themed_games",
        "icon": "🥋",
        "description": "武俠世界主題遊戲",
        "module_name": "themed_games.martial_arts",
        "class_name": "MartialArtsThemedLogic",
        "min_bet": 5,
        "max_bet": 800,
        "rtp": 95.7,
        "image_path": "assets/images/games/martial_arts.png"
    },
    
    # 傳統遊戲 (1款)
    {
        "id": "erbakan",
        "name": "二八扛",
        "category": "traditional_games",
        "icon": "🀄",
        "description": "傳統中式牌類遊戲",
        "module_name": "traditional_games.erbakan",
        "class_name": "ErbakanLogic",
        "min_bet": 10,
        "max_bet": 3000,
        "rtp": 96.1,
        "image_path": "assets/images/games/erbakan.png"
    }
]

# 按類別分組的遊戲信息
GAMES_BY_CATEGORY = {
    "card_games": [game for game in ALL_GAMES_INFO if game["category"] == "card_games"],
    "dice_games": [game for game in ALL_GAMES_INFO if game["category"] == "dice_games"],
    "wheel_games": [game for game in ALL_GAMES_INFO if game["category"] == "wheel_games"],
    "slots_games": [game for game in ALL_GAMES_INFO if game["category"] == "slots_games"],
    "lottery_games": [game for game in ALL_GAMES_INFO if game["category"] == "lottery_games"],
    "simulation_games": [game for game in ALL_GAMES_INFO if game["category"] == "simulation_games"],
    "themed_games": [game for game in ALL_GAMES_INFO if game["category"] == "themed_games"],
    "traditional_games": [game for game in ALL_GAMES_INFO if game["category"] == "traditional_games"]
}

# 遊戲總數驗證
assert len(ALL_GAMES_INFO) == 24, f"遊戲總數應為24款，當前為{len(ALL_GAMES_INFO)}款"

def get_game_by_id(game_id: str) -> Dict[str, Any]:
    """根據遊戲ID獲取遊戲信息"""
    for game in ALL_GAMES_INFO:
        if game["id"] == game_id:
            return game
    raise ValueError(f"找不到ID為 {game_id} 的遊戲")

def get_games_by_category(category: str) -> List[Dict[str, Any]]:
    """根據類別獲取遊戲列表"""
    return GAMES_BY_CATEGORY.get(category, [])

def get_all_categories() -> List[str]:
    """獲取所有遊戲類別"""
    return list(GAMES_BY_CATEGORY.keys())