from sqlalchemy import Boolean, Column,DateTime,Integer, String, func, ForeignKey
from sqlalchemy.orm import relationship
from .databaseSetup import  Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True,index=True)
    email = Column(String,unique=True,index=True)
    password_hash=Column(String)
    created_at=Column(DateTime, server_default=func.now())


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String)
    content = Column(String)
    author_id = Column(Integer,ForeignKey("users.id"),index=True)
    img_url=Column(String)
    published =  Column(Boolean, default=True)
    created_at=Column(DateTime, server_default=func.now())
    user = relationship("User")
    comments = relationship(
        "Comment",      
        cascade="all, delete-orphan"
    )

class Comment(Base):
    __tablename__="comments"
    id=Column(Integer,primary_key=True)
    post_id=Column(Integer,ForeignKey("posts.id"))
    user_id=Column(Integer,ForeignKey("users.id"))
    content=Column(String)
    created_at=Column(DateTime, server_default=func.now())
    user = relationship('User')

