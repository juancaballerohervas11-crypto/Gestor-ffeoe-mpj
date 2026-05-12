from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from pathlib import Path



load_dotenv(dotenv_path=Path(__file__).parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")


# Fuerza el plugin de password normal
engine = create_engine(
    DATABASE_URL,
    connect_args={
        
        # Esto asegura una conexión limpia
        "client_flag":0,


        # Nombres de los argumentos para la conexión
        "auth_plugin_map": "mysql_native_password"
    }
)

# Creamos el sessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()