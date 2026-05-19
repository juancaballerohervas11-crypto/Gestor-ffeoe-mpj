import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.main import app
from backend.app.database import get_db, Base
from backend.app import models, utils
import io

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
def clean_db():
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
        user = models.User(
            email="test@test.com",
            full_name="Profesor Test",
            password=utils.get_password_hash("password123"),
            role="profesor"
        )
        db.add(user)
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
    admin_user = models.User(
        email="admin@test.com",
        full_name="Admin Test",
        password=utils.get_password_hash("admin123"),
        role="admin"
    )
    db.add(admin_user)
    db.commit()
    db.close()
    resp = client.post("/api/v1/auth/login", data={
        "username": "admin@test.com",
        "password": "admin123"
    })
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


# ---------------------------------------------------------------------------
# EMPRESAS
# ---------------------------------------------------------------------------

def test_crear_empresa_basica(client):
    """Crear empresa con campos mínimos obligatorios."""
    resp = client.post("/api/v1/empresas/", json={
        "nombre": "Empresa A", "cif": "A12345678"
    })
    assert resp.status_code == 201
    assert resp.json()["nombre"] == "Empresa A"
    assert resp.json()["cif"] == "A12345678"


def test_crear_empresa_campos_completos(client):
    """Crear empresa con todos los campos nuevos (dirección, web, contacto interno)."""
    resp = client.post("/api/v1/empresas/", json={
        "nombre": "Tech Solutions S.L.",
        "cif": "B12345678",
        "plazas_totales": 3,
        "direccion": "Calle Ejemplo 12, Madrid",
        "web": "https://techsolutions.es",
        "email": "info@techsolutions.es",
        "telefono": "910111222",
        "contacto_nombre": "Ana Martínez",
        "contacto_email": "ana@techsolutions.es",
        "contacto_telefono": "600111333",
        "contacto_dni": "12345678A"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["direccion"] == "Calle Ejemplo 12, Madrid"
    assert data["web"] == "https://techsolutions.es"
    assert data["contacto_nombre"] == "Ana Martínez"
    assert data["contacto_dni"] == "12345678A"


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


def test_editar_empresa_campos_nuevos(client):
    """Actualizar campos de contacto interno en una empresa existente."""
    emp_id = client.post("/api/v1/empresas/", json={
        "nombre": "Original", "cif": "C1"
    }).json()["id"]
    resp = client.put(f"/api/v1/empresas/{emp_id}", json={
        "contacto_nombre": "Carlos López",
        "contacto_dni": "98765432B",
        "direccion": "Avda. Principal 5"
    })
    assert resp.status_code == 200
    assert resp.json()["contacto_nombre"] == "Carlos López"
    assert resp.json()["contacto_dni"] == "98765432B"


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


# ---------------------------------------------------------------------------
# ALUMNOS
# ---------------------------------------------------------------------------

def test_crear_alumno_basico(client):
    """Crear alumno con campos mínimos."""
    resp = client.post("/api/v1/alumnos/", json={
        "nombre": "Marcos", "apellido": "García", "email": "marcos@test.com"
    })
    assert resp.status_code == 201
    assert resp.json()["email"] == "marcos@test.com"


def test_crear_alumno_con_dni(client):
    """Crear alumno incluyendo el nuevo campo DNI."""
    resp = client.post("/api/v1/alumnos/", json={
        "nombre": "Laura",
        "apellido": "Pérez",
        "email": "laura@test.com",
        "dni": "12345678A",
        "telefono": "600111222"
    })
    assert resp.status_code == 201
    assert resp.json()["dni"] == "12345678A"
    assert resp.json()["telefono"] == "600111222"


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


def test_editar_alumno_dni(client):
    """Actualizar el DNI de un alumno existente."""
    alu_id = client.post("/api/v1/alumnos/", json={
        "nombre": "Sin DNI", "apellido": "Test", "email": "sin@dni.com"
    }).json()["id"]
    resp = client.put(f"/api/v1/alumnos/{alu_id}", json={"dni": "99887766C"})
    assert resp.status_code == 200
    assert resp.json()["dni"] == "99887766C"


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


# ---------------------------------------------------------------------------
# IMPORTACIÓN CSV
# ---------------------------------------------------------------------------

def test_importar_alumnos_csv_basico(client):
    """CSV mínimo con nombre y email."""
    csv_content = "nombre,apellido,email\nJuan,García,juan@csv.com\nLucía,Pérez,lucia@csv.com\n"
    resp = client.post(
        "/api/v1/alumnos/importar-csv",
        files={"file": ("alumnos.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    )
    assert resp.status_code == 201
    assert resp.json()["new_students"] == 2
    assert resp.json()["skipped"] == 0


def test_importar_alumnos_csv_con_dni(client):
    """CSV con todos los campos nuevos (dni, telefono)."""
    csv_content = (
        "nombre,apellido,email,dni,telefono\n"
        "Ana,Sánchez,ana@csv.com,12345678A,600111222\n"
        "Luis,Gómez,luis@csv.com,87654321B,600333444\n"
    )
    resp = client.post(
        "/api/v1/alumnos/importar-csv",
        files={"file": ("alumnos.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    )
    assert resp.status_code == 201
    assert resp.json()["new_students"] == 2
    # Verificar que el DNI se guardó
    alumnos = client.get("/api/v1/alumnos/").json()
    dnis = [a["dni"] for a in alumnos]
    assert "12345678A" in dnis


def test_importar_alumnos_csv_duplicado_saltado(client):
    """Un email duplicado debe contarse en skipped."""
    client.post("/api/v1/alumnos/", json={"nombre": "X", "apellido": "Y", "email": "dup@csv.com"})
    csv_content = "nombre,apellido,email\nX,Y,dup@csv.com\nNuevo,Z,nuevo@csv.com\n"
    resp = client.post(
        "/api/v1/alumnos/importar-csv",
        files={"file": ("alumnos.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    )
    assert resp.status_code == 201
    assert resp.json()["new_students"] == 1
    assert resp.json()["skipped"] == 1


def test_importar_empresas_csv_basico(client):
    """CSV mínimo de empresas con nombre y cif."""
    csv_content = "nombre,cif\nEmpresa CSV 1,X11111111\nEmpresa CSV 2,X22222222\n"
    resp = client.post(
        "/api/v1/empresas/importar-empresas",
        files={"file": ("empresas.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    )
    assert resp.status_code == 201
    assert resp.json()["new_records"] == 2
    assert resp.json()["skipped"] == 0


def test_importar_empresas_csv_campos_completos(client):
    """CSV de empresas con todos los campos nuevos."""
    csv_content = (
        "nombre,cif,plazas,direccion,web,email,telefono,contacto_nombre,contacto_email,contacto_telefono,contacto_dni\n"
        "Alpha Corp,A99999999,3,Calle A 1,https://alpha.com,info@alpha.com,910111222,Ana M,ana@alpha.com,600111333,12345678A\n"
    )
    resp = client.post(
        "/api/v1/empresas/importar-empresas",
        files={"file": ("empresas.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    )
    assert resp.status_code == 201
    assert resp.json()["new_records"] == 1
    # Verificar que los datos de contacto se guardaron
    empresas = client.get("/api/v1/empresas/").json()
    empresa = next(e for e in empresas if e["cif"] == "A99999999")
    assert empresa["contacto_nombre"] == "Ana M"
    assert empresa["contacto_dni"] == "12345678A"
    assert empresa["plazas_totales"] == 3


def test_importar_empresas_csv_duplicado_saltado(client):
    """CIF duplicado en CSV debe ser saltado."""
    client.post("/api/v1/empresas/", json={"nombre": "Dup", "cif": "DUP000001"})
    csv_content = "nombre,cif\nDup,DUP000001\nNueva,NEW000002\n"
    resp = client.post(
        "/api/v1/empresas/importar-empresas",
        files={"file": ("empresas.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    )
    assert resp.status_code == 201
    assert resp.json()["new_records"] == 1
    assert resp.json()["skipped"] == 1


# ---------------------------------------------------------------------------
# CONTACTOS
# ---------------------------------------------------------------------------

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
        "nombre": "E", "cif": "T00000000"
    }).json()["id"]
    client.post("/api/v1/contactos/", json={
        "empresa_id": emp_id, "estado": "Acepta", "plazas_ofrecidas": 3,
        "fecha_inicio": "2026-05-01T00:00:00", "fecha_fin": "2026-06-01T00:00:00", "horas_totales": 400
    })
    emp = client.get(f"/api/v1/empresas/{emp_id}").json()
    assert emp["plazas_totales"] == 3


# ---------------------------------------------------------------------------
# ASIGNACIONES
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# AUTH
# ---------------------------------------------------------------------------

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