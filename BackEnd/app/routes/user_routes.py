from fastapi import APIRouter, Depends, HTTPException, Request
from ..model import User
from sqlalchemy.orm import Session
from ..databaseSetup import get_db
from ..schemas import UserCreate, UserLogin

router = APIRouter() 
@router.get("/")
def greet():
    return "Home page"

@router.post("/login")
def login(user:UserLogin,db: Session = Depends(get_db)):
    user_data= db.query(User).filter(User.email == user.email).first()
    if not user_data or  user_data.email==user.email:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.password_hash == user_data.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return "Login success"

@router.post("/register")
async def register(user: UserCreate ,db: Session = Depends(get_db)):
    user=User(username=user.username, email=user.email,password_hash=user.password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return "Data recieved"



