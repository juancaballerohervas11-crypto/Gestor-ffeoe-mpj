from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models
from .routers import usuarios, alumnos, empresas, contactos, profesores
from fastapi import Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from . import models, auth_tokens
from .database import get_db
from fastapi.openapi.docs import get_swagger_ui_html


#   CREACIÓN DE TABLAS
# lee los modelos de models.py y crea las tablas en MySQL si no existen
models.Base.metadata.create_all(bind=engine)




#   INICIALIZACIÓN DE LA APP

app = FastAPI(
    title="Sistema de Gestión FFOE",
    description="API profesional para la gestión de prácticas, alumnos y empresas.",
    version="1.0.0"
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #poner la URL del frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],
)



#   INCLUSIÓN DE ROUTERS

app.include_router(usuarios.router)
app.include_router(alumnos.router)
app.include_router(empresas.router)
app.include_router(contactos.router)
app.include_router(profesores.router)

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

    # 3 Listado completo de empresas (Ordenadas por cantidad de plazas)
    
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
            "plazas_disponibles_totales": plazas_libres_totales,
            "listado_ofertas": [
                {"nombre": e.nombre, "plazas": e.plazas_totales, "contacto": e.contacto} 
                for e in ofertas_empresas
            ]
        }
    }