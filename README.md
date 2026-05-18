#  GestorFFEOE - "Bienvenidos a Segundo"

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

Bienvenido al repositorio oficial del proyecto **GestorFFEOE**, una solución  para la gestión de asignaciones de alumnos a empresas en el instituto hlanz para el periodo de prácticas (FCT/Dual).





En este repositorio vamos a ver el flujo de trabajo de un Gestor web para la asignación de prácticas FCT/Dual del instituto Hlanz. Permite gestionar ciclos, alumnos y empresas mediante roles de Admin, Profesor y Alumno. Desarrollado con arquitectura API-First (PHP/Python y React/Vue), autenticación JWT e importación masiva por CSV.





##  Equipo y Roles

*   **Marcos**: Especialista en Backend (API, Base de Datos, Lógica de Negocio).

*   **Pedro**: Especialista en Frontend (Interfaz de Usuario, Dashboard, UX).

*   **Juan**: Especialista en QA, IA y Documentación (Calidad, Seguridad, Tests).







##  Stack Tecnológico

*   **Backend**:  Python (Django/FastAPI).

*   **Frontend**: JavaScript (React/Vue).

*   **Base de Datos**: Relacional (MySQL).

*   **Autenticación**: JSON Web Tokens (JWT).

*   **Documentación**: Swagger / OpenAPI 3.0.



##  Estructura del Proyecto

*   [`/backend`](./backend): Código fuente del servidor y API.

*   [`/frontend`](./frontend): Código fuente de la aplicación web.

*   [`/docs`](./docs): Documentación técnica, diseño de BD y guías de estilo.

*   [`/tests`](./tests): Pruebas unitarias y de integración.



##  Estado del Proyecto: **Fase 1 - Planificación y Diseño** 🏗️

Actualmente hemos completado:

- [x] Configuración del repositorio y protección de ramas.

- [x] Definición de estándares de calidad ([CONTRIBUTING.md](./CONTRIBUTING.md)).

- [x] Guía de uso de IA para el equipo.

- [x] Diseño inicial de la Base de Datos Relacional.

- [x] Esqueleto de la documentación Swagger.


##  Cómo Contribuir
Para garantizar un código limpio y mantenible, el equipo sigue estas reglas estrictas:
1.  **Regla de las 20 líneas**: Las funciones del backend no deben exceder las 20 líneas de código (Clean Code).
2.  **Tipado Estricto**: Uso obligatorio de TypeScript en el frontend y Type Hints en el backend.
3.  **Unit Testing**: Validación obligatoria de cada funcionalidad mediante tests unitarios antes de la integración.
