from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta,timezone
from typing import Optional
from . import database, models, schemas
from dotenv import load_dotenv
import os
from pathlib import Path




load_dotenv(dotenv_path=Path(__file__).parent / ".env")

    

# Configuración básica 

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120   # 2 horas

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")





#   CREACIÓN Y VALIDACIÓN DEL TOKEN

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub") 
        if email is None:
            raise credentials_exception
        
        token_data = schemas.TokenData(id=email) # Usamos el email como identificador
    except JWTError:
        raise credentials_exception
    return token_data





#   VERIFICACIÓN DEL TOKEN DEL USUARIO

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Valida el token y devuelve el usuario de la base de datos.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el usuario",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1 Verifica que el token sea válido y obtenemos el ID
    token_data = verify_access_token(token, credentials_exception)

    # 2 Busca al usuario en la Base de Datos
    user = db.query(models.User).filter(models.User.email == token_data.id).first()
    if user is None:
        raise credentials_exception

    return user





#   VALIDACION DE PERMISOS DE USUARIO

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: models.User = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes los permisos necesarios para realizar esta acción"
            )
        return current_user