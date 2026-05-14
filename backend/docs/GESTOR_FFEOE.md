# Manual de uso Gestor FFEOE
**Creado por:** Marcos Aragón Romero

>El backend del proyecto, así como toda la documentación de dicho backend ha sido desarrollado por Marcos Aragón Romero con ayuda de IA, para un trabajo conjunto con otros alumnos del IES Politécnico Hermenegildo Lanz.  
***IMPORTANTE:** todo el código está revisado y comprendo por completo el funcionamiento del mismo. La IA ha sido simplemente un apoyo*


***Nota:** Este archivo resume el contenido del manual de la base de datos. En caso de querer ver el diagrama de la base de datos abra el archivo `.pdf`*


---



## Características del Sistema
* **Lenguaje de programación usado:** Python 3.13.7  
* **Framework:** FastAPI
* **Motor:** MySQL 8.0  (vía Docker)  
* **ORM:** SQLAlchemy  
* **Driver:** PyMySQL


---


#   ESTRUCTURA DEL BACKEND

```
PRACTICAS/
│
├── app/
│   ├── routers/
│   │   ├── usuarios.py
│   │   ├── alumnos.py
│   │   ├── empresas.py
│   │   ├── contactos.py
│   │   └── profesores.py
│   │   
│   ├── __init__.py
│   ├── utils.py
│   ├── auth_tokens.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   └── .env
│
├── docs/
│   ├── GESTOR_FFEOE.md
│   ├── Manual_instalacion_api_gestor_ffeoe
│   ├── Manual_db_gestor_ffeoe.pdf
│   ├── empresas_TEMPLATE.csv
│   └── alumnos_TEMPLATE.csv
│
├── docker-compose.yml
└── requirements.txt
```


---


#   INSTALACIÓN Y USO

## Manual de Uso de la Base de Datos

Este apartado explica como inicializar el contenedor de la base de dato y como configurarlo.

### Gestión con Docker
| Acción | Comando |
| :--- | :--- |
| **Levantar todo** | `docker-compose up -d` |
| **Ver procesos activos** | `docker ps` |
| **Detener contenedor** | `docker-compose stop` |
| **Apagar todo** | `docker-compose down` |
| **Eliminar contenedor y datos** | `docker-compose down -v` |
| **Reconstruir contenedor** | `docker-compose up --build` |

---

## Manual de Instalación de la API

Este apartado explica como iniciar la API, incluyendo la instalación de paquetes y de venv si es la primera vez que se inicia

**Requisito previo:** Iniciar Docker y la base de datos antes de configurar la API.


### SI ES LA PRIMERA VEZ QUE INICIAS LA API
### Configuración del Entorno
1. `cd backend`
1. `cd app`
1. `python -m venv venv`
1. `pip install -r requirements.txt`

### Inicialización de la API
1. Activar entorno virtual: `.\venv\Scripts\activate` (dentro de carpeta `app`).
1. Volver a raíz (Backend): `cd ..`
1. Ejecutar: `\app\venv\Scripts\python.exe -m uvicorn app.main:app --reload`
### Si quieres acceder desde mas equipos de una red
4. Si has ejecutado el comando de justo antes pulsa `crtl+C`
5. Ejecutar: `.\app\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Acceso y Swagger
* **Swagger UI:** [http://127.0.0.1:8000/docs]   

### En caso de acceder mediante otro equipo que este en la misma red:
1. Ejecutar: `ipconfig`.
1. Buscar tu dirección IPv4
1. Accedes a la url usando tu dirección IPv4:
* **Swagger UI:** [http://*tu_durección_ip*:8000/docs]   



   
   
* **Autorización:**   
  - Pulsar botón **Authorize**.
  - Identificarse en **OAuth2PasswordBearer** con email (`username`) y contraseña.
  - Confirmar pulsando el botón **Authorize** del formulario.
  
  
*Nota: la interfaz de usuario OpenAPI funciona como documentación de la estructura y de la programación del proyecto. Al ser visibles y funcionales todas las clases y endpoints programados. También es posible ver los esquemas de creación y los modelos de tablas de la base de datos*

---

#   IMPORTACIÓN MEDIANTE CSV

>Para realizar importaciones correctamente, los archivos `.csv` deben seguir **exactamente** los formatos indicados a continuación.
**Los archivos `.csv` de la carpeta son plantillas de ejemplo para la importación de alumnos y empresas**  
**Aviso:** Los emails de las plantillas son únicamente ejemplos genéricos, no tienen nada con este proyecto


---


## Importación de ALUMNOS

### FORMATO:

nombre,apellido,email   
Juan,García,juan.garcia@email.com   
Lucía,Pérez,lucia.perez@email.com  


---


## Importación de EMPRESAS


### FORMATO:

nombre,cif,contacto   
Empresa Alpha,A12345678,Pepito Perez   
Empresa Beta,B98765432,Maria Garcia   


### En caso de que la empresa oferte plazas:

*Se añaden las plazas al final*

nombre,cif,contacto,**`plazas`**  
Empresa Alpha,A12345678,Pepito Perez,**`3`**  
Empresa Beta,B98765432,Maria Garcia,**`0`**


---


#   ARCHIVOS DEL PROYECTO

## `main.py`
Punto de entrada de la aplicación. Se encarga de inicializar la app FastAPI, registrar todos los routers, configurar el middleware CORS y crear las tablas en la base de datos al arrancar. También expone el endpoint raíz `GET /` y el endpoint de estadísticas `GET /stats/resumen`.

## `database.py`
Configuración de la conexión a MySQL con SQLAlchemy. Define el motor de conexión con la URL leída desde el `.env`, la fábrica de sesiones `SessionLocal`, la clase base `Base` de la que heredan todos los modelos, y la función `get_db()` que provee una sesión de base de datos a cada petición y la cierra al terminar.

## `models.py`
Define las tablas de la base de datos como clases Python mediante el ORM de SQLAlchemy.

| Modelo | Tabla | Descripción |
| :--- | :--- | :--- |
| `User` | `users` | Usuarios del sistema (admins y profesores) |
| `Empresa` | `empresas` | Empresas con plazas de prácticas |
| `Alumno` | `alumnos` | Alumnos pendientes de asignación |
| `ContactoEmpresa` | `contactos_empresa` | Registro de contactos entre profesores y empresas |

## `schemas.py`
Define los esquemas de validación de datos con Pydantic. Controla qué datos se aceptan en las peticiones entrantes y qué datos se devuelven en las respuestas.

| Esquema | Uso |
| :--- | :--- |
| `UserCreate` / `UserOut` / `UserUpdate` | Crear, mostrar y editar usuarios |
| `UserLogin` / `Token` / `TokenData` | Autenticación y tokens JWT |
| `EmpresaCreate` / `EmpresaOut` / `EmpresaUpdate` | CRUD de empresas |
| `AlumnoCreate` / `AlumnoOut` / `AlumnoUpdate` | CRUD de alumnos |
| `ContactoCreate` / `ContactoOut` / `ContactoBase` / `ContactoUpdate` | CRUD de contactos |
| `AsignacionAlumno` | Asignación de alumnos a empresas |

## `auth_tokens.py`
Gestión de autenticación JWT. Contiene:
* `create_access_token()` — genera un token JWT firmado con el `SECRET_KEY` y una expiración de 60 minutos.
* `verify_access_token()` — decodifica y valida un token, extrayendo el email del usuario.
* `get_current_user()` — dependencia de FastAPI que valida el token de cada petición y devuelve el usuario activo.
* `RoleChecker` — clase reutilizable que protege endpoints según el rol del usuario.

## `utils.py`
Funciones auxiliares reutilizables en los routers y servicios.

| Función | Descripción |
| :--- | :--- |
| `empresa_existe()` | Busca una empresa por ID |
| `alumno_existe()` | Busca un alumno por ID |
| `contacto_existe()` | Busca un contacto por ID |
| `profesor_existe()` | Busca un usuario por ID |
| `get_password_hash()` | Genera el hash bcrypt de una contraseña |
| `verify_password()` | Compara una contraseña en texto plano con su hash |
| `devolver_plaza_empresa()` | Incrementa en 1 las plazas de una empresa |
| `obtener_empresa_por_cif()` | Busca una empresa por su CIF |
| `obtener_usuario_por_email()` | Busca un usuario por su email |

## `services.py`
Capa de lógica de negocio que separa las operaciones de base de datos de los routers. Contiene funciones para crear, editar y eliminar cada entidad del sistema, incluyendo toda la lógica de gestión de plazas al registrar o editar contactos.

## Routers

Cada archivo en `routers/` agrupa los endpoints de una entidad y se registra en `main.py` mediante `app.include_router()`.

| Archivo | Prefijo | Entidad gestionada |
| :--- | :--- | :--- |
| `usuarios.py` | `/auth` | Autenticación y gestión de usuarios |
| `alumnos.py` | `/alumnos` | Gestión de alumnos |
| `empresas.py` | `/empresas` | Gestión de empresas |
| `contactos.py` | sin prefijo | Contactos y asignaciones |
| `profesores.py` | `/profesores` | Gestión de profesores |


---


#   ENDPOINTS

## Autenticación — `/auth`

| Método | Ruta | Descripción | Permisos |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/login` | Iniciar sesión y obtener token JWT | Público |
| `POST` | `/auth/registrar` | Registrar nuevo usuario | Admin |
| `GET` | `/auth/me` | Ver datos del usuario autenticado | Autenticado |
| `GET` | `/auth/` | Listar todos los usuarios | Admin |
| `PUT` | `/auth/{user_id}/role` | Cambiar rol de un usuario | Admin |
| `DELETE` | `/auth/{user_id}` | Eliminar usuario | Admin |

### Roles disponibles

| Rol | Permisos |
| :--- | :--- |
| `admin` | Acceso completo a todos los endpoints |
| `profesor` | Puede gestionar alumnos, empresas y contactos |
| `user` | Sin acceso a endpoints protegidos |

---

## Alumnos — `/alumnos`

| Método | Ruta | Descripción | Permisos |
| :--- | :--- | :--- | :--- |
| `GET` | `/alumnos/` | Listar todos los alumnos | Público |
| `POST` | `/alumnos/` | Crear alumno manualmente | Admin, Profesor |
| `POST` | `/alumnos/importar-csv` | Importar alumnos desde archivo CSV | Admin, Profesor |
| `PUT` | `/alumnos/{alumno_id}` | Editar datos de un alumno | Admin, Profesor |
| `DELETE` | `/alumnos/{alumno_id}` | Eliminar alumno | Admin, Profesor |

---

## Empresas — `/empresas`

| Método | Ruta | Descripción | Permisos |
| :--- | :--- | :--- | :--- |
| `GET` | `/empresas/` | Listar todas las empresas | Público |
| `POST` | `/empresas/` | Crear empresa manualmente | Admin, Profesor |
| `POST` | `/empresas/importar-empresas` | Importar empresas desde CSV | Admin, Profesor |
| `PUT` | `/empresas/{empresa_id}` | Editar datos de una empresa | Admin, Profesor |
| `DELETE` | `/empresas/{empresa_id}` | Eliminar empresa | Admin, Profesor |
| `GET` | `/empresas/{empresa_id}/contactos` | Ver historial de contactos de una empresa | Público |

---

## Contactos y Asignaciones

| Método | Ruta | Descripción | Permisos |
| :--- | :--- | :--- | :--- |
| `GET` | `/contactos/` | Listar todos los contactos | Admin, Profesor |
| `GET` | `/contactos/recientes` | Ver los 3 últimos contactos registrados | Admin, Profesor |
| `POST` | `/contactos/` | Registrar nuevo contacto con empresa | Admin, Profesor |
| `PUT` | `/{contacto_id}` | Editar contacto existente | Admin, Profesor |
| `DELETE` | `/{contacto_id}` | Eliminar contacto | Admin, Profesor |
| `POST` | `/asignaciones/{alumno_id}/{empresa_id}` | Asignar alumno a empresa | Admin, Profesor |
| `DELETE` | `/asignaciones/{alumno_id}` | Eliminar asignación de alumno | Admin, Profesor |

### Estados posibles de un contacto

| Estado | Efecto en plazas de la empresa |
| :--- | :--- |
| `Acepta` | Suma `plazas_ofrecidas` a `plazas_totales` |
| `Rechaza` | Sin efecto |
| `Pendiente` | Sin efecto |

---

## Profesores — `/profesores`

| Método | Ruta | Descripción | Permisos |
| :--- | :--- | :--- | :--- |
| `GET` | `/profesores/` | Listar profesores y administradores | Público |
| `POST` | `/profesores/` | Crear nuevo profesor | Admin |
| `PUT` | `/profesores/{profe_id}` | Editar datos de un profesor | Admin, Profesor |
| `DELETE` | `/profesores/{profe_id}` | Eliminar profesor | Admin, Profesor |

---

## General

| Método | Ruta | Descripción | Permisos |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Estado de la API | Público |
| `GET` | `/stats/resumen` | Resumen general de alumnos y plazas | Autenticado |


---


#   LÓGICA DE PLAZAS

Las plazas de cada empresa se gestionan automáticamente según las siguientes reglas:

* Al registrar un contacto con estado `Acepta` → `plazas_totales += plazas_ofrecidas`
* Al editar un contacto de `Acepta` a otro estado → `plazas_totales -= plazas_ofrecidas`
* Al editar un contacto de otro estado a `Acepta` → `plazas_totales += plazas_ofrecidas`
* Al asignar un alumno a una empresa → `plazas_totales -= 1`
* Al eliminar la asignación de un alumno → `plazas_totales += 1`
* Al eliminar un alumno que tenía empresa asignada → `plazas_totales += 1`
* Al eliminar una empresa → todos sus alumnos quedan sin empresa asignada


---
*Documentación de la versión 1.0.0 de la API Gestor FFEOE.*