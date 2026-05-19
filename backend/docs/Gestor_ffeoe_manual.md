# Manual de uso Gestor FFEOE
**Creado por:** Marcos Aragón Romero y Juan Caballero. 

>El backend del proyectoha sido desarrollado por Marcos Aragón Romero con ayuda de IA, para un trabajo conjunto con otros alumnos del IES Politécnico Hermenegildo Lanz.  
***IMPORTANTE:** todo el código está revisado por Juan caballero Hervás y comprendo por completo el funcionamiento del mismo. La IA ha sido simplemente un apoyo*





---



## Características del Sistema
* **Lenguaje de programación usado:** Python (3.13.7)  
* **Framework:** FastAPI
* **Motor:** MySQL 8.0 gestionado vía Docker  
* **ORM:** SQLAlchemy  
* **Driver:** PyMySQL


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
1. `cd app`
1. `python -m venv venv`
1. `pip install -r requirements.txt`

### Inicialización de la API
1. Activar entorno virtual: `.\venv\Scripts\activate` (dentro de carpeta `app`).
1. Volver a raíz: `cd ..`
1. Ejecutar: `\app\venv\Scripts\python.exe -m uvicorn app.main:app --reload`

### Acceso y Swagger
* **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)   
   
   
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

```
nombre,apellido,email,dni,telefono
Juan,García,juan.garcia@email.com,12345678A,600111222
Lucía,Pérez,lucia.perez@email.com,87654321B,600333444
```

**Columnas obligatorias:** `nombre`, `email`  
**Columnas opcionales:** `apellido`, `dni`, `telefono`

---


## Importación de EMPRESAS


### FORMATO COMPLETO:

```
nombre,cif,plazas,direccion,web,email,telefono,contacto_nombre,contacto_email,contacto_telefono,  contacto_dni
Empresa Alpha,A12345678,3,Calle Ejemplo 12 Madrid,https://alpha.com,info@alpha.com,910111222,Ana Martínez,ana@alpha.com,600111333,12345678A
Empresa Beta,B98765432,0,Avenida Principal 5 Sevilla,https://beta.es,contacto@beta.es,910444555,Pepito Pérez,pepito@beta.es,600444666,98765432B
```

**Columnas obligatorias:** `nombre`, `cif`  
**Columnas opcionales:** `plazas`, `direccion`, `web`, `email`, `telefono`, `contacto_nombre`, `contacto_email`, `contacto_telefono`, `contacto_dni`

### FORMATO MÍNIMO (sin datos adicionales):

```
nombre,cif
Empresa Alpha,A12345678
Empresa Beta,B98765432
```

