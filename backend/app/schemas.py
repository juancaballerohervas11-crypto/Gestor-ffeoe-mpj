from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime



#   ESQUEMAS DE USUARIO 

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None 
    role: Optional[str] = "user"
    profile_pic: Optional[str] = None

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
    current_password: Optional[str] = None
    profile_pic: Optional[str] = None




# ESQUEMAS DE LOGIN

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None




# ESQUEMAS DE TUTOR LABORAL

class TutorLaboralBase(BaseModel):
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    dni: Optional[str] = None

class TutorLaboralCreate(TutorLaboralBase):
    pass

class TutorLaboralOut(TutorLaboralBase):
    id: int
    empresa_id: int

    class Config:
        from_attributes = True

# ESQUEMA DE EMPRESA 

class EmpresaOut(BaseModel):
    id: int
    nombre: str
    cif: str
    registrado_por: int
    plazas_totales: int = 0

    # Datos generales
    direccion: Optional[str] = None
    web: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None

    # Persona de contacto interna
    contacto_nombre: Optional[str] = None
    contacto_email: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_dni: Optional[str] = None

    # Campo heredado
    contacto: Optional[str] = None

    tutores: List[TutorLaboralOut] = []

    class Config:
        from_attributes = True

#   ESQUEMA DE ALUMNO

class HistorialPracticaOut(BaseModel):
    id: int
    alumno_id: int
    curso: str
    tipo: str
    empresa: str
    horas: int
    resultado: str

    class Config:
        from_attributes = True


class AlumnoOut(BaseModel):
    id: int
    nombre: str
    apellido: str
    email: EmailStr
    dni: Optional[str] = None
    registrado_por: Optional[int] = None
    empresa_asignada_id: Optional[int] = None
    empresa_nombre: Optional[str] = None
    ciclo_id: Optional[int] = None
    telefono: Optional[str] = None
    cv_path: Optional[str] = None
    tutor_docente_id: Optional[int] = None
    tutor_docente_nombre: Optional[str] = None
    tutor_laboral_nombre: Optional[str] = None
    tutor_laboral_dni: Optional[str] = None
    tutor_laboral_contacto: Optional[str] = None
    historial_practicas: List[HistorialPracticaOut] = []

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
    plazas_totales: int = 0

    # Datos generales
    direccion: Optional[str] = None
    web: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None

    # Persona de contacto interna
    contacto_nombre: Optional[str] = None
    contacto_email: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_dni: Optional[str] = None

class AlumnoCreate(BaseModel):
    nombre: str
    apellido: str
    email: Optional[EmailStr]
    dni: Optional[str] = None
    ciclo_id: Optional[int] = None
    telefono: Optional[str] = None
    cv_path: Optional[str] = None



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
    plazas_totales: Optional[int] = None

    # Datos generales
    direccion: Optional[str] = None
    web: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None

    # Persona de contacto interna
    contacto_nombre: Optional[str] = None
    contacto_email: Optional[str] = None
    contacto_telefono: Optional[str] = None
    contacto_dni: Optional[str] = None

class AlumnoUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    dni: Optional[str] = None
    ciclo_id: Optional[int] = None
    telefono: Optional[str] = None
    cv_path: Optional[str] = None

class AlumnoPerfilUpdate(BaseModel):
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None

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


# ESQUEMAS DE CICLOS

class CicloBase(BaseModel):
    nombre: str
    ano_inicio: int
    ano_fin: int

class CicloCreate(CicloBase):
    pass

class CicloUpdate(BaseModel):
    nombre: Optional[str] = None
    ano_inicio: Optional[int] = None
    ano_fin: Optional[int] = None

class CicloOut(CicloBase):
    id: int
    profesores: List[UserOut] = []
    alumnos: List[AlumnoOut] = []

    class Config:
        from_attributes = True

class AsignarProfesor(BaseModel):
    profesor_id: int

class StudentRegister(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str
    dni: Optional[str] = None
    telefono: Optional[str] = None
    ciclo_id: Optional[int] = None
