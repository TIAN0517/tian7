from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Jy技術團隊 遊戲帝國API",
    description="23款經典遊戲 + USDT系統 + 企業級安全",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "歡迎使用 Jy技術團隊 遊戲帝國API",
        "version": "1.0.0",
        "developer": "TIAN0517"
    } 