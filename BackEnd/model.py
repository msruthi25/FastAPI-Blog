from sqlalchemy import Column,DateTime,Integer, String, func
from databaseSetup import  Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True)
    username = Column(String,unique=True)
    email = Column(String)
    password_hash=Column(String)
    created_at=Column(DateTime, server_default=func.now())


    