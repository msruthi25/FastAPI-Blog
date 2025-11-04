from fastapi import Depends
from main import app
from model import User
from sqlalchemy.orm import Session
from databaseSetup import get_db


@app.get("/")
def greet():
    return "Home page"

@app.get("/login")
def login():
    return "Login page"



@app.post("/register")
def register(db: Session = Depends(get_db)):
    user=User(username="Sruthi", email="sruthi@gmail.com",  password_hash="Sruthi")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user