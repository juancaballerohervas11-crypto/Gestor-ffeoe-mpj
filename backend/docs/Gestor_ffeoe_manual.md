# Manual de uso Gestor FFEOE
**Creado por:** Marcos Aragón Romero

>El backend del proyecto, así como toda la documentación de dicho backend ha sido desarrollado por Marcos Aragón Romero con ayuda de IA, para un trabajo conjunto con otros alumnos del IES Politécnico Hermenegildo Lanz.  
***IMPORTANTE:** todo el código está revisado y comprendo por completo el funcionamiento del mismo. La IA ha sido simplemente un apoyo*


***Nota:** Este archivo resume el contenido de los manuales de la base de datos y de instalación de la API de forma no visual y menos exhaustiva. En caso de necesitar ver algo como el contenido del archivo docker-compose, abra los archivos `.pdf`*


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