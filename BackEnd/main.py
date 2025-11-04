from fastapi import FastAPI
import databaseSetup

app = FastAPI()

from routes import user_routes