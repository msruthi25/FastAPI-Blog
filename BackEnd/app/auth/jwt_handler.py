from fastapi import FastAPI, Depends, HTTPException,  APIRouter
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from ..config import settings
from ..logger.logger import log
import asyncio

router = APIRouter()

SECRET_KEY =  settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

if not SECRET_KEY or not ALGORITHM or not ACCESS_TOKEN_EXPIRE_MINUTES:
        raise RuntimeError("Missing JWT configuration in environment variables")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def generate_token(user,user_id):
    expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": user, "exp": expire,"id":user_id}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    log.info("Generating access token", user_id=user_id, expires_in=expire)
    return {"access_token": token, "token_type": "bearer"}
    
async def token_validation(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        id=payload.get("id")
        log.info("Generating access token", user_id=id, username=username)
        if username is None:
            log.error("Invalid Token when validation")
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        log.error("Error occured during Token validation")
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": username,"id":id}  