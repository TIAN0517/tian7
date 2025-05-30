# RanOnline 遊戲啟動器

一個具有史詩奇幻風格和現代科技感的遊戲啟動器，為 RanOnline 玩家提供極致的遊戲體驗。

## 🎯 特色功能

- **史詩奇幻風格**：融合經典遊戲元素與現代UI設計
- **沉浸式體驗**：高品質影片播放與動畫效果
- **多樣化功能**：主遊戲、娛樂城、裝備市場、USDT充值、排行榜
- **企業級品質**：穩定、安全、高效的運行環境

## 🚀 快速開始

### 環境要求

- Python 3.8+
- PyQt5
- 其他依賴見 requirements.txt

### 安裝步驟

1. 克隆專案
```bash
git clone https://github.com/your-username/ranonline-launcher.git
cd ranonline-launcher
```

2. 創建虛擬環境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安裝依賴
```bash
pip install -r requirements.txt
```

4. 運行應用
```bash
python src/core/application.py
```

## 📁 專案結構

```
src/
├── core/                   # 核心模塊
│   ├── application.py      # 主應用程式
│   ├── config.py          # 配置管理
│   ├── database.py        # 數據庫連接
│   └── network.py         # 網路管理
├── ui/                    # UI 模塊
│   ├── main_window.py     # 主視窗
│   ├── tabs/              # 分頁模塊
│   │   ├── home_tab.py    # 主遊戲首頁
│   │   ├── casino_tab.py  # 娛樂城
│   │   ├── market_tab.py  # 裝備市場
│   │   ├── recharge_tab.py # USDT充值
│   │   └── ranking_tab.py # 排行榜
│   ├── widgets/           # 自訂控件
│   └── resources/         # UI 資源
├── services/              # 業務邏輯
└── utils/                 # 工具模塊
```

## 🎨 設計規範

### 色彩系統

- **主遊戲區域**
  - 深空背景: #0a0a0a
  - 戰場深藍: #1a2238
  - 傳奇金色: #FFD700
  - 魔法紫色: #7B2FF2

- **娛樂城區域**
  - 奢華黑金: #23243a
  - 酒紅絲絨: #B31217
  - 香檳金色: #F7E7CE
  - 翡翠綠色: #2ecc71

### 字體系統

- **主要字體**
  - Noto Sans TC
  - Microsoft JhengHei
  - PingFang TC
  - Helvetica Neue

- **遊戲字體**
  - Orbitron
  - Rajdhani
  - Exo 2

## 🔧 開發指南

### 代碼風格

- 遵循 PEP 8 規範
- 使用 Black 進行代碼格式化
- 使用 isort 進行導入排序
- 使用 flake8 進行代碼檢查
- 使用 mypy 進行類型檢查

### 測試

```bash
# 運行所有測試
pytest

# 運行帶覆蓋率的測試
pytest --cov=src tests/

# 運行 UI 測試
pytest tests/ui/
```

## 📝 版本歷史

- v1.0.0 (2024-03-xx)
  - 初始版本發布
  - 實現核心功能
  - 完成基礎UI設計

## 🤝 貢獻指南

1. Fork 專案
2. 創建特性分支
3. 提交更改
4. 推送到分支
5. 創建 Pull Request

## 📄 授權協議

本專案採用 MIT 授權協議 - 詳見 [LICENSE](LICENSE) 文件
