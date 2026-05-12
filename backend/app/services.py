from sqlalchemy.orm import Session
from . import models, schemas, utils
from fastapi import HTTPException


#   CONTACTOS

def crear_contacto(db: Session, contacto: schemas.ContactoCreate, user: models.User):
    empresa = utils.empresa_existe(db, contacto.empresa_id)
    nuevo_contacto = models.ContactoEmpresa(
        **contacto.model_dump(),
        profesor_id=user.id,
        nombre_profesor=user.full_name
    )
    if contacto.estado == "Acepta":
        empresa.plazas_totales += contacto.plazas_ofrecidas
    db.add(nuevo_contacto)
    db.commit()
    db.refresh(nuevo_contacto)
    return nuevo_contacto


def editar_contacto(db: Session, contacto_id: int, contacto_actualizado: schemas.ContactoBase):
    contacto_db = utils.contacto_existe(db, contacto_id)
    empresa = utils.empresa_existe(db, contacto_db.empresa_id)

    estado_anterior = contacto_db.estado
    estado_nuevo = contacto_actualizado.estado

    if estado_anterior == "Acepta" and estado_nuevo != "Acepta":
        empresa.plazas_totales -= contacto_db.plazas_ofrecidas
    elif estado_anterior != "Acepta" and estado_nuevo == "Acepta":
        empresa.plazas_totales += contacto_actualizado.plazas_ofrecidas

    contacto_data = contacto_actualizado.model_dump(exclude_unset=True)
    for key, value in contacto_data.items():
        setattr(contacto_db, key, value)

    db.commit()
    db.refresh(contacto_db)
    return contacto_db


def eliminar_contacto(db: Session, contacto_id: int):
    contacto = utils.contacto_existe(db, contacto_id)
    db.delete(contacto)
    db.commit()





    #   EMPRESAS

def crear_empresa(db: Session, empresa: schemas.EmpresaCreate, user: models.User):
    existe = db.query(models.Empresa).filter(models.Empresa.cif == empresa.cif).first()
    if existe:
        raise HTTPException(status_code=400, detail="El CIF ya está registrado")
    nueva_empresa = models.Empresa(**empresa.model_dump(), registrado_por=user.id)
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)
    return nueva_empresa


def editar_empresa(db: Session, empresa_id: int, datos: schemas.EmpresaUpdate):
    empresa_db = utils.empresa_existe(db, empresa_id)
    datos_dict = datos.model_dump(exclude_unset=True)
    for key, value in datos_dict.items():
        setattr(empresa_db, key, value)
    db.commit()
    db.refresh(empresa_db)
    return empresa_db


def eliminar_empresa(db: Session, empresa_id: int):
    empresa = utils.empresa_existe(db, empresa_id)
    db.query(models.Alumno).filter(models.Alumno.empresa_asignada_id == empresa_id).update(
        {models.Alumno.empresa_asignada_id: None}
    )
    db.delete(empresa)
    db.commit()






#   ALUMNOS

def crear_alumno(db: Session, alumno: schemas.AlumnoCreate, user: models.User):
    existe = db.query(models.Alumno).filter(models.Alumno.email == alumno.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    nuevo_alumno = models.Alumno(**alumno.model_dump(), registrado_por=user.id)
    db.add(nuevo_alumno)
    db.commit()
    db.refresh(nuevo_alumno)
    return nuevo_alumno


def editar_alumno(db: Session, alumno_id: int, datos: schemas.AlumnoUpdate):
    alumno_db = utils.alumno_existe(db, alumno_id)
    update_data = datos.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(alumno_db, key, value)
    db.commit()
    db.refresh(alumno_db)
    return alumno_db


def eliminar_alumno(db: Session, alumno_id: int):
    alumno = utils.alumno_existe(db, alumno_id)
    if alumno.empresa_asignada_id:
        utils.devolver_plaza_empresa(db, alumno.empresa_asignada_id)
    db.delete(alumno)
    db.commit()





    #   PROFESORES / USUARIOS

def crear_profesor(db: Session, user: schemas.UserCreate):
    existe = db.query(models.User).filter(models.User.email == user.email).first()
    if existe:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    nuevo_profe = models.User(
        email=user.email,
        full_name=user.full_name,
        password=utils.get_password_hash(user.password),
        role="profesor"
    )
    db.add(nuevo_profe)
    db.commit()
    db.refresh(nuevo_profe)
    return nuevo_profe


def editar_profesor(db: Session, profe_id: int, datos: schemas.UserUpdate):
    profe = utils.profesor_existe(db, profe_id)
    update_data = datos.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["password"] = utils.get_password_hash(update_data["password"])
    for key, value in update_data.items():
        setattr(profe, key, value)
    db.commit()
    db.refresh(profe)
    return profe


def eliminar_profesor(db: Session, profe_id: int, current_user: models.User):
    profe = utils.profesor_existe(db, profe_id)
    if profe.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario")
    db.delete(profe)
    db.commit()


def registrar_usuario(db: Session, usuario: schemas.UserCreate):
    if utils.obtener_usuario_por_email(db, usuario.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")
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


def eliminar_usuario(db: Session, user_id: int, current_user: models.User):
    usuario = utils.profesor_existe(db, user_id)
    if usuario.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario administrador")
    db.delete(usuario)
    db.commit()