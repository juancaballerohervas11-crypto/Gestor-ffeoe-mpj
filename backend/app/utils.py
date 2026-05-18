from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from . import models

#   ESTE ARCHIVO CONTIENE VALIDACIONES PARA EL CRUD Y EL HASHING DE CONTRASEÑAS



#              VALIDACIONES

def empresa_existe(db: Session, empresa_id: int):
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La empresa con ID {empresa_id} no existe"
        )
    return empresa


def alumno_existe(db: Session, alumno_id: int):
    alumno = db.query(models.Alumno).filter(models.Alumno.id == alumno_id).first()
    if not alumno:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El alumno con ID {alumno_id} no existe"
        )
    return alumno


def contacto_existe(db: Session, contacto_id: int):
    contacto = db.query(models.ContactoEmpresa).filter(models.ContactoEmpresa.id == contacto_id).first()
    if not contacto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El contacto con ID {contacto_id} no existe"
        )
    return contacto

def profesor_existe(db: Session, profesor_id: int):
    user = db.query(models.User).filter(models.User.id == profesor_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se ha encontrado ningún profesor con el ID {profesor_id}"
        )
    return user


def ciclo_existe(db: Session, ciclo_id: int):
    ciclo = db.query(models.Ciclo).filter(models.Ciclo.id == ciclo_id).first()
    if not ciclo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El ciclo con ID {ciclo_id} no existe"
        )
    return ciclo





#         HASHING DE CONTRASEÑAS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    # Hacemos el Hash de la contraseña para dejarla segura
def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)





#  DEVOLVER PLAZA A EMPRESA

def devolver_plaza_empresa(db: Session, empresa_id: int):
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if empresa:
        empresa.plazas_totales += 1
        db.add(empresa) 



#   BUSCAR EMPRESA USANDO EL CIF

def obtener_empresa_por_cif(db: Session, cif: str):
    return db.query(models.Empresa).filter(models.Empresa.cif == cif).first()


#   BUSCAR USUARIO CON EL EMAIL (USERNAME)

def obtener_usuario_por_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()
