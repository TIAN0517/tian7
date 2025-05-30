#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jy技術團隊 獨立USDT系統 v3.0 - API路由層
Author: TIAN0517
Version: 3.0.0
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import Optional, Dict, Any
from decimal import Decimal
import logging
from datetime import datetime

from services.user_service import user_service
from services.transaction_service import transaction_service
from models.database_models import NetworkType, TransactionStatus

# 配置日誌
logger = logging.getLogger(__name__)

# 創建FastAPI應用
app = FastAPI(
    title="Jy技術團隊 獨立USDT系統",
    description="USDT充值積分系統API",
    version="3.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 密碼Bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 依賴函數：驗證JWT令牌
async def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    user_id = user_service.verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="無效的認證令牌"
        )
    return user_id

# 用戶相關路由
@app.post("/api/v1/users/register")
async def register_user(
    username: str,
    password: str,
    email: str,
    phone: Optional[str] = None
) -> Dict[str, Any]:
    """註冊新用戶"""
    success, message, data = user_service.register(
        username=username,
        password=password,
        email=email,
        phone=phone
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "data": data}

@app.post("/api/v1/users/login")
async def login_user(
    username: str,
    password: str
) -> Dict[str, Any]:
    """用戶登錄"""
    success, message, data = user_service.login(
        username=username,
        password=password
    )
    if not success:
        raise HTTPException(status_code=401, detail=message)
    return {"message": message, "data": data}

@app.post("/api/v1/users/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """修改密碼"""
    success, message = user_service.change_password(
        user_id=user_id,
        old_password=old_password,
        new_password=new_password
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@app.post("/api/v1/users/reset-password")
async def reset_password(email: str) -> Dict[str, Any]:
    """重置密碼"""
    success, message = user_service.reset_password(email=email)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@app.get("/api/v1/users/info")
async def get_user_info(
    user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """獲取用戶信息"""
    success, message, data = user_service.get_user_info(user_id=user_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "data": data}

# 交易相關路由
@app.post("/api/v1/transactions/deposit")
async def create_deposit(
    network: NetworkType,
    amount: Decimal,
    user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """創建充值交易"""
    success, message, data = transaction_service.create_deposit(
        user_id=user_id,
        network=network,
        amount=amount
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "data": data}

@app.post("/api/v1/transactions/verify")
async def verify_transaction(
    tx_hash: str,
    network: NetworkType,
    user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """驗證交易"""
    success, message, data = transaction_service.verify_transaction(
        tx_hash=tx_hash,
        network=network
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "data": data}

@app.get("/api/v1/transactions/history")
async def get_transaction_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[TransactionStatus] = None,
    user_id: int = Depends(get_current_user)
) -> Dict[str, Any]:
    """獲取交易歷史"""
    success, message, data = transaction_service.get_transaction_history(
        user_id=user_id,
        page=page,
        page_size=page_size,
        status=status
    )
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "data": data}

@app.get("/api/v1/network/status")
async def get_network_status() -> Dict[str, Any]:
    """獲取網絡狀態"""
    success, message, data = transaction_service.get_network_status()
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message, "data": data}

# 健康檢查
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """健康檢查"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0"
    }

# 錯誤處理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局異常處理"""
    logger.error(f"未處理的異常: {str(exc)}")
    return {
        "message": "服務器內部錯誤",
        "detail": str(exc)
    }

# 啟動事件
@app.on_event("startup")
async def startup_event():
    """應用啟動時執行"""
    logger.info("應用啟動")

# 關閉事件
@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉時執行"""
    logger.info("應用關閉") 