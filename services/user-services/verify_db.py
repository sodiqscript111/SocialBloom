from sqlalchemy import create_engine, inspect
from db.database import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
inspector = inspect(engine)
tables = inspector.get_table_names()
print("Tables found:", tables)
