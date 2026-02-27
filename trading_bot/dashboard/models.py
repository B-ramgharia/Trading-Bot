from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    trades: list["Trade"] = Relationship(back_populates="user")

class Trade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True)
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: str
    executed_qty: float = 0.0
    avg_price: float = 0.0
    order_id: Optional[int] = None
    client_order_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign Key
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="trades")

class UserCreate(SQLModel):
    username: str
    password: str

class UserRead(SQLModel):
    id: int
    username: str
    created_at: datetime

class TradeCreate(SQLModel):
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    notes: Optional[str] = None

class TradeRead(SQLModel):
    id: int
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: str
    executed_qty: float
    avg_price: float
    notes: Optional[str]
    created_at: datetime
