import os
from sqlmodel import Session, SQLModel, create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trading_bot.db")

# Use check_same_thread=False for SQLite + FastAPI
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

def create_db_and_tables():
    from . import models  # Ensure models are imported to register with SQLModel
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
