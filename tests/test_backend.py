import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.main import app
from backend.app.database import get_db, Base
from backend.app import models, utils

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_final.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def limpiar_bd():
    yield
    db = TestingSessionLocal()
    db.query(models.ContactoEmpresa).delete()
    db.query(models.Alumno).delete()
    db.query(models.Empresa).delete()
    db.query(models.User).delete()
    db.commit()
    db.close()

@pytest.fixture
def client():
    with TestClient(app) as c:
        db = TestingSessionLocal()
        usuario = models.User(
            email="test@test.com",
            full_name="Profesor Test",
            password=utils.get_password_hash("password123"),
            role="profesor"
        )
        db.add(usuario)
        db.commit()
        db.close()
        resp = c.post("/api/v1/auth/login", data={
            "username": "test@test.com",
            "password": "password123"
        })
        token = resp.json()["access_token"]
        c.headers.update({"Authorization": f"Bearer {token}"})
        yield c

@pytest.fixture
def admin(client):
    db = TestingSessionLocal()
    admin = models.User(
        email="admin@test.com",
        full_name="Admin Test",
        password=utils.get_password_hash("admin123"),
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.close()
    resp = client.post("/api/v1/auth/login", data={
        "username": "admin@test.com",
        "password": "admin123"
    })
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

# --- EMPRESAS ---

def test_crear_empresa(client):
    resp = client.post("/api/v1/empresas/", json={
        "nombre": "Empresa A", "cif": "A12345678", "contacto": "Juan"
    })
    assert resp.status_code == 201
    assert resp.json()["nombre"] == "Empresa A"
    assert resp.json()["cif"] == "A12345678"

def test_listar_empresas(client):
    client.post("/api/v1/empresas/", json={"nombre": "E1", "cif": "C1"})
    client.post("/api/v1/empresas/", json={"nombre": "E2", "cif": "C2"})
    resp = client.get("/api/v1/empresas/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2

def test_obtener_empresa(client):
    emp_id = client.post("/api/v1/empresas/", json={
        "nombre": "E1", "cif": "C1"
    }).json()["id"]
    resp = client.get(f"/api/v1/empresas/{emp_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == emp_id

def test_editar_empresa(client):
    emp_id = client.post("/api/v1/empresas/", json={
        "nombre": "Original", "cif": "C1"
    }).json()["id"]
    resp = client.put(f"/api/v1/empresas/{emp_id}", json={"nombre": "Editada"})
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Editada"

def test_eliminar_empresa(client):
    emp_id = client.post("/api/v1/empresas/", json={
        "nombre": "E1", "cif": "C1"
    }).json()["id"]
    resp = client.delete(f"/api/v1/empresas/{emp_id}")
    assert resp.status_code == 204

def test_unicidad_cif_empresa(client):
    client.post("/api/v1/empresas/", json={"nombre": "A", "cif": "A12345678"})
    resp = client.post("/api/v1/empresas/", json={"nombre": "B", "cif": "A12345678"})
    assert resp.status_code == 400
    assert "CIF ya está registrado" in resp.json()["detail"]

def test_empresa_no_encontrada(client):
    resp = client.get("/api/v1/empresas/99999")
    assert resp.status_code == 404

# --- ALUMNOS ---

def test_crear_alumno(client):
    resp = client.post("/api/v1/alumnos/", json={
        "nombre": "Marcos", "apellido": "García", "email": "marcos@test.com"
    })
    assert resp.status_code == 201
    assert resp.json()["email"] == "marcos@test.com"

def test_listar_alumnos(client):
    client.post("/api/v1/alumnos/", json={"nombre": "A", "apellido": "B", "email": "a@a.com"})
    client.post("/api/v1/alumnos/", json={"nombre": "C", "apellido": "D", "email": "c@c.com"})
    resp = client.get("/api/v1/alumnos/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2

def test_editar_alumno(client):
    alu_id = client.post("/api/v1/alumnos/", json={
        "nombre": "Antes", "apellido": "B", "email": "a@a.com"
    }).json()["id"]
    resp = client.put(f"/api/v1/alumnos/{alu_id}", json={"nombre": "Después"})
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Después"

def test_eliminar_alumno(client):
    alu_id = client.post("/api/v1/alumnos/", json={
        "nombre": "A", "apellido": "B", "email": "a@a.com"
    }).json()["id"]
    resp = client.delete(f"/api/v1/alumnos/{alu_id}")
    assert resp.status_code == 204

def test_unicidad_email_alumno(client):
    client.post("/api/v1/alumnos/", json={"nombre": "A", "apellido": "B", "email": "a@a.com"})
    resp = client.post("/api/v1/alumnos/", json={"nombre": "C", "apellido": "D", "email": "a@a.com"})
    assert resp.status_code == 400
    assert "email ya está registrado" in resp.json()["detail"]

# --- CONTACTOS ---

def test_crear_contacto_acepta_suma_plazas(client):
    emp_id = client.post("/api/v1/empresas/", json={
        "nombre": "E", "cif": "C1", "plazas_totales": 0
    }).json()["id"]
    client.post("/api/v1/contactos/", json={
        "empresa_id": emp_id, "estado": "Acepta", "plazas_ofrecidas": 5,
        "fecha_inicio": "2026-05-01T00:00:00", "fecha_fin": "2026-06-01T00:00:00", "horas_totales": 400
    })
    emp = client.get(f"/api/v1/empresas/{emp_id}").json()
    assert emp["plazas_totales"] == 5

def test_crear_contacto_rechaza_no_suma_plazas(client):
    emp_id = client.post("/api/v1/empresas/", json={
        "nombre": "E", "cif": "C1", "plazas_totales": 0
    }).json()["id"]
    client.post("/api/v1/contactos/", json={
        "empresa_id": emp_id, "estado": "Rechaza", "plazas_ofrecidas": 5,
        "fecha_inicio": "2026-05-01T00:00:00", "fecha_fin": "2026-06-01T00:00:00", "horas_totales": 400
    })
    emp = client.get(f"/api/v1/empresas/{emp_id}").json()
    assert emp["plazas_totales"] == 0

def test_logica_plazas_contacto_acepta(client):
    emp_id = client.post("/api/v1/empresas/", json={
        "nombre": "E", "cif": "T00000000", "contacto": "Marcos"
    }).json()["id"]
    client.post("/api/v1/contactos/", json={
        "empresa_id": emp_id, "estado": "Acepta", "plazas_ofrecidas": 3,
        "fecha_inicio": "2026-05-01T00:00:00", "fecha_fin": "2026-06-01T00:00:00", "horas_totales": 400
    })
    emp = client.get(f"/api/v1/empresas/{emp_id}").json()
    assert emp["plazas_totales"] == 3

# --- ASIGNACIONES ---

def test_asignar_alumno_a_empresa(client):
    emp_id = client.post("/api/v1/empresas/", json={
        "nombre": "E", "cif": "C1", "plazas_totales": 2
    }).json()["id"]
    alu_id = client.post("/api/v1/alumnos/", json={
        "nombre": "A", "apellido": "B", "email": "a@a.com"
    }).json()["id"]
    resp = client.post(f"/api/v1/asignaciones/{alu_id}/{emp_id}")
    assert resp.status_code == 200

def test_devolucion_plaza_al_borrar_alumno(client):
    emp_id = client.post("/api/v1/empresas/", json={
        "nombre": "E", "cif": "1", "plazas_totales": 1
    }).json()["id"]
    alu_id = client.post("/api/v1/alumnos/", json={
        "nombre": "A", "apellido": "B", "email": "a@a.es"
    }).json()["id"]
    client.post(f"/api/v1/asignaciones/{alu_id}/{emp_id}")
    client.delete(f"/api/v1/alumnos/{alu_id}")
    emp = client.get(f"/api/v1/empresas/{emp_id}").json()
    assert emp["plazas_totales"] == 1

# --- AUTH ---

def test_login_correcto(client):
    resp = TestClient(app).post("/api/v1/auth/login", data={
        "username": "test@test.com",
        "password": "password123"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_login_incorrecto():
    resp = TestClient(app).post("/api/v1/auth/login", data={
        "username": "noexiste@test.com",
        "password": "wrongpass"
    })
    assert resp.status_code == 401

def test_ruta_protegida_sin_token():
    resp = TestClient(app).post("/api/v1/empresas/", json={
        "nombre": "E", "cif": "C1"
    })
    assert resp.status_code == 401