import time
import uuid
import structlog
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from structlog.contextvars import bound_contextvars
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Import your local modules
from .routes import user_routes, posts_routes, comments_routes
from .databaseSetup import Base, engine
from .logger.logger import log
from .limiter import limiter
from .agent import agent_routes
from app.agent.cron.generate_blog import generate_content

# --- 1. SCHEDULER INITIALIZATION ---
# Initialize here so it's accessible globally, but start it in lifespan
scheduler = AsyncIOScheduler()

# --- 2. LIFESPAN MANAGEMENT ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP LOGIC ---
    log.info("Application startup initiated")
    
    # A. Database Setup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # B. Scheduler Setup
    # Moving scheduler here ensures it only starts if the DB is ready
    log.info("Starting scheduler")
    try:
        # Check if job already exists to avoid duplicates on reload
        if not scheduler.get_job("blog_gen_job"):
            scheduler.add_job(generate_content,"interval",hours=1,id="blog_gen_job")
        scheduler.start()
    except Exception as e:
        log.error("Failed to start scheduler", error=str(e))

    yield  # --- APP IS RUNNING ---

    # --- SHUTDOWN LOGIC ---
    log.info("Application shutdown initiated")
    scheduler.shutdown()
    await engine.dispose()

# --- 3. APP CONFIGURATION ---
app = FastAPI(lifespan=lifespan)

# Rate Limiter
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. REQUEST TRACING MIDDLEWARE ---
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
  
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

# --- 5. ROUTER INCLUSION ---
# Included outside lifespan but inside the script flow
try:
    app.include_router(user_routes.router, prefix="", tags=["login"])
    app.include_router(posts_routes.router, prefix="", tags=["post"])
    app.include_router(comments_routes.router, prefix="", tags=["comment"])
    app.include_router(agent_routes.router, prefix="", tags=["agent"])
except Exception as e:
    log.error("Router inclusion error", error=str(e))
