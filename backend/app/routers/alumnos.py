from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from .. import models, schemas, auth_tokens, utils, services
from ..database import get_db
from ..auth_tokens import *
import csv
import io

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