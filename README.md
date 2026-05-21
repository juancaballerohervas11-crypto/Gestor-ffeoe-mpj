#  GestorFFEOE - "Bienvenidos a Segundo"



Bienvenido al repositorio oficial del proyecto **GestorFFEOE**, una solución  para la gestión de asignaciones de alumnos a empresas en el instituto hlanz para el periodo de prácticas (FCT/Dual).





En este repositorio vamos a ver el flujo de trabajo de un Gestor web para la asignación de prácticas FCT/Dual del instituto Hlanz. Permite gestionar ciclos, alumnos y empresas mediante roles de Admin, Profesor y Alumno. Desarrollado con arquitectura API-First (FastAPI + Vanilla JS), autenticación JWT e importación masiva por CSV.





##  Equipo y Roles

*   **Marcos**: Especialista en Backend (API, Base de Datos, Lógica de Negocio).

*   **Pedro**: Especialista en Frontend (Interfaz de Usuario, Dashboard, UX).

*   **Juan**: Especialista en QA, IA y Documentación (Calidad, Seguridad, Tests).







##  Stack Tecnológico

*   **Backend**:  Python (FastAPI) + SQLAlchemy ORM.

*   **Frontend**: Vanilla JavaScript (ES Modules, sin frameworks).

*   **Base de Datos**: Relacional (MySQL).

*   **Autenticación**: JSON Web Tokens (JWT).

*   **Documentación**: Swagger / OpenAPI 3.0.



##  Estructura del Proyecto

*   [`/backend`](./backend): Código fuente del servidor y API.

*   [`/frontend`](./frontend): Código fuente de la aplicación web.

*   [`/docs`](./docs): Documentación técnica, diseño de BD y guías de estilo.

*   [`/tests`](./tests): Pruebas unitarias y de integración.





##  Cómo Contribuir
Para garantizar un código limpio y mantenible, el equipo sigue estas reglas estrictas:
1.  **Regla de las 20 líneas**: Las funciones del backend no deben exceder las 20 líneas de código (Clean Code).
2.  **Tipado Estricto**: Uso de Type Hints en el backend (Python). El frontend usa Vanilla JS estándar.
3.  **Unit Testing**: Validación obligatoria de cada funcionalidad mediante tests unitarios antes de la integración.
