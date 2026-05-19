# Guía de Contribución - Proyecto GestorFFEOE

¡Hola equipo! Como responsables del éxito de este proyecto, debemos seguir estas normas estrictas para cumplir con los requisitos del profesor y asegurar la calidad del código.

## 1. Reglas de Oro del Código (Clean Code)
*   **Límite de 20 líneas**: Ninguna función o método puede superar las 20 líneas de código. Si es más larga, divídela en funciones más pequeñas.
*   **Nombres Semánticos**: Prohibido usar nombres como `a` o `var1`. Usa nombres que expliquen qué hace la variable (ej: `listaAlumnos`, `usuarioLogueado`).
*   **Tipado Obligatorio**: Se deben usar Type Hints en los parámetros y retornos de funciones Python del backend.
*   **Arquitectura**: Separación total entre Frontend y Backend. No se permite lógica de negocio en las vistas.

## 2. Flujo de Trabajo en Git
*   **Prohibido Push a Main**: Nadie sube código directamente a `main`.
*   **Ramas por Tarea**: Crea una rama para cada cosa que hagas:
    *   `func/nombre-tarea` para nuevas funciones.
    *   `corr/nombre-tarea` para arreglar fallos.
*   **Pull Requests (PR)**: Al terminar, abre una PR. El Alumno C (o el otro compañero) debe revisarla y aprobarla antes de unirla a `main`.

## 3. Uso de IA
*   Podemos usar IA para generar código y tests, pero es obligatorio **revisar el código generado** para asegurar que cumple con las reglas de seguridad y las 20 líneas por función.

## 4. Documentación
*   Cada nuevo endpoint del Backend debe estar documentado en **Swagger/OpenAPI** antes de dar la tarea por finalizada.
