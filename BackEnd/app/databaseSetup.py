from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

engine=create_engine("sqlite:///blog.db",echo=True)

Base =declarative_base()
try:
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
except SQLAlchemyError as e:
    raise RuntimeError(f"Database connection failed ",{str(e)})

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



