from fastapi import FastAPI
from .routes import user_routes,posts_routes,comments_routes
from .databaseSetup import Base, engine


Base.metadata.create_all(bind=engine) 
app = FastAPI()

app.include_router(user_routes.router, prefix="", tags=["login"])
app.include_router(posts_routes.router, prefix="", tags=["post"])
app.include_router(comments_routes.router, prefix="", tags=["comment"])
