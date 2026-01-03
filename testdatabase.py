from sqlalchemy import create_engine, text, Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import datetime
from contextlib import contextmanager

Base = declarative_base()

#Table definitions
class ClickLog(Base):
    __tablename__ = "click_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class DatabaseManager:
    def __init__(self):
        self.database_url = os.environ.get("DATABASE_URL")
        if self.database_url and self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
        
        if not self.database_url:
            self.database_url = "sqlite:///./test.db"

        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def session(self):
        #open and close sessions 
        db = self.SessionLocal()
        try:
            yield db  # returns without finishing execution
            db.commit() # Auto-save if no errors
        except Exception:
            db.rollback() # Auto-cancel if there's an error
            raise
        finally:
            db.close() # Auto-close always

#creates database instance to be imported
dbtest = DatabaseManager()
