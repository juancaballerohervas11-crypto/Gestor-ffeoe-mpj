from sqlalchemy.orm import Session
from . import models, schemas, utils
from fastapi import HTTPException


#   CONTACTOS

def crear_contacto(db: Session, contacto: schemas.ContactoCreate, user: models.User):
    empresa = utils.empresa_existe(db, contacto.empresa_id)
    new_contact = models.ContactoEmpresa(
        **contacto.model_dump(),
        profesor_id=user.id,
        nombre_profesor=user.full_name
    )
    if contacto.estado == "Acepta":
        empresa.plazas_totales += contacto.plazas_ofrecidas
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


def editar_contacto(db: Session, contacto_id: int, contacto_actualizado: schemas.ContactoBase):
    contact_record = utils.contacto_existe(db, contacto_id)
    empresa = utils.empresa_existe(db, contact_record.empresa_id)

    previous_status = contact_record.estado
    new_status = contacto_actualizado.estado

    if previous_status == "Acepta" and new_status != "Acepta":
        empresa.plazas_totales -= contact_record.plazas_ofrecidas
    elif previous_status != "Acepta" and new_status == "Acepta":
        empresa.plazas_totales += contacto_actualizado.plazas_ofrecidas

    contact_data = contacto_actualizado.model_dump(exclude_unset=True)
    for key, value in contact_data.items():
        setattr(contact_record, key, value)

    db.commit()
    db.refresh(contact_record)
    return contact_record


def eliminar_contacto(db: Session, contacto_id: int):
    contacto = utils.contacto_existe(db, contacto_id)
    db.delete(contacto)
    db.commit()





    #   EMPRESAS

def crear_empresa(db: Session, empresa: schemas.EmpresaCreate, user: models.User):
    exists = db.query(models.Empresa).filter(models.Empresa.cif == empresa.cif).first()
    if exists:
        raise HTTPException(status_code=400, detail="El CIF ya está registrado")
    new_company = models.Empresa(**empresa.model_dump(), registrado_por=user.id)
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return new_company


def editar_empresa(db: Session, empresa_id: int, datos: schemas.EmpresaUpdate):
    empresa_db = utils.empresa_existe(db, empresa_id)
    update_data = datos.model_dump(exclude_unset=True)
    for key, value in update_data.items():
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

def crear_usuario_alumno_si_no_existe(db: Session, email: str, full_name: str, dni: str = None):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        default_pwd = dni if (dni and len(dni.strip()) > 0) else "123456"
        user = models.User(
            email=email,
            full_name=full_name,
            password=utils.get_password_hash(default_pwd),
            role="alumno"
        )
        db.add(user)
        db.flush()
    return user

def crear_alumno(db: Session, alumno: schemas.AlumnoCreate, user: models.User):
    exists = db.query(models.Alumno).filter(models.Alumno.email == alumno.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Crear cuenta de login
    crear_usuario_alumno_si_no_existe(
        db,
        alumno.email,
        f"{alumno.nombre} {alumno.apellido}",
        alumno.dni
    )
    
    new_student = models.Alumno(**alumno.model_dump(), registrado_por=user.id)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


def editar_alumno(db: Session, alumno_id: int, datos: schemas.AlumnoUpdate):
    student_record = utils.alumno_existe(db, alumno_id)
    update_data = datos.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(student_record, key, value)
    db.commit()
    db.refresh(student_record)
    return student_record


def eliminar_alumno(db: Session, alumno_id: int):
    alumno = utils.alumno_existe(db, alumno_id)
    if alumno.empresa_asignada_id:
        utils.devolver_plaza_empresa(db, alumno.empresa_asignada_id)
    db.delete(alumno)
    db.commit()





    #   PROFESORES / USUARIOS

def crear_profesor(db: Session, user: schemas.UserCreate):
    exists = db.query(models.User).filter(models.User.email == user.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    new_teacher = models.User(
        email=user.email,
        full_name=user.full_name,
        password=utils.get_password_hash(user.password),
        role="profesor"
    )
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher


def editar_profesor(db: Session, profe_id: int, datos: schemas.UserUpdate):
    teacher = utils.profesor_existe(db, profe_id)
    update_data = datos.model_dump(exclude_unset=True)
    
    if "password" in update_data and update_data["password"]:
        current_password = update_data.get("current_password")
        if not current_password or not utils.verify_password(current_password, teacher.password):
            raise HTTPException(status_code=400, detail="La contraseña antigua es incorrecta")
        
        update_data.pop("current_password", None)
        update_data["password"] = utils.get_password_hash(update_data["password"])
    else:
        update_data.pop("current_password", None)

    for key, value in update_data.items():
        setattr(teacher, key, value)
    db.commit()
    db.refresh(teacher)
    return teacher


def eliminar_profesor(db: Session, profe_id: int, current_user: models.User):
    profe = utils.profesor_existe(db, profe_id)
    if profe.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario")
    db.delete(profe)
    db.commit()


def registrar_usuario(db: Session, usuario: schemas.UserCreate):
    if utils.obtener_usuario_por_email(db, usuario.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    new_user = models.User(
        email=usuario.email,
        full_name=usuario.full_name,
        password=utils.get_password_hash(usuario.password),
        role=usuario.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def eliminar_usuario(db: Session, user_id: int, current_user: models.User):
    usuario = utils.profesor_existe(db, user_id)
    if usuario.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario administrador")
    db.delete(usuario)
    db.commit()


def registrar_alumno_publico(db: Session, reg: schemas.StudentRegister):
    # 1. Verificar si ya existe el Alumno
    exists_alumno = db.query(models.Alumno).filter(models.Alumno.email == reg.email).first()
    if exists_alumno:
        raise HTTPException(status_code=400, detail="El email ya está registrado como alumno")
    
    # 2. Verificar si ya existe el Usuario
    exists_user = db.query(models.User).filter(models.User.email == reg.email).first()
    if exists_user:
        raise HTTPException(status_code=400, detail="El email ya está en uso")
        
    # 3. Crear registro de Usuario para autenticacion
    new_user = models.User(
        email=reg.email,
        full_name=f"{reg.nombre} {reg.apellido}",
        password=utils.get_password_hash(reg.password),
        role="alumno"
    )
    db.add(new_user)
    db.flush()
    
    # 4. Crear registro de Alumno
    new_student = models.Alumno(
        nombre=reg.nombre,
        apellido=reg.apellido,
        email=reg.email,
        dni=reg.dni,
        telefono=reg.telefono,
        ciclo_id=reg.ciclo_id,
        registrado_por=None
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    return new_user