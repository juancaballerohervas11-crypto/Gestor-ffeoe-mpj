from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth_tokens import get_current_user, RoleChecker

router = APIRouter(
    prefix="/ciclos",
    tags=["Ciclos"]
)

# Permitir que solo el administrador cree o modifique ciclos, pero cualquiera puede listarlos
allow_admin = RoleChecker(["admin", "coordinador"])


@router.post("/", response_model=schemas.CicloOut, status_code=status.HTTP_201_CREATED)
def crear_ciclo(
    ciclo: schemas.CicloCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(allow_admin)
):
    """
    Crea un nuevo ciclo. Solo para Administrador / Coordinador.
    """
    nuevo_ciclo = models.Ciclo(**ciclo.model_dump())
    db.add(nuevo_ciclo)
    db.commit()
    db.refresh(nuevo_ciclo)
    return nuevo_ciclo


@router.get("/", response_model=List[schemas.CicloOut])
def listar_ciclos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Lista todos los ciclos disponibles.
    """
    ciclos = db.query(models.Ciclo).all()
    return ciclos


@router.post("/{ciclo_id}/asignar_profesor", status_code=status.HTTP_200_OK)
def asignar_profesor_a_ciclo(
    ciclo_id: int,
    asignacion: schemas.AsignarProfesor,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(allow_admin)
):
    """
    Asigna un profesor a un ciclo existente.
    Solo para Administrador / Coordinador.
    """
    # Buscar el ciclo
    ciclo = db.query(models.Ciclo).filter(models.Ciclo.id == ciclo_id).first()
    if not ciclo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ciclo no encontrado")
        
    # Buscar el profesor (Usuario)
    profesor = db.query(models.User).filter(models.User.id == asignacion.profesor_id).first()
    if not profesor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesor no encontrado")
        
    # Verificar que el usuario asignado tenga el rol apropiado, opcional pero buena práctica
    # if profesor.role not in ["profesor", "admin", "coordinador"]:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es un profesor")

    # Verificar si ya está asignado
    if profesor in ciclo.profesores:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El profesor ya está asignado a este ciclo")

    ciclo.profesores.append(profesor)
    db.commit()
    
    return {"mensaje": f"Profesor {profesor.email} asignado correctamente al ciclo {ciclo.nombre}"}


@router.put("/{ciclo_id}", response_model=schemas.CicloOut)
def modificar_ciclo(
    ciclo_id: int,
    datos: schemas.CicloUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(allow_admin)
):
    """
    Modifica un ciclo existente.
    Solo para Administrador / Coordinador.
    """
    from .. import utils
    ciclo_db = utils.ciclo_existe(db, ciclo_id)
    
    datos_dict = datos.model_dump(exclude_unset=True)
    for key, value in datos_dict.items():
        setattr(ciclo_db, key, value)
        
    db.commit()
    db.refresh(ciclo_db)
    return ciclo_db


@router.delete("/{ciclo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ciclo(
    ciclo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(allow_admin)
):
    """
    Elimina un ciclo existente.
    Solo para Administrador / Coordinador.
    """
    from .. import utils
    ciclo_db = utils.ciclo_existe(db, ciclo_id)
    
    # Desasignar alumnos de este ciclo antes de borrarlo (para evitar errores de clave foránea)
    db.query(models.Alumno).filter(models.Alumno.ciclo_id == ciclo_id).update(
        {models.Alumno.ciclo_id: None}
    )
    
    db.delete(ciclo_db)
    db.commit()
    return None


@router.post("/{ciclo_id}/asignar_alumno/{alumno_id}", status_code=status.HTTP_200_OK)
def asignar_alumno_a_ciclo(
    ciclo_id: int,
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Asigna un alumno a un ciclo.
    Permitido para Administrador, Coordinador y Profesor.
    """
    from .. import utils
    # Verificar permisos
    if current_user.role not in ["admin", "coordinador", "profesor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes los permisos necesarios para realizar esta acción"
        )
        
    ciclo = utils.ciclo_existe(db, ciclo_id)
    alumno = utils.alumno_existe(db, alumno_id)
    
    alumno.ciclo_id = ciclo.id
    db.commit()
    
    return {"mensaje": f"Alumno {alumno.nombre} {alumno.apellido} asignado correctamente al ciclo {ciclo.nombre}"}


@router.delete("/{ciclo_id}/desasignar_alumno/{alumno_id}", status_code=status.HTTP_200_OK)
def desasignar_alumno_de_ciclo(
    ciclo_id: int,
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Desasigna un alumno de un ciclo.
    Permitido para Administrador, Coordinador y Profesor.
    """
    from .. import utils
    # Verificar permisos
    if current_user.role not in ["admin", "coordinador", "profesor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes los permisos necesarios para realizar esta acción"
        )
        
    ciclo = utils.ciclo_existe(db, ciclo_id)
    alumno = utils.alumno_existe(db, alumno_id)
    
    if alumno.ciclo_id != ciclo.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El alumno no pertenece a este ciclo"
        )
        
    alumno.ciclo_id = None
    db.commit()
    
    return {"mensaje": f"Alumno {alumno.nombre} {alumno.apellido} desasignado correctamente del ciclo {ciclo.nombre}"}