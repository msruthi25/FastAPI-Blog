from fastapi import FastAPI,HTTPException
from .routes import user_routes,posts_routes,comments_routes
from .databaseSetup import Base, engine


Base.metadata.create_all(bind=engine) 
app = FastAPI()
try:
    app.include_router(user_routes.router, prefix="", tags=["login"])
    app.include_router(posts_routes.router, prefix="", tags=["post"])
    app.include_router(comments_routes.router, prefix="", tags=["comment"])
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Internal Server Error")