from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone

profesores_ciclos = Table(
    'profesores_ciclos', Base.metadata,
    Column('profesor_id', Integer, ForeignKey('users.id')),
    Column('ciclo_id', Integer, ForeignKey('ciclos.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), server_default='user', nullable=False)

    # Relaciones
    empresas_registradas = relationship("Empresa", back_populates="profesor")
    alumnos_registrados = relationship("Alumno", back_populates="profesor")
    contactos_realizados = relationship("ContactoEmpresa", back_populates="profesor")
    ciclos = relationship("Ciclo", secondary=profesores_ciclos, back_populates="profesores")

class Ciclo(Base):
    __tablename__ = "ciclos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    ano_inicio = Column(Integer, nullable=False)
    ano_fin = Column(Integer, nullable=False)

    # Relación M:N con User (Profesor)
    profesores = relationship("User", secondary=profesores_ciclos, back_populates="ciclos")
    # Relación 1:N con Alumno
    alumnos = relationship("Alumno", back_populates="ciclo")

class Empresa(Base):
    __tablename__ = "empresas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    cif = Column(String(20), unique=True, index=True, nullable=False)
    contacto = Column(String(255), nullable=True)

    # Para borrar el registro de contactos junto con la empresa
    historial_contactos = relationship(
    "ContactoEmpresa",
    back_populates="empresa",
    cascade="all, delete-orphan"
    )
    
    # total de plazas acordadas
    plazas_totales = Column(Integer, default=0)
    
    registrado_por = Column(Integer, ForeignKey("users.id"))
    
    # Relaciones
    profesor = relationship("User", back_populates="empresas_registradas")
    historial_contactos = relationship("ContactoEmpresa", back_populates="empresa")

class Alumno(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    
    registrado_por = Column(Integer, ForeignKey("users.id"))
    
    empresa_asignada_id = Column(Integer, ForeignKey("empresas.id"), nullable=True)
    empresa_asignada = relationship("Empresa")  # ← añadir esta línea

    ciclo_id = Column(Integer, ForeignKey("ciclos.id"), nullable=True)
    ciclo = relationship("Ciclo", back_populates="alumnos")

    telefono = Column(String(20), nullable=True)
    cv_path = Column(String(255), nullable=True)

    profesor = relationship("User", back_populates="alumnos_registrados")

class ContactoEmpresa(Base):
    __tablename__ = "contactos_empresa"

    # Profesor que contacta con la empresa
    profesor_id = Column(Integer, ForeignKey("users.id"))
    nombre_profesor = Column(String(255)) 

    # Información del contacto con la empresa
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"))
    

    estado = Column(String(50)) # Ejemplo: 'Acepta', 'Rechaza', 'Pendiente'

    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    
    horas_totales = Column(Integer, default=0)
    
    plazas_ofrecidas = Column(Integer, default=0)
    observaciones = Column(String(500), nullable=True)
    fecha_contacto = Column(DateTime, default=lambda: datetime.now(timezone.utc))


    # Relaciones para poder hacer consultas cruzadas
    empresa = relationship("Empresa", back_populates="historial_contactos")
    profesor = relationship("User", back_populates="contactos_realizados")