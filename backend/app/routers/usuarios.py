from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import models, schemas, auth_tokens, utils
from ..database import get_db
from typing import List
from ..auth_tokens import *


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)



permiso_admin_prof = RoleChecker(["admin", "profesor"])
permiso_admin = RoleChecker(["admin"])






#   LOGIN (Con su Token)

@router.post("/login", response_model=schemas.Token)
def login_para_obtener_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # Buscamos al usuario por su username (email)
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not utils.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Creamos el token
    access_token_expires = timedelta(minutes=auth_tokens.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_tokens.create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}





#   REGISTRO DE NUEVOS USUARIOS

@router.post("/registrar", response_model=schemas.UserOut, status_code=201)
def registrar_usuario(
    usuario: schemas.UserCreate, 
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin) 
):
    # Comprueba si ya existe el mail
    if utils.obtener_usuario_por_email(db, usuario.email):
        raise HTTPException(
            status_code=400, 
            detail="El email ya está registrado"
        )

    # Crear nuevo usuario con contraseña hasheada
    nuevo_usuario = models.User(
        email=usuario.email,
        full_name=usuario.full_name,
        password=utils.get_password_hash(usuario.password),
        role=usuario.role
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario


#   VER MI PERFIL DE USUARIO

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



#   CAMBIAR ROL O EDITAR USUARIO

@router.put("/{user_id}/role", response_model=schemas.UserOut)
def cambiar_rol_usuario(
    user_id: int,
    nuevo_rol: str, # "admin" o "profesor"
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin)
):
    # Valida existencia
    usuario = utils.profesor_existe(db, user_id)

    # Valida roles permitidos para el cambio
    roles_permitidos = ["admin", "profesor", "user"]
    if nuevo_rol not in roles_permitidos:
        raise HTTPException(
            status_code=400, 
            detail=f"Rol no válido. Los roles permitidos son: {', '.join(roles_permitidos)}"
        )

    # 3. Actualización directa del objeto
    usuario.role = nuevo_rol
    
    db.commit()
    db.refresh(usuario)
    
    return usuario





#   ELIMINAR USUARIO

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin)
):
    # Valida existencia
    usuario = utils.profesor_existe(db, user_id)

    # Evita que el admin se borre a sí mismo
    if usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No puedes eliminar tu propio usuario administrador"
        )

    # Borra el usuario
    db.delete(usuario)
    db.commit()
    
    return None