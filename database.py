from sqlalchemy import create_engine, text, Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import datetime
from typing import Generator

Base = declarative_base()

class ClickLog(Base):
    __tablename__ = "click_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Database:
    def __init__(self):
        # Render provides the DATABASE_URL environment variable.
        self.database_url = os.environ.get("DATABASE_URL")
        if self.database_url and self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
        
        if not self.database_url:
            self.database_url = "sqlite:///./test.db"
            print("WARNING: DATABASE_URL not found, falling back to local SQLite.")

        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_all(self):
        """Creates all tables defined in the Base metadata."""
        Base.metadata.create_all(bind=self.engine)

    def get_db(self) -> Generator[Session, None, None]:
        """Dependency to get a database session."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def test_connection(self):
        """Simple health check for the database."""
        try:
            with self.SessionLocal() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False

# Create a singleton instance to be used across the app
db_manager = Database()