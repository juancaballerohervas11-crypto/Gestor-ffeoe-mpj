from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:2b295fed2ac875775c825fbe2ba996842d09ebc3381cf148b81a68a7a0236373@localhost:3307/gestor_ffeoe"

# forzamos el plugin de password normal
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        
        # Esto asegura una conexión limpia
        "client_flag":0,


        # nombres de los argumentos para la conexión
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