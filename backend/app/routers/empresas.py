from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth_tokens, utils, services
from ..database import get_db
from ..auth_tokens import *
import csv
import io

router = APIRouter(
    prefix="/empresas",
    tags=["Empresas"]
)

permiso_admin_prof = RoleChecker(["admin", "profesor"])
permiso_admin = RoleChecker(["admin"])

#   LISTAR

@router.get("/", response_model=List[schemas.EmpresaOut])
def listar_empresas(
    db: Session = Depends(get_db),
):
    return db.query(models.Empresa).all()

#   VER UNA EMPRESA

@router.get("/{empresa_id}", response_model=schemas.EmpresaOut)
def obtener_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
):
    return utils.empresa_existe(db, empresa_id)

#   CREAR

@router.post("/", response_model=schemas.EmpresaOut, status_code=201)
def crear_empresa(
    empresa: schemas.EmpresaCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin_prof)
):
    return services.crear_empresa(db, empresa, current_user)

#   IMPORTAR POR CSV

@router.post("/importar-empresas", status_code=201)
async def importar_empresas(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin_prof)
):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode('utf-8')))

    records_created = 0
    records_skipped = 0

    for row in reader:
        nombre = row.get('nombre')
        cif = row.get('cif')

        if not nombre or not cif:
            records_skipped += 1
            continue

        if utils.obtener_empresa_por_cif(db, cif):
            records_skipped += 1
            continue

        try:
            new_company = models.Empresa(
                nombre=nombre,
                cif=cif,
                plazas_totales=int(row.get('plazas', 0) or 0),
                direccion=row.get('direccion') or None,
                web=row.get('web') or None,
                email=row.get('email') or None,
                telefono=row.get('telefono') or None,
                contacto_nombre=row.get('contacto_nombre') or None,
                contacto_email=row.get('contacto_email') or None,
                contacto_telefono=row.get('contacto_telefono') or None,
                contacto_dni=row.get('contacto_dni') or None,
                registrado_por=current_user.id
            )
            db.add(new_company)
            records_created += 1
        except ValueError:
            records_skipped += 1
            continue

    db.commit()
    return {
        "status": "completed",
        "new_records": records_created,
        "skipped": records_skipped
    }

#   EDITAR

@router.put("/{empresa_id}", response_model=schemas.EmpresaOut)
def actualizar_empresa(
    empresa_id: int,
    datos: schemas.EmpresaUpdate,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    return services.editar_empresa(db, empresa_id, datos)

#   ELIMINAR

@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    services.eliminar_empresa(db, empresa_id)

#   VER CONTACTOS CON LA EMPRESA

@router.get("/{empresa_id}/contactos", response_model=List[schemas.ContactoOut])
def obtener_contactos_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
):
    utils.empresa_existe(db, empresa_id)
    return db.query(models.ContactoEmpresa).filter(models.ContactoEmpresa.empresa_id == empresa_id).all()