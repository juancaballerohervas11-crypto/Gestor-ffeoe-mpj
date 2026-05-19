from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from .. import models, schemas, auth_tokens, utils, services
from ..database import get_db
from ..auth_tokens import *
import csv
import io
import os
import shutil

router = APIRouter(
    prefix="/alumnos",
    tags=["Alumnos"]
)

permiso_admin_prof = RoleChecker(["admin", "profesor"])
permiso_admin = RoleChecker(["admin"])


#   LISTAR

@router.get("/", response_model=List[schemas.AlumnoOut])
def listar_alumnos(
    db: Session = Depends(get_db),
):
    return db.query(models.Alumno).all()





#   CREAR

@router.post("/", response_model=schemas.AlumnoOut, status_code=201)
def crear_alumno(
    alumno: schemas.AlumnoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin_prof)
):
    return services.crear_alumno(db, alumno, current_user)





#   IMPORTACION POR CSV

@router.post("/importar-csv", status_code=201)
async def importar_alumnos(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin_prof)
):
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))

    creados = 0
    saltados = 0

    for row in reader:
        email = row.get('email')
        if not email or not row.get('nombre'):
            saltados += 1
            continue

        existe = db.query(models.Alumno).filter(models.Alumno.email == email).first()
        if existe:
            saltados += 1
            continue

        nuevo = models.Alumno(
            nombre=row.get('nombre'),
            apellido=row.get('apellido'),
            email=email,
            registrado_por=current_user.id
        )
        db.add(nuevo)
        creados += 1

    db.commit()
    return {"nuevos_alumnos": creados, "saltados": saltados}



#   ACTUALIZAR

@router.put("/{alumno_id}", response_model=schemas.AlumnoOut)
def actualizar_alumno(
    alumno_id: int,
    datos: schemas.AlumnoUpdate,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    try:
        return services.editar_alumno(db, alumno_id, datos)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El email ya está en uso por otro alumno")



#   ELIMINAR

@router.delete("/{alumno_id}", status_code=204)
def eliminar_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    services.eliminar_alumno(db, alumno_id)


#   PERFIL ALUMNO (LOGUEADO)

@router.get("/perfil/me", response_model=schemas.AlumnoOut)
def obtener_mi_perfil(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user)
):
    """
    Obtiene el perfil del alumno logueado (vinculado por email).
    """
    alumno = db.query(models.Alumno).filter(models.Alumno.email == current_user.email).first()
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró un perfil de alumno asociado a este usuario"
        )
    return alumno


@router.put("/perfil/me", response_model=schemas.AlumnoOut)
def actualizar_mi_perfil(
    datos: schemas.AlumnoPerfilUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user)
):
    """
    Permite al alumno logueado actualizar sus datos de contacto (email y telefono).
    """
    alumno = db.query(models.Alumno).filter(models.Alumno.email == current_user.email).first()
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró un perfil de alumno asociado a este usuario"
        )

    # Validar si el nuevo email ya está en uso por otro alumno
    if datos.email and datos.email != alumno.email:
        existe = db.query(models.Alumno).filter(models.Alumno.email == datos.email).first()
        if existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado por otro alumno"
            )
        alumno.email = datos.email
        # También actualizamos el email del usuario logueado para consistencia de credenciales
        user = db.query(models.User).filter(models.User.email == current_user.email).first()
        if user:
            user.email = datos.email

    if datos.telefono is not None:
        alumno.telefono = datos.telefono

    db.commit()
    db.refresh(alumno)
    return alumno


@router.post("/perfil/me/cv", status_code=status.HTTP_200_OK)
async def subir_mi_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user)
):
    """
    Permite al alumno logueado subir su currículum en formato PDF.
    """
    alumno = db.query(models.Alumno).filter(models.Alumno.email == current_user.email).first()
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró un perfil de alumno asociado a este usuario"
        )

    # Validar formato de archivo
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser un documento PDF"
        )

    
    # Crear directorio si no existe
    upload_dir = os.path.join("uploads", "cvs")
    os.makedirs(upload_dir, exist_ok=True)

    # Guardar archivo con nombre único
    file_name = f"cv_alumno_{alumno.id}.pdf"
    file_path = os.path.join(upload_dir, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Actualizar ruta en la base de datos
    alumno.cv_path = file_path
    db.commit()

    return {"mensaje": "Currículum subido correctamente", "cv_path": file_path}


#   ACCESOS DE GESTORES (ADMIN/PROFESOR) A DETALLES DE ALUMNO

@router.get("/{alumno_id}", response_model=schemas.AlumnoOut)
def obtener_detalle_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin_prof)
):
    """
    Obtiene los detalles de un alumno específico por ID.
    Solo accesible para Administradores, Coordinadores y Profesores.
    """
    from .. import utils
    alumno = utils.alumno_existe(db, alumno_id)
    return alumno


@router.get("/{alumno_id}/descargar-cv")
def descargar_cv_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user)
):
    """
    Permite descargar o ver el CV en PDF de un alumno.
    Accesible para el propio alumno, y para Administradores, Coordinadores o Profesores.
    """
    from .. import utils
    import os
    alumno = utils.alumno_existe(db, alumno_id)

    # Verificar permisos: El propio alumno o administradores/profesores
    if current_user.email != alumno.email and current_user.role not in ["admin", "coordinador", "profesor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver el currículum de este alumno"
        )

    if not alumno.cv_path or not os.path.exists(alumno.cv_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Este alumno no ha subido su currículum aún"
        )

    from fastapi.responses import FileResponse
    return FileResponse(
        path=alumno.cv_path,
        media_type="application/pdf",
        filename=f"CV_{alumno.nombre}_{alumno.apellido}.pdf"
    )