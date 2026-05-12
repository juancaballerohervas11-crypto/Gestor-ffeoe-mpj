from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from .. import models, schemas, auth_tokens, utils, services, database
from ..auth_tokens import *

router = APIRouter(
    prefix="/profesores",
    tags=["Profesores"]
)

get_db = database.get_db

permiso_admin_prof = RoleChecker(["admin", "profesor"])
permiso_admin = RoleChecker(["admin"])





#   CREAR

@router.post("/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def crear_profesor(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin)
):
    return services.crear_profesor(db, user)




#   LISTAR

@router.get("/", response_model=List[schemas.UserOut])
def listar_profesores_y_administradores(
    db: Session = Depends(get_db),
):
    return db.query(models.User).filter(models.User.role.in_(["profesor", "admin"])).all()






#   EDITAR

@router.put("/{profe_id}", response_model=schemas.UserOut)
def actualizar_profesor(
    profe_id: int,
    datos: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    try:
        return services.editar_profesor(db, profe_id, datos)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El nuevo email ya está en uso")






#   ELIMINAR

@router.delete("/{profe_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_profesor(
    profe_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin_prof)
):
    services.eliminar_profesor(db, profe_id, current_user)