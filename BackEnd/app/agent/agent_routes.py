from fastapi import APIRouter,Depends, HTTPException
from pydantic import BaseModel
from .graph import build_graph
from ..schemas import AIResponse, PostModel
from ..routes.posts_routes import create_post_service
from ..databaseSetup import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth.jwt_handler import token_validation


router=APIRouter()

class AgentInput(BaseModel):
    input: str


#auto_generate_blog()    
async def generate_blog(input:AgentInput, current_user:dict , db: AsyncSession = Depends(get_db) ):
    app = build_graph()
    output= app.invoke({"topic": input ,"prompt": "{}"})
    post = PostModel(
        title=output.get("title"),
        content=output.get("content"),
        img_url=output.get("img_url")
    )
    post_data = await create_post_service(post, current_user , db)
    return post_data


#generate_blog based on user input
@router.post("/agent")
async def getInput(input:AgentInput, response_model= AIResponse, db: AsyncSession = Depends(get_db),current_user=Depends(token_validation)):
    app = build_graph()
    output= app.invoke({"topic": input ,"prompt": "{}"})
    post = PostModel(
        title=output.get("title"),
        content=output.get("content"),
        img_url=output.get("img_url")
    )
    return post