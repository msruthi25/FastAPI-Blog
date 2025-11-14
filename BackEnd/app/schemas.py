from typing import Optional
from pydantic import BaseModel,EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    username : str
    email : EmailStr
    password_hash : str

class UserLogin(BaseModel):
    email: EmailStr
    password_hash : str  

class PostResponse(BaseModel):  #Sending post responses
    id: int
    title:str
    content:str
    author_id:int
    img_url:str
    published:bool
    created_at:datetime

class PostModel(BaseModel):  #Creating Post
    title:str
    content:str
    img_url:str
    published:bool

class Comments(BaseModel):  #Add Comments
    content:str

class CommentsResponse(BaseModel):
    id: int
    content: str
    username: str    
    created_at:datetime

class PostUpdateModel(BaseModel):
    title:str
    content:str
    img_url:str
    author_id:int
