import sys
import os
sys.path.append(os.getcwd())

from app.models.user import Base
print("Tables in metadata:", Base.metadata.tables.keys())
