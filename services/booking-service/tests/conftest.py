import os
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.rabbitmq import RabbitMqContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["RABBITMQ_URL"] = "amqp://guest:guest@localhost:5672/"
os.environ["NOTIFICATION_SERVICE_HOST"] = "localhost:50051"
os.environ["JWT_SECRET_KEY"] = "testsecret"

from app.db.database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from events.config import setup_rabbitmq

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:15") as postgres:
        url = postgres.get_connection_url().replace("postgresql+psycopg2", "postgresql+psycopg")
        os.environ["DATABASE_URL"] = url
        yield postgres

@pytest.fixture(scope="session")
def rabbitmq_container():
    with RabbitMqContainer("rabbitmq:3-management") as rabbitmq:
        host = rabbitmq.get_container_host_ip()
        port = rabbitmq.get_exposed_port(5672)
        url = f"amqp://guest:guest@{host}:{port}/"
        os.environ["RABBITMQ_URL"] = url
        setup_rabbitmq()
        yield rabbitmq
        
@pytest.fixture(scope="session")
def db_engine(postgres_container):
    url = os.environ["DATABASE_URL"]
    engine = create_engine(url)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(db_session, rabbitmq_container):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
