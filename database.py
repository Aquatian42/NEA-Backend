from sqlalchemy import create_engine, text, Column, Integer, DateTime, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import datetime
from contextlib import contextmanager

#used to define tables
Base = declarative_base()

#table definitions, objescts of these become records
class Users(Base):
    __tablename__ = "users"
    userID = Column(Integer, primary_key=True, nullable=False, index=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(256), nullable=False)
    password_hash = Column(String, nullable=False)

class UserData(Base):
    __tablename__ = "userdata"
    #will delete these records automatically when users records are deleted.
    userID = Column(Integer, ForeignKey("users.userID", ondelete="CASCADE"), primary_key=True, nullable=False, index=True)
    temperature = Column(String(10), nullable=False, default="degC")
    speed = Column(String(10), nullable=False, default="ms")
    distance = Column(String(10), nullable=False, default="km")
    pressure = Column(String(10), nullable=False, default="pa")

class UserLocations(Base):
    __tablename__ = "userlocations"
    locationID = Column(Integer, primary_key=True, nullable=False, index=True)
    #will delete these records automatically when users records are deleted.
    userID = Column(Integer, ForeignKey("users.userID", ondelete="CASCADE"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String, nullable=True)


class DatabaseManager:
    def __init__(self):
        self.database_url = os.environ.get("DATABASE_URL")

        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    #create tables if they have been deleted
    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def session(self):
        #open and close sessions 
        db = self.SessionLocal()
        try:
            yield db  # returns without finishing execution until actions are complete
            db.commit() # save
        except Exception:
            db.rollback() # cancel operations if error
            raise
        finally:
            db.close() # close database to allow other users to access

#creates database instance to be imported
db = DatabaseManager()