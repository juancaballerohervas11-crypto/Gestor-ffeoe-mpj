from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, auth_tokens, utils
from ..database import get_db
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from typing import List
from ..auth_tokens import *


router = APIRouter(
    prefix="/empresas",
    tags=["Empresas"]
)

permiso_admin_prof = RoleChecker(["admin", "profesor"])
permiso_admin = RoleChecker(["admin"])





#   LISTADO DE EMPRESAS 

@router.get("/", response_model=List[schemas.EmpresaOut])
def listar_empresas(
    db: Session = Depends(get_db),
):
    return db.query(models.Empresa).all()




#   CREACIÓN MANUAL

@router.post("/empresas/", response_model=schemas.EmpresaOut, status_code=201)
def crear_empresa(
    empresa: schemas.EmpresaCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin_prof)
):
    
    # Valida si el CIF ya existe
    existe = db.query(models.Empresa).filter(models.Empresa.cif == empresa.cif).first()
    if existe:
        raise HTTPException(status_code=400, detail="El CIF ya está registrado")

    nueva_empresa = models.Empresa(**empresa.model_dump(), registrado_por=current_user.id)
    db.add(nueva_empresa)
    db.commit()
    db.refresh(nueva_empresa)
    return nueva_empresa




#   IMPORTACIÓN MEDIANTE .csv

@router.post("/importar-empresas", status_code=201)
async def importar_empresas(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_tokens.get_current_user),
    _ = Depends(permiso_admin_prof)
):
    # Lectura del archivo
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode('utf-8')))

    registros_creados = 0
    registros_saltados = 0

    for row in reader:
        nombre = row.get('nombre')
        cif = row.get('cif')

        # Validación básica de campos obligatorios
        if not nombre or not cif:
            registros_saltados += 1
            continue

        # Verifica duplicados 
        if utils.obtener_empresa_por_cif(db, cif):
            registros_saltados += 1
            continue 

        # Crea las nuevas empresas
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




#   EDITAR EMPRESA

@router.put("/empresas/{empresa_id}", response_model=schemas.EmpresaOut)
def actualizar_empresa(
    empresa_id: int, 
    datos: schemas.EmpresaUpdate, 
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    # Valida existencia
    empresa_db = utils.empresa_existe(db, empresa_id)

    # Extrae los datos
    datos_dict = datos.model_dump(exclude_unset=True)
    
    # Actualiza el objeto encontrado
    for key, value in datos_dict.items():
        setattr(empresa_db, key, value)
    
    
    db.commit()
    db.refresh(empresa_db)

    return empresa_db





#   ELIMINAR EMPRESA

@router.delete("/empresas/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
    _ = Depends(permiso_admin_prof)
):
    # Valida existencia 
    empresa = utils.empresa_existe(db, empresa_id)
    
    # Libera a los alumnos asignados
    db.query(models.Alumno).filter(models.Alumno.empresa_asignada_id == empresa_id).update(
        {models.Alumno.empresa_asignada_id: None}
    )

    # Borra la empresa
    db.delete(empresa)
    db.commit()
    
    return None


#   LISTADO DE CONTACTOS CON LA EMPRESA

@router.get("/{empresa_id}/contactos", response_model=List[schemas.ContactoOut])
def obtener_contactos_empresa(
    empresa_id: int,
    db: Session = Depends(get_db),
):
    # Valida existencia
    utils.empresa_existe(db, empresa_id)
    
    # Filtra los contactos directamente
    return db.query(models.ContactoEmpresa).filter(models.ContactoEmpresa.empresa_id == empresa_id).all()