from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from ..model import User
from sqlalchemy.orm import Session
from ..databaseSetup import get_db
from ..schemas import UserCreate, UserLogin
from ..auth import jwt_handler,hashing
from ..logger.logger import log
import asyncio
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..limiter import limiter

router = APIRouter() 




@router.get("/")
async def greet():
    return {"message": "Home page"}

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, user: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(User).filter(User.email == user.email))
        user_data = result.scalar_one_or_none()

        if not user_data or user_data.email != user.email:
            log.warning("Login failed: user not found or email mismatch", email=user.email)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        password_valid = await hashing.verify_password(user.password, user_data.password_hash)     
        if not password_valid:
            log.warning("Login failed: incorrect password", email=user.email, user_id=user_data.id)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = await jwt_handler.generate_token(user_data.username, user_data.id)
        log.info("User logged in successfully", username=user_data.username, user_id=user_data.id)
        return {"access_token": access_token, "username": user_data.username, "user_id": user_data.id}
    except HTTPException:
        raise
    except Exception as e:
        log.error("Internal server error during login", email=user.email, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal Server Error {str(e)}")


@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        password_hash = await hashing.hash_password(user.password)
        new_user = User(username=user.username, email=user.email, password_hash=password_hash)

        result = await db.execute(select(User).filter_by(email=user.email))
        exists = result.scalar_one_or_none()
        if exists:
            log.warning("Registration failed: email already exists", email=user.email)
            raise HTTPException(status_code=409, detail="Email already exists")

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        log.info("User registered successfully", username=new_user.username, email=new_user.email, user_id=new_user.id)
        return {"status": "success", "message": "User registered successfully"}
    except HTTPException:
        raise

    except Exception as e:
        log.error("Internal server error during registration", email=user.email, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal server error {str(e)}")





