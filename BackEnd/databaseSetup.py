from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

engine=create_engine("sqlite:///blog.db",echo=True)

Base =declarative_base()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import model

Base.metadata.create_all(bind=engine)