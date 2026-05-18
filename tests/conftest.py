import os
os.environ["DATABASE_URL"] = "sqlite:///./test_final.db"
os.environ["SECRET_KEY"] = "clave_secreta_para_tests"
os.environ["TESTING"] = "true"

from backend.app.main import app
from backend.app.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_final.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db