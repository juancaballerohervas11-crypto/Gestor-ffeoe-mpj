# Estándares de Código y Nomenclatura

Para que el Alumno A (Backend) y el Alumno B (Frontend) se entiendan sin hablar, seguiremos estas reglas:

## 1. Idioma
*   **Código**: Inglés para nombres de variables, funciones y clases (ej: `getUser`, `studentList`). Es el estándar profesional.
*   **Comentarios**: Español, para que nos entendamos rápido entre nosotros.
*   **Base de Datos**: Español (como ya diseñamos las tablas).

## 2. Formato de Escritura (Naming)
*   **Variables y Funciones**: `camelCase` (ej: `getStudentById`, `isLoggedIn`).
*   **Clases**: `PascalCase` (ej: `UserController`, `DatabaseConnection`).
*   **Constantes**: `UPPER_SNAKE_CASE` (ej: `MAX_FILE_SIZE`).

## 3. API (Rutas)
*   Todas las rutas deben ser en minúsculas.
*   Prefijo obligatorio: `/api/v1/`


## 4. Git (Mensajes de Commit)
Recordatorio de los prefijos:
*   `func:` para nuevas cosas.
*   `corr:` para arreglar fallos.
*   `docs:` para documentación.
*   `tarea:` para mantenimiento.
