from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from . import database, models, schemas
from fastapi import FastAPI
    
app = FastAPI(
    title="Gestor FFEOE",
    # Esto mantiene la autorización aún recargando la pagina del Swagger
    swagger_ui_parameters={"persistAuthorization": True} 
)

# Configuración básica 

SECRET_KEY = "3a5878ad1068da64a065f1f68b00a17aa2c4ad33a84effe1c5ad499ef2c7dda5"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")





#   CREACIÓN Y VALIDACIÓN DEL TOKEN

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
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