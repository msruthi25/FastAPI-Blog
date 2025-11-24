from passlib.context import CryptContext
from ..logger.logger import log
import asyncio

pwd_context=CryptContext(schemes=["argon2"], deprecated="auto")

async def hash_password(password:str):
    log.info("Password hashing completed")
    return await asyncio.to_thread(pwd_context.hash, password)

async def verify_password(plain_password:str,hashed_password:str):
    log.info("Password hash verification completed")
    return await asyncio.to_thread(pwd_context.verify, plain_password, hashed_password)

