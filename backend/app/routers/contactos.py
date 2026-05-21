from .. import models, schemas, auth_tokens, utils, services
from ..database import get_db
from ..auth_tokens import *
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional


router = APIRouter(tags=["Contactos y Asignaciones"])

permiso_admin_prof = RoleChecker(["admin", "profesor"])


#   CREAR
@router.post("/contactos/", response_model=schemas.ContactoOut, status_code=201)
def registrar_contacto(
    contacto: schemas.ContactoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin_prof)
):
    return services.crear_contacto(db, contacto, current_user)




#   EDITAR 

@router.put("/{contacto_id}", status_code=status.HTTP_200_OK)
def editar_contacto(
    contacto_id: int,
    contacto_actualizado: schemas.ContactoBase,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    return services.editar_contacto(db, contacto_id, contacto_actualizado)




#   ELIMINAR

@router.delete("/{contacto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_contacto(
    contacto_id: int,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    services.eliminar_contacto(db, contacto_id)







#   LISTAR

@router.get("/contactos/", response_model=List[schemas.ContactoOut])
def listar_todos_los_contactos(
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    return db.query(models.ContactoEmpresa).order_by(models.ContactoEmpresa.fecha_contacto.desc()).all()






#   LISTAR RECIENTES

@router.get("/contactos/recientes", response_model=List[schemas.ContactoOut])
def ver_contactos_recientes(
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    return db.query(models.ContactoEmpresa)\
             .order_by(models.ContactoEmpresa.fecha_contacto.desc())\
             .limit(3).all()




#   ASIGNAR ALUMNO A EMPRESA

@router.post("/asignaciones/{alumno_id}/{empresa_id}")
def asignar_alumno_a_empresa(
    alumno_id: int,
    empresa_id: int,
    tutor_docente_id: Optional[int] = None,
    tutor_laboral_nombre: Optional[str] = None,
    horas: Optional[int] = 380,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    alumno = utils.alumno_existe(db, alumno_id)
    empresa = utils.empresa_existe(db, empresa_id)

    if empresa.plazas_totales <= 0:
        raise HTTPException(status_code=400, detail=f"La empresa {empresa.nombre} no tiene plazas disponibles")
    if alumno.empresa_asignada_id:
        raise HTTPException(status_code=400, detail="El alumno ya tiene una empresa asignada")

    alumno.empresa_asignada_id = empresa.id
    empresa.plazas_totales -= 1

    if tutor_docente_id is not None:
        docente = db.query(models.User).filter(models.User.id == tutor_docente_id).first()
        if not docente:
            raise HTTPException(status_code=404, detail="El tutor docente especificado no existe")
        alumno.tutor_docente_id = tutor_docente_id
        alumno.tutor_docente_nombre = docente.full_name or docente.email

    # Set workplace tutor details
    if tutor_laboral_nombre:
        alumno.tutor_laboral_nombre = tutor_laboral_nombre
        # If they match the company's main contact or any of the additional tutors, copy details
        tutor_adicional = next((t for t in empresa.tutores if t.nombre == tutor_laboral_nombre), None)
        if empresa.contacto_nombre == tutor_laboral_nombre:
            alumno.tutor_laboral_dni = empresa.contacto_dni
            alumno.tutor_laboral_contacto = f"{empresa.contacto_email or ''} | {empresa.contacto_telefono or ''}".strip(" | ")
        elif tutor_adicional:
            alumno.tutor_laboral_dni = tutor_adicional.dni
            alumno.tutor_laboral_contacto = f"{tutor_adicional.email or ''} | {tutor_adicional.telefono or ''}".strip(" | ")
        else:
            alumno.tutor_laboral_dni = None
            alumno.tutor_laboral_contacto = None
    else:
        alumno.tutor_laboral_nombre = empresa.contacto_nombre or "Pendiente de Asignar"
        alumno.tutor_laboral_dni = empresa.contacto_dni
        alumno.tutor_laboral_contacto = f"{empresa.contacto_email or ''} | {empresa.contacto_telefono or ''}".strip(" | ")

    # Guardar en el historial de prácticas reales del alumno de forma persistente
    from datetime import datetime
    curso_nombre = f"Curso {datetime.now().year} - {datetime.now().year + 1}"
    if alumno.ciclo:
        curso_nombre = f"Curso {alumno.ciclo.ano_inicio} - {alumno.ciclo.ano_fin} ({alumno.ciclo.nombre})"
    
    historial_entry = models.HistorialPractica(
        alumno_id=alumno.id,
        curso=curso_nombre,
        tipo="FCT / Dual",
        empresa=empresa.nombre,
        horas=horas,
        resultado="APTO"
    )
    db.add(historial_entry)

    db.commit()
    return {"message": f"Alumno {alumno.nombre} asignado a {empresa.nombre} con éxito"}



#   ELIMINAR ASIGNACION DE ALUMNO A EMPRESA

@router.delete("/asignaciones/{alumno_id}")
def eliminar_asignacion(
    alumno_id: int,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    alumno = utils.alumno_existe(db, alumno_id)
    if not alumno.empresa_asignada_id:
        raise HTTPException(status_code=404, detail="El alumno no tiene asignación")

    empresa = utils.empresa_existe(db, alumno.empresa_asignada_id)
    empresa.plazas_totales += 1
    
    alumno.empresa_asignada_id = None
    alumno.tutor_docente_id = None
    alumno.tutor_docente_nombre = None
    alumno.tutor_laboral_nombre = None
    alumno.tutor_laboral_dni = None
    alumno.tutor_laboral_contacto = None
    
    db.commit()
    return {"mensaje": "Asignación eliminada correctamente"}