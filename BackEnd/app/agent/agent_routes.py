from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from .graph import build_graph, build_news_graph
from ..schemas import AIResponse, PostModel
from ..routes.posts_routes import create_post_service
from ..databaseSetup import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..auth.jwt_handler import token_validation
from .llm import analyse_image_llm, analyse_image_llm_async
import asyncio
from functools import partial

router = APIRouter()

class AgentInput(BaseModel):
    input: str

class ImageInput(BaseModel):
    image_base64: str
    media_type: str

class NewsInput(BaseModel):
    title: str
    url: str
    summary: str
    source: str = "hackernews"


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


@router.post("/agent")
async def getInput(
    input: AgentInput,
    response_model=AIResponse,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(token_validation)
):
    loop = asyncio.get_event_loop()
    graph = build_graph()
    output = await loop.run_in_executor(
        None,
        partial(graph.invoke, {"topic": input, "prompt": "{}"})
    )
    post = PostModel(
        title=output.get("title"),
        content=output.get("content"),
        img_url=output.get("img_url")
    )
    return post

@router.post("/analyse-image")
async def analyse_image(
    input: ImageInput,
    current_user=Depends(token_validation)
):
    try:
        description = await analyse_image_llm_async( 
            input.image_base64,
            input.media_type
        )
        return {"description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@router.post("/generate-from-news")
async def generate_from_news(
    input: NewsInput,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(token_validation)
):
    loop = asyncio.get_event_loop()
    graph = build_news_graph()
    output = await loop.run_in_executor(
        None,
        partial(graph.invoke, {
            "topic": input.title,
            "prompt": "{}",
            "news_items": [{
                "title": input.title,
                "url": input.url,
                "summary": input.summary
            }],
            "news_source": input.source
        })
    )
    post = PostModel(
        title=output.get("title"),
        content=output.get("content"),
        img_url=output.get("img_url")
    )
    return post


@router.get("/tech-news-stories")
async def get_tech_news_stories(
    source: str = "hackernews",
    current_user=Depends(token_validation)
):
    loop = asyncio.get_event_loop()
    try:
        from mcp_server.tools.fetch_news import fetch_news
        result = await loop.run_in_executor(
            None,
            partial(fetch_news, source, 5)
        )
        return {"stories": result.get("articles", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





        