from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from .. import models, schemas, auth_tokens, utils, services
from ..database import get_db
from ..auth_tokens import *

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

permiso_admin_prof = RoleChecker(["admin", "profesor"])
permiso_admin = RoleChecker(["admin"])




#   LOGIN

@router.post("/login", response_model=schemas.Token)
def login_para_obtener_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth_tokens.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_tokens.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}




#   REGISTRO

@router.post("/registrar", response_model=schemas.UserOut, status_code=201)
def registrar_usuario(
    usuario: schemas.UserCreate,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin)
):
    return services.registrar_usuario(db, usuario)



#   VER DATOS DE USUARIO

@router.get("/me", response_model=schemas.UserOut)
def leer_mis_datos(current_user: models.User = Depends(auth_tokens.get_current_user)):
    return current_user





#   LISTADO DE USUARIOS

@router.get("/", response_model=List[schemas.UserOut])
def listar_usuarios(
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin)
):
    return db.query(models.User).all()





#   CAMBIO DE ROL DE UN USUARIO

@router.put("/{user_id}/role", response_model=schemas.UserOut)
def cambiar_rol_usuario(
    user_id: int,
    nuevo_rol: str,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin)
):
    usuario = utils.profesor_existe(db, user_id)
    roles_permitidos = ["admin", "profesor", "user"]
    if nuevo_rol not in roles_permitidos:
        raise HTTPException(
            status_code=400,
            detail=f"Rol no válido. Los roles permitidos son: {', '.join(roles_permitidos)}"
        )
    usuario.role = nuevo_rol
    db.commit()
    db.refresh(usuario)
    return usuario



#   ELIMINAR

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin)
):
    services.eliminar_usuario(db, user_id, current_user)