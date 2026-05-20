from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import usuarios, alumnos, empresas, contactos, profesores, ciclos
from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models, auth_tokens
from .database import get_db
from fastapi.openapi.docs import get_swagger_ui_html
import socket


#   CREACIÓN DE TABLAS
# lee los modelos de models.py y crea las tablas en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

#   MIGRACIÓN AUTOMÁTICA DE COLUMNAS (Para bases de datos existentes)
from sqlalchemy import inspect, text
def auto_migrate():
    from .database import SessionLocal
    db = SessionLocal()
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('alumnos')]
        
        # Check and add tutor_docente_id
        if 'tutor_docente_id' not in columns:
            try:
                db.execute(text("ALTER TABLE alumnos ADD COLUMN tutor_docente_id INT NULL"))
                db.execute(text("ALTER TABLE alumnos ADD CONSTRAINT fk_alumnos_tutor_docente FOREIGN KEY (tutor_docente_id) REFERENCES users(id)"))
                print("Auto-migration: Added tutor_docente_id and foreign key to alumnos table")
            except Exception as e:
                try:
                    db.execute(text("ALTER TABLE alumnos ADD COLUMN tutor_docente_id INT NULL"))
                    print("Auto-migration: Added tutor_docente_id column (sqlite/fallback)")
                except Exception as ex:
                    print(f"Auto-migration info: tutor_docente_id column skipped/exists: {ex}")
        
        # Check and add tutor_docente_nombre
        if 'tutor_docente_nombre' not in columns:
            try:
                db.execute(text("ALTER TABLE alumnos ADD COLUMN tutor_docente_nombre VARCHAR(255) NULL"))
                print("Auto-migration: Added tutor_docente_nombre to alumnos table")
            except Exception as e:
                print(f"Auto-migration info: tutor_docente_nombre skipped: {e}")
            
        # Check and add tutor_laboral_nombre
        if 'tutor_laboral_nombre' not in columns:
            try:
                db.execute(text("ALTER TABLE alumnos ADD COLUMN tutor_laboral_nombre VARCHAR(255) NULL"))
                print("Auto-migration: Added tutor_laboral_nombre to alumnos table")
            except Exception as e:
                print(f"Auto-migration info: tutor_laboral_nombre skipped: {e}")
            
        # Check and add tutor_laboral_dni
        if 'tutor_laboral_dni' not in columns:
            try:
                db.execute(text("ALTER TABLE alumnos ADD COLUMN tutor_laboral_dni VARCHAR(50) NULL"))
                print("Auto-migration: Added tutor_laboral_dni to alumnos table")
            except Exception as e:
                print(f"Auto-migration info: tutor_laboral_dni skipped: {e}")
                
        # Check and add tutor_laboral_contacto
        if 'tutor_laboral_contacto' not in columns:
            try:
                db.execute(text("ALTER TABLE alumnos ADD COLUMN tutor_laboral_contacto VARCHAR(255) NULL"))
                print("Auto-migration: Added tutor_laboral_contacto to alumnos table")
            except Exception as e:
                print(f"Auto-migration info: tutor_laboral_contacto skipped: {e}")
            
        # Check and add profile_pic to users table
        user_columns = [col['name'] for col in inspector.get_columns('users')]
        if 'profile_pic' not in user_columns:
            try:
                db.execute(text("ALTER TABLE users ADD COLUMN profile_pic LONGTEXT NULL"))
                print("Auto-migration: Added profile_pic to users table (MySQL)")
            except Exception as e:
                try:
                    db.execute(text("ALTER TABLE users ADD COLUMN profile_pic TEXT NULL"))
                    print("Auto-migration: Added profile_pic to users table (SQLite/fallback)")
                except Exception as ex:
                    print(f"Auto-migration info: profile_pic skipped/exists: {ex}")

        db.commit()
    except Exception as e:
        print(f"Auto-migration warning: {e}")
    finally:
        db.close()

auto_migrate()






#   INICIALIZACIÓN DE LA APP

app = FastAPI(
    title="Sistema de Gestión FFOE",
    description="API de Gestión de prácticas para alumnado de Formación Profesional.",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True} 
    )



# Esto es para casos donde el constructor de FastAPI falla

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_ui_parameters={"persistAuthorization": True}
    )

#   CONFIGURACIÓN DE CORS

import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No requiere conexión real a internet
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

local_ip = get_local_ip()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://{local_ip}:5173",
        f"http://{local_ip}:5500",
        f"http://{local_ip}:5501",
        f"http://{local_ip}",
        "http://localhost:5173",      
        "http://localhost:5500",
        "http://localhost:5501",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:5501",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)




#   INCLUSIÓN DE ROUTERS

app.include_router(usuarios.router, prefix="/api/v1")
app.include_router(alumnos.router, prefix="/api/v1")
app.include_router(empresas.router, prefix="/api/v1")
app.include_router(contactos.router, prefix="/api/v1")
app.include_router(profesores.router, prefix="/api/v1")
app.include_router(ciclos.router, prefix="/api/v1")

@app.get("/", tags=["General"])
def read_root():
    return {
        "mensaje": "Bienvenido a la API de Gestión de FFEOE",
        "estado": "Online",
        "documentacion": "/docs"
    }




@app.get("/stats/resumen", tags=["Estadísticas"])
def obtener_resumen_gestion(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user)
):
    # 1 Alumnos totales y alumnos asignados
    total_alumnos = db.query(models.Alumno).count()
    alumnos_con_empresa = db.query(models.Alumno).filter(models.Alumno.empresa_asignada_id != None).count()
    alumnos_sin_empresa = total_alumnos - alumnos_con_empresa

    # 2 Total de plazas disponibles en el sistema
    plazas_libres_totales = db.query(func.sum(models.Empresa.plazas_totales)).scalar() or 0

    # 3 Profesores, Empresas, y Ciclos totales en el sistema
    total_profesores = db.query(models.User).filter(models.User.role.in_(["admin", "profesor", "coordinador"])).count()
    total_empresas = db.query(models.Empresa).count()
    total_ciclos = db.query(models.Ciclo).count()

    # 4 Listado completo de empresas (Ordenadas por cantidad de plazas)
    ofertas_empresas = db.query(models.Empresa)\
        .filter(models.Empresa.plazas_totales > 0)\
        .order_by(models.Empresa.plazas_totales.desc())\
        .all()

    return {
        "alumnos": {
            "total": total_alumnos,
            "asignados": alumnos_con_empresa,
            "pendientes": alumnos_sin_empresa
        },
        "empresas": {
            "total": total_empresas,
            "plazas_disponibles_totales": plazas_libres_totales,
            "listado_ofertas": [
                {"nombre": e.nombre, "plazas": e.plazas_totales, "contacto": e.contacto} 
                for e in ofertas_empresas
            ]
        },
        "profesores": {
            "total": total_profesores
        },
        "ciclos": {
            "total": total_ciclos
        }
    }