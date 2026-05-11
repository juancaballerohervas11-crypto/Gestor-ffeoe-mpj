from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from .. import models, schemas, auth_tokens, utils, database
from ..utils import *
from ..auth_tokens import *

router = APIRouter(
    prefix="/profesores",
    tags=["Profesores"]
)

get_db = database.get_db


permiso_admin_prof = RoleChecker(["admin", "profesor"])
permiso_admin = RoleChecker(["admin"])







#   CREAR PROFESOR

@router.post("/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def crear_profesor(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin)
):
    
    
    # Verifica si el email ya existe en los usuarios
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Encripta la contraseña
    hashed_password = utils.get_password_hash(user.password)
    nuevo_profe = models.User(
        email=user.email,
        full_name=user.full_name,
        password=hashed_password,
        role="profesor" 
    )
    
    db.add(nuevo_profe)
    db.commit()
    db.refresh(nuevo_profe)
    return nuevo_profe





#   LISTAR PROFESORES / ADMINS

@router.get("/", response_model=List[schemas.UserOut])
def listar_profesores_y_administradores(
    db: Session = Depends(get_db),
):
    # Filtramos para obtener solo usuarios con rol docente o administrativo
    profesores = db.query(models.User).filter(models.User.role.in_(["profesor", "admin"])).all()
    return profesores



#   MODIFICAR PROFESOR

@router.put("/{profe_id}", response_model=schemas.UserOut)
def actualizar_profesor(
    profe_id: int,
    datos: schemas.UserUpdate, 
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    # Valida existencia
    profe = utils.profesor_existe(db, profe_id)

    try:
        update_data = datos.model_dump(exclude_unset=True)
        
        # Hashea de contraseña
        if "password" in update_data and update_data["password"]:
            update_data["password"] = utils.get_password_hash(update_data["password"])
            
        # Actualiza de atributos
        for key, value in update_data.items():
            setattr(profe, key, value)

        db.commit()
        db.refresh(profe)
        return profe
  
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El nuevo email ya está en uso")



#   ELIMINAR PROFESOR 

@router.delete("/{profe_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_profesor(
    profe_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin_prof) 
):
    # Valida existencia
    profe = utils.profesor_existe(db, profe_id)
    
    # Evita que el profesor se borre a si mismo
    if profe.id == current_user.id:
        raise HTTPException(
            status_code=400, 
            detail="No puedes eliminar tu propio usuairio administrador/profesor"
        )

    # Borra al profesor
    db.delete(profe)
    db.commit()
    return None