from fastapi import FastAPI,HTTPException,Request
import time
import uuid
import structlog
from .routes import user_routes,posts_routes,comments_routes
from .databaseSetup import Base, engine
from .logger.logger import log
from structlog.contextvars import bound_contextvars
from sqlalchemy.ext.asyncio import AsyncEngine
import asyncio
from contextlib import asynccontextmanager
from .limiter import limiter
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware




@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
app = FastAPI(lifespan=lifespan)

#Set  limiter
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

#CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


log.info("Application starts")
try:
    app.include_router(user_routes.router, prefix="", tags=["login"])
    app.include_router(posts_routes.router, prefix="", tags=["post"])
    app.include_router(comments_routes.router, prefix="", tags=["comment"])
except Exception as e:
    log.error("Application start Error")
    raise HTTPException(status_code=500, detail=f"Internal Server Error")



#Request Tracing
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
  
    # Add request_id to the structlog context
    with bound_contextvars(request_id=request_id):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
  
        log.info(
            "Request completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=round(process_time, 4),
        )
        response.headers["X-Request-ID"] = request_id
        return response