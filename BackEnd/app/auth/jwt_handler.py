from fastapi import FastAPI, Depends, HTTPException,  APIRouter
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

router = APIRouter()

load_dotenv()  

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def generate_token(user,user_id):
    expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": user, "exp": expire,"id":user_id}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(token)
    return {"access_token": token, "token_type": "bearer"}
    
def token_validation(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        id=payload.get("id")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": username,"id":id}  