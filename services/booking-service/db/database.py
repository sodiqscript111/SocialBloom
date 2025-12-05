from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Using bookingsdb as specified
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:password@localhost/bookingsdb"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
