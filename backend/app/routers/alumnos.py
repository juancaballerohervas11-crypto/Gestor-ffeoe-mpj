import csv
import io
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, auth_tokens, utils
from ..database import get_db
from sqlalchemy.exc import IntegrityError
from ..auth_tokens import *
from ..utils import *


router = APIRouter(
    prefix="/alumnos",
    tags=["Alumnos"]
)

permiso_admin_prof = RoleChecker(["admin", "profesor"])
permiso_admin = RoleChecker(["admin"])




#   LISTADO DE LOS ALUMNOS

@router.get("/", response_model=List[schemas.AlumnoOut])
def listar_alumnos(
    db: Session = Depends(get_db),
):
    return db.query(models.Alumno).all()



#   CREACIÓN MANUAL DE ALUMNO 

@router.post("/", response_model=schemas.AlumnoOut, status_code=201)
def crear_alumno(
    alumno: schemas.AlumnoCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin_prof)
):
    
    # Verificar si el email ya existe
    existe = db.query(models.Alumno).filter(models.Alumno.email == alumno.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    nuevo_alumno = models.Alumno(**alumno.model_dump(), registrado_por=current_user.id)

    db.add(nuevo_alumno)
    db.commit()
    db.refresh(nuevo_alumno)
    return nuevo_alumno






#   IMPORTAR ALUMNOS DESDE .csv

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
            curso=row.get('curso'),
            registrado_por=current_user.id
        )
        db.add(nuevo)
        creados += 1
    
    db.commit()
    return {"nuevos_alumnos": creados, "saltados": saltados}




#   EDITAR ALUMNO

@router.put("/{alumno_id}", response_model=schemas.AlumnoOut)
def actualizar_alumno(
    alumno_id: int, 
    datos: schemas.AlumnoUpdate, 
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
  
    alumno_existente = alumno_existe(db, alumno_id)

  
    try:
        update_data = datos.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(alumno_existente, key, value)

        db.commit()
        db.refresh(alumno_existente)
        return alumno_existente
        
    except IntegrityError:
        db.rollback() 
        raise HTTPException(
            status_code=400, 
            detail="El email ya está en uso por otro alumno"
        )




#   ELIMINAR ALUMNO

@router.delete("/{alumno_id}", status_code=204)
def eliminar_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    
    alumno = utils.alumno_existe(db, alumno_id)

    if alumno.empresa_asignada_id:
        utils.devolver_plaza_empresa(db, alumno.empresa_asignada_id)

    db.delete(alumno)
    db.commit()
    return None