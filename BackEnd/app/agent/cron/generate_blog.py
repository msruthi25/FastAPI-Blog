from app.logger.logger import log
from dotenv import load_dotenv
load_dotenv("C:/Users/sruth/Desktop/AI course/FastAPI_Blog/BackEnd/.env")
import random
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.databaseSetup import AsyncSessionLocal
from fastapi import APIRouter, Depends, HTTPException, Request
from app.model import User
from sqlalchemy.future import select
from app.agent.agent_routes import generate_blog
from sqlalchemy.exc import SQLAlchemyError

TOPICS = [
    "Artificial Intelligence in Healthcare",
    "Machine Learning Model Deployment",
    "Edge Computing vs Cloud Computing",
    "Cybersecurity Best Practices in 2026",
    "Natural Language Processing (NLP) Applications",
    "Blockchain Beyond Cryptocurrency",
    "Data Engineering: ETL vs ELT",
    "Serverless Architecture Explained",
    "How to Build a Scalable API",
    "DevOps Automation with CI/CD Pipelines"
]

async def get_system_user(db):
    try:
        result= await db.execute(select(User).filter(User.email == 'admin@gmail.com'))
        user_data = result.scalar_one_or_none()
        print(user_data)
        return user_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error {str(e)}")


async def generate_content():
    log.info("Cron job started", status="initiated")    
    try:
        async with AsyncSessionLocal() as db:
            try:
                system_user = await get_system_user(db)
                if not system_user:
                    log.error("Cron job failed: System user not found in database")
                    return 
            except SQLAlchemyError as e:
                log.error("Database error while fetching system user", error=str(e))
                return

            topic = random.choice(TOPICS)
            user_data = {"username": system_user.username, "id": system_user.id}            
            log.info("Generating blog for topic", topic=topic, user=user_data["username"])

            try:
                await generate_blog(topic, user_data, db)
                log.info("Cron job completed successfully", topic=topic)
                
            except Exception as e:
                log.error("AI Generation failed", topic=topic, error=str(e))
                await db.rollback() 

    except Exception as e:
        log.critical("Unexpected error in cron job lifecycle", error=str(e))
