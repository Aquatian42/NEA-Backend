from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import datetime

# 1. SETUP THE CONNECTION URL
# This checks if we are on Render (Postgres) or local (SQLite)
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./test.db"

# 2. THE ENGINE
# This is the actual connection to the database server.
engine = create_engine(DATABASE_URL)

# 3. THE SESSION FACTORY
# This is like a "Machine" that creates temporary workspaces (Sessions) for us.
# Every time we want to talk to the DB, we ask this factory for a new session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. THE BASE
# This is the list that tracks all our tables.
Base = declarative_base()

# 5. THE MODEL (Our Table)
class ClickLog(Base):
    __tablename__ = "click_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
