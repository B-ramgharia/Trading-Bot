"""
app.py
------
FastAPI dashboard backend for the Binance Futures Testnet trading bot.

Provides REST API endpoints for:
  - Account information
  - Order placement (MARKET, LIMIT, STOP_MARKET, STOP)
  - Open order listing / cancellation
  - Server connectivity check

Also serves the static HTML/CSS/JS dashboard.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from pydantic import BaseModel
import os

from trading_bot.bot.client import BinanceFuturesClient, BinanceAPIError
from trading_bot.bot.logging_config import setup_logging, get_logger
from trading_bot.bot.orders import OrderManager
from trading_bot.bot.validators import validate_all

from .database import engine, get_session, create_db_and_tables
from .models import User, Trade, UserCreate, UserRead, TradeCreate, TradeRead
from .auth import verify_password, get_password_hash, create_access_token, decode_access_token

load_dotenv()
setup_logging()
logger = get_logger("dashboard")

# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Trading Bot Dashboard",
    description="Binance Futures Testnet – Trading Bot Dashboard API",
    version="1.1.0",
)

# ── Database Initialization ────────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ── Initialise client ─────────────────────────────────────────────────────────

API_KEY = os.getenv("BINANCE_API_KEY", "").strip()
API_SECRET = os.getenv("BINANCE_API_SECRET", "").strip()

if not API_KEY or not API_SECRET:
    logger.warning(
        "BINANCE_API_KEY / BINANCE_API_SECRET not set. "
        "Dashboard will return errors for authenticated endpoints."
    )

client = BinanceFuturesClient(api_key=API_KEY, api_secret=API_SECRET)
order_manager = OrderManager(client)

# ── Middlewares ──────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication logic
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session)
) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Serve static files only if the directory exists
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Pydantic models ──────────────────────────────────────────────────────────


# ── Auth Routes ─────────────────────────────────────────────────────────────

@app.post("/api/auth/signup", response_model=UserRead)
async def signup(user_in: UserCreate, session: Session = Depends(get_session)):
    """Register a new user."""
    # Check if user exists
    statement = select(User).where(User.username == user_in.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pw = get_password_hash(user_in.password)
    new_user = User(username=user_in.username, hashed_password=hashed_pw)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@app.post("/api/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session)
):
    """Log in and get an access token."""
    statement = select(User).where(User.username == form_data.username)
    user = session.exec(statement).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user

# ── Order Params Model (Replacement for Pydantic model) ───────────────────
class OrderRequest(BaseModel):
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = "GTC"
    notes: Optional[str] = None  # Added notes for journal

class CancelRequest(BaseModel):
    symbol: str
    order_id: int


# ── Routes ────────────────────────────────────────────────────────────────────


@app.get("/")
async def dashboard():
    """Serve the main dashboard HTML page."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/ping")
async def ping():
    """Check if Binance Testnet is reachable."""
    try:
        ok = client.ping()
        return {"status": "ok" if ok else "unreachable"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


@app.get("/api/account")
async def account_info():
    """Get account balance and position information."""
    try:
        data = client.get_account_info()

        # Extract relevant balances (non-zero)
        balances = [
            {
                "asset": b["asset"],
                "balance": b["balance"],
                "availableBalance": b["availableBalance"],
                "unrealizedProfit": b.get("crossUnPnl", "0"),
            }
            for b in data.get("assets", [])
            if float(b.get("balance", 0)) != 0
        ]

        # Extract open positions (non-zero)
        positions = [
            {
                "symbol": p["symbol"],
                "positionAmt": p["positionAmt"],
                "entryPrice": p["entryPrice"],
                "unrealizedProfit": p["unrealizedProfit"],
                "leverage": p.get("leverage", "1"),
                "positionSide": p.get("positionSide", "BOTH"),
            }
            for p in data.get("positions", [])
            if float(p.get("positionAmt", 0)) != 0
        ]

        return {
            "totalWalletBalance": data.get("totalWalletBalance", "0"),
            "totalUnrealizedProfit": data.get("totalUnrealizedProfit", "0"),
            "availableBalance": data.get("availableBalance", "0"),
            "balances": balances,
            "positions": positions,
        }
    except BinanceAPIError as exc:
        raise HTTPException(status_code=400, detail=f"[{exc.code}] {exc.message}")
    except Exception as exc:
        logger.exception("Account info error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/order")
async def place_order(
    req: OrderRequest, 
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Place a new order and save to journal."""
    try:
        validated = validate_all(
            symbol=req.symbol,
            side=req.side,
            order_type=req.order_type,
            quantity=req.quantity,
            price=req.price,
            stop_price=req.stop_price,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    try:
        symbol = validated["symbol"]
        side = validated["side"]
        qty = validated["quantity"]
        price = validated["price"]
        stop_price = validated["stop_price"]
        order_type = validated["order_type"]

        if order_type == "MARKET":
            result = order_manager.place_market_order(symbol, side, qty)
        elif order_type == "LIMIT":
            result = order_manager.place_limit_order(
                symbol, side, qty, price, time_in_force=req.time_in_force
            )
        elif order_type in ("STOP_MARKET", "STOP"):
            result = order_manager.place_stop_order(symbol, side, qty, stop_price, price)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported type: {order_type}")

        # Save to trade journal
        new_trade = Trade(
            user_id=current_user.id,
            symbol=result.symbol,
            side=result.side,
            order_type=result.order_type,
            quantity=float(result.orig_qty),
            price=float(result.price) if result.price != "0" else None,
            stop_price=float(stop_price) if stop_price else None,
            status=result.status,
            executed_qty=float(result.executed_qty),
            avg_price=float(result.avg_price),
            order_id=result.order_id,
            client_order_id=result.client_order_id,
            notes=req.notes
        )
        session.add(new_trade)
        session.commit()
        session.refresh(new_trade)

        return {
            "success": True,
            "order": {
                "orderId": result.order_id,
                "clientOrderId": result.client_order_id,
                "symbol": result.symbol,
                "side": result.side,
                "type": result.order_type,
                "status": result.status,
                "origQty": result.orig_qty,
                "executedQty": result.executed_qty,
                "avgPrice": result.avg_price,
                "price": result.price,
            },
            "trade_id": new_trade.id
        }
    except BinanceAPIError as exc:
        raise HTTPException(status_code=400, detail=f"[{exc.code}] {exc.message}")
    except Exception as exc:
        logger.exception("Order placement error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── Journal Routes ──────────────────────────────────────────────────────────

@app.get("/api/journal", response_model=List[TradeRead])
async def get_journal(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Fetch user's trade journal."""
    statement = select(Trade).where(Trade.user_id == current_user.id).order_by(Trade.created_at.desc())
    trades = session.exec(statement).all()
    return trades

@app.patch("/api/journal/{trade_id}", response_model=TradeRead)
async def update_journal_entry(
    trade_id: int,
    notes: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update notes for a journal entry."""
    trade = session.get(Trade, trade_id)
    if not trade or trade.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    trade.notes = notes
    session.add(trade)
    session.commit()
    session.refresh(trade)
    return trade

@app.delete("/api/journal/{trade_id}")
async def delete_journal_entry(
    trade_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a journal entry."""
    trade = session.get(Trade, trade_id)
    if not trade or trade.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    session.delete(trade)
    session.commit()
    return {"success": True}


@app.get("/api/open-orders")
async def open_orders(
    symbol: str = "", 
    current_user: User = Depends(get_current_user)
):
    """Get all open orders, optionally filtered by symbol."""
    try:
        params = {}
        if symbol:
            params["symbol"] = symbol.upper()
        data = client._request("GET", "/fapi/v1/openOrders", params=params)
        orders = [
            {
                "orderId": o.get("orderId"),
                "symbol": o.get("symbol"),
                "side": o.get("side"),
                "type": o.get("type"),
                "status": o.get("status"),
                "price": o.get("price"),
                "origQty": o.get("origQty"),
                "executedQty": o.get("executedQty"),
                "stopPrice": o.get("stopPrice", "0"),
                "time": o.get("time"),
            }
            for o in (data if isinstance(data, list) else [])
        ]
        return {"orders": orders}
    except BinanceAPIError as exc:
        raise HTTPException(status_code=400, detail=f"[{exc.code}] {exc.message}")
    except Exception as exc:
        logger.exception("Open orders error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/api/order")
async def cancel_order_api(
    req: CancelRequest, 
    current_user: User = Depends(get_current_user)
):
    """Cancel an open order."""
    try:
        data = client.cancel_order(req.symbol.upper(), req.order_id)
        return {"success": True, "result": data}
    except BinanceAPIError as exc:
        raise HTTPException(status_code=400, detail=f"[{exc.code}] {exc.message}")
    except Exception as exc:
        logger.exception("Cancel order error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/exchange-info")
async def exchange_info():
    """Get exchange trading rules (Unprotected for frontend init)."""
    try:
        data = client.get_exchange_info()
        symbols = [
            {
                "symbol": s["symbol"],
                "baseAsset": s.get("baseAsset", ""),
                "quoteAsset": s.get("quoteAsset", ""),
                "status": s.get("status", ""),
            }
            for s in data.get("symbols", [])
            if s.get("status") == "TRADING"
        ]
        return {"symbols": symbols}
    except Exception as exc:
        logger.exception("Exchange info error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
