import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_final.db")
os.environ.setdefault("SECRET_KEY", "clave_secreta_para_tests")
os.environ.setdefault("TESTING", "true")

# Parchear el engine de la app ANTES de importar main para evitar
# que create_all falle con LONGTEXT en SQLite.
import backend.app.database as _db_module
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_SQLITE_URL = "sqlite:///./test_final.db"
_test_engine = create_engine(_SQLITE_URL, connect_args={"check_same_thread": False})
_db_module.engine = _test_engine
_db_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

from backend.app.main import app       # noqa: E402  (importación diferida intencionada)
from backend.app.database import get_db, Base

try:
    Base.metadata.create_all(bind=_test_engine)
except Exception as e:
    print(f"[conftest] create_all skipped: {e}")

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db