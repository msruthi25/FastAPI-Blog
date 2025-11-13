from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from ..model import User
from sqlalchemy.orm import Session
from ..databaseSetup import get_db
from ..schemas import UserCreate, UserLogin
from ..auth import jwt_handler,hashing
router = APIRouter() 
@router.get("/")
def greet():
    return "Home page"

@router.post("/login")
def login(user:UserLogin,db: Session = Depends(get_db)):
    user_data= db.query(User).filter(User.email == user.email).first()
    if not user_data or user_data.email!=user.email:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not hashing.verify_password(user.password_hash,user_data.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token=jwt_handler.generate_token(user_data.username,user_data.id)
    return {"access_token":access_token,"username":user_data.username,"user_id":user_data.id}

@router.post("/register")
async def register(user: UserCreate ,db: Session = Depends(get_db)):
    password_hash=hashing.hash_password(user.password_hash)
    user=User(username=user.username, email=user.email,password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return "Data recieved"



