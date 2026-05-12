from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime



#   ESQUEMAS DE USUARIO 

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None 
    role: Optional[str] = "user"

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int

    # Esto permite que Pydantic lea modelos de SQLAlchemy
    class Config:
        from_attributes = True 

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None




# ESQUEMAS DE LOGIN

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None




# ESQUEMA DE EMPRESA 

class EmpresaOut(BaseModel):
    id: int
    nombre: str
    cif: str
    contacto: Optional[str] = None
    registrado_por: int

    class Config:
        from_attributes = True



#   ESQUEMA DE ALUMNO

class AlumnoOut(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: EmailStr
    registrado_por: Optional[int]=None
    empresa_asignada_id: Optional[int]=None

    class Config:
        from_attributes = True



#   ESQUEMA CONTACTO

class ContactoBase(BaseModel):
    empresa_id: int
    estado: str  # Ejemplo: 'Acepta', 'Rechaza'
    
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    horas_totales: int = 0
    
    plazas_ofrecidas: int = 0
    observaciones: Optional[str] = None
    
    class Config:
        from_attributes=True




# ESQUEMAS DE CREACIÓN DE EMPRESAS Y ALUMNOS

class EmpresaCreate(BaseModel):
    nombre: str
    cif: str
    contacto: Optional[str] = None
    # plazas_totales empieza en 0 por defecto en el modelo

class AlumnoCreate(BaseModel):
    nombre: str
    apellido: str
    email: Optional[EmailStr]




# ESQUEMAS DE REGISTRO DE CONTACTO

class ContactoCreate(BaseModel):
    empresa_id: int
    estado: str  # Ejemplo: 'Acepta', 'Rechaza'
    
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    horas_totales: int = 0
    
    plazas_ofrecidas: int = 0
    observaciones: Optional[str] = None



# ESQUEMAS DE EDICION DE PROFESORES, ALUMNOS Y EMPRESAS

class EmpresaUpdate(BaseModel):
    nombre: Optional[str] = None
    cif: Optional[str] = None
    contacto: Optional[str] = None

class AlumnoUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None

class ProfesorUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None




# VER EL CONTACTO (RESPUESTA)

class ContactoOut(ContactoCreate):
    id: int

    profesor_id: Optional[int]
    nombre_profesor: Optional[str] = None
    
    fecha_contacto: datetime

    class Config:
        from_attributes = True


#   EDITAR CONTACTO
class ContactoUpdate(BaseModel):
    empresa_id: int
    estado: str  # Ejemplo: 'Acepta', 'Rechaza'
    
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    horas_totales: int = 0
    
    plazas_ofrecidas: int = 0
    observaciones: Optional[str] = None
    
    class Config:
        from_attributes = True





# ESQUEMA DE ASIGNACIÓN DE ALUMNOS A LAS PLAZAS

class AsignacionAlumno(BaseModel):
    alumno_id: int
    empresa_id: int
    fecha_inicio: datetime
    observaciones: Optional[str] = None