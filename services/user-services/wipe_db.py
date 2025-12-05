from sqlalchemy import create_engine, MetaData
from db.database import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)
metadata.drop_all(bind=engine)
print("All tables dropped.")
