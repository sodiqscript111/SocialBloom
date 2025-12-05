from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Hardcoded PostgreSQL URL - CHANGE THIS to your actual credentials!
# Format: postgresql://<username>:<password>@<host>:<port>/<database_name>
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://postgres:password@localhost/testing"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()