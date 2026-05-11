from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth_tokens, utils
from ..database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, auth_tokens, database, schemas 
from ..auth_tokens import *


router = APIRouter(
    tags=["Contactos y Asignaciones"]
)

permiso_admin_prof = RoleChecker(["admin", "profesor"])
permiso_admin = RoleChecker(["admin"])





#   REGISTRAR CONTACTO

@router.post("/contactos/", response_model=schemas.ContactoOut, status_code=201)
def registrar_contacto(
    contacto: schemas.ContactoCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin_prof)
):
    # Usamos la validación de utils 
    empresa = utils.empresa_existe(db, contacto.empresa_id)

    # Crea el registro (asignando datos del profesor actual)
    nuevo_contacto = models.ContactoEmpresa(
        **contacto.model_dump(),
        profesor_id=current_user.id, 
        nombre_profesor=current_user.full_name 
    )
    
    if contacto.estado == "Acepta":
        empresa.plazas_totales += contacto.plazas_ofrecidas

    db.add(nuevo_contacto)
    db.commit()
    db.refresh(nuevo_contacto)
    return nuevo_contacto





#   EDITAR REGISTRO DE CONTACTO

@router.put("/{contacto_id}", status_code=status.HTTP_200_OK)
def editar_contacto(
    contacto_id: int,
    contacto_actualizado: schemas.ContactoBase,
    db: Session = Depends(database.get_db),
    _ = Depends(permiso_admin_prof)
):
    # Valida el contacto
    contacto_db = utils.contacto_existe(db, contacto_id)

    # Actualiza los campos
    # Usamos exclude_unset=True para no sobreescribir con Nones si el esquema lo permite
    contacto_data = contacto_actualizado.model_dump(exclude_unset=True) 
    
    for key, value in contacto_data.items():
        setattr(contacto_db, key, value)

    
    db.commit()
    db.refresh(contacto_db)
    
    return contacto_db


#   ELIMINAR CONTACTO

@router.delete("/{contacto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_contacto(
    contacto_id: int,
    db: Session = Depends(database.get_db),
    _ = Depends(permiso_admin_prof)
):
    # Valida existencia 
    contacto = utils.contacto_existe(db, contacto_id)

    # Elimina directamente el objeto encontrado
    db.delete(contacto)
    db.commit()
    
    return None





#   LISTADO DE CONTACTOS CON EMPRESA

@router.get("/contactos/", response_model=List[schemas.ContactoOut])
def listar_todos_los_contactos(
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):  
  
    # Devolvemos todos los registros de la tabla contactos
    return db.query(models.ContactoEmpresa).order_by(models.ContactoEmpresa.fecha_contacto.desc()).all()




#   ÚLTIMOS CONTACTOS CON EMPRESA

@router.get("/contactos/recientes", response_model=List[schemas.ContactoOut])
def ver_contactos_recientes(
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)

):
    
    return db.query(models.ContactoEmpresa)\
             .order_by(models.ContactoEmpresa.fecha_contacto.desc())\
             .limit(3).all() #cambiando el numero en el paréntesis de ".limit()" cambia cuántos contactos hay en el listado



#   ASIGNACIÓN ALUMNO A EMPRESA

@router.post("/asignaciones/{alumno_id}/{empresa_id}")
def asignar_alumno_a_empresa(
    alumno_id: int, 
    empresa_id: int, 
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    # Valida existencia
    alumno = utils.alumno_existe(db, alumno_id)
    empresa = utils.empresa_existe(db, empresa_id)


    # Valida plazas de la empresa
    if empresa.plazas_totales <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"La empresa {empresa.nombre} no tiene plazas disponibles"
        )

    if alumno.empresa_asignada_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El alumno ya tiene una empresa asignada"
        )

    # Proceso de asignación
    alumno.empresa_asignada_id = empresa.id
    empresa.plazas_totales -= 1
    
    db.commit()
    
    return {"mensaje": f"Alumno {alumno.nombre} asignado a {empresa.nombre} con éxito"}






#   ELIMINAR ASIGNACIÓN DE ALUMNO EN EMPRESA

@router.delete("/asignaciones/{alumno_id}")
def eliminar_asignacion(
    alumno_id: int,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):

    #Comprueba si el alumno está asignado a una plaza
    alumno = db.query(models.Alumno).filter(models.Alumno.id == alumno_id).first()
    if not alumno or not alumno.empresa_asignada_id:
        raise HTTPException(status_code=404, detail="El alumno no tiene asignación")

    # Devolver plaza a la empresa
    empresa = db.query(models.Empresa).filter(models.Empresa.id == alumno.empresa_asignada_id).first()
    if empresa:
        empresa.plazas_totales += 1
    
    alumno.empresa_asignada_id = None
    db.commit()
    return {"mensaje": "Asignación eliminada correctamente"}