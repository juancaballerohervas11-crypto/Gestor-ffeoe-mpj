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

    registros_creados = 0
    registros_saltados = 0

    for row in reader:
        nombre = row.get('nombre')
        cif = row.get('cif')

        if not nombre or not cif:
            registros_saltados += 1
            continue

        if utils.obtener_empresa_por_cif(db, cif):
            registros_saltados += 1
            continue

        try:
            nueva_empresa = models.Empresa(
                nombre=nombre,
                cif=cif,
                contacto=row.get('contacto'),
                plazas_totales=int(row.get('plazas', 0)),
                registrado_por=current_user.id
            )
            db.add(nueva_empresa)
            registros_creados += 1
        except ValueError:
            registros_saltados += 1
            continue

    db.commit()
    return {
        "status": "completado",
        "nuevos_registros": registros_creados,
        "duplicados_o_invalidos_saltados": registros_saltados
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