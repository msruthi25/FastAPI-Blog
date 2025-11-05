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
    published:bool
    created_at:datetime

class PostModel(BaseModel):  #Creating Post
    title:str
    content:str
    author_id:int
    published:bool


class Comments(BaseModel):  #Add Comments
    post_id:int
    user_id:int
    content:str


