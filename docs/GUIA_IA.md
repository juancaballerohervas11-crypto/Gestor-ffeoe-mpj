# Guía de Uso de IA - Proyecto GestorFFEOE

Esta guía establece los principios y buenas prácticas para el uso de Inteligencia Artificial (IA) en el desarrollo del proyecto GestorFFEOE por parte del equipo de 1º DAW del IES HLanz.

## 🎯 Propósito del uso de IA
La IA se utiliza como una herramienta de **asistencia y aprendizaje**, no como un sustituto del trabajo del desarrollador. El objetivo es aumentar la productividad, mejorar la calidad del código y facilitar la resolución de problemas complejos.

## 🛠️ Áreas de Aplicación

### 1. Desarrollo de Código (Marcos y Pedro)
*   **Generación de Boilerplate:** Uso de IA para crear estructuras básicas de archivos, modelos de datos o componentes repetitivos.
*   **Refactorización:** Pedir sugerencias a la IA para simplificar funciones (especialmente para cumplir la regla de las 20 líneas).
*   **Explicación de Errores:** Utilizar la IA para entender mensajes de error complejos en la terminal o consola.

### 2. Control de Calidad y Tests (Juan)
*   **Generación de Casos de Prueba:** Uso de IA para identificar casos borde (edge cases) que deben ser testeados.
*   **Documentación Automática:** Generación de comentarios y documentación técnica a partir del código fuente.
*   **Auditoría de Seguridad:** Pedir a la IA que revise posibles vulnerabilidades en el código (ej. inyecciones SQL o fallos en JWT).

## ⚠️ Reglas de Oro (Obligatorio)

1.  **Revisión Humana Obligatoria:** Ningún código generado por IA puede ser subido al repositorio sin haber sido revisado, entendido y probado por el responsable del área.
2.  **Prohibición de "Copy-Paste" Ciego:** El desarrollador debe ser capaz de explicar cada línea de código, incluso si ha sido sugerida por una IA.
3.  **Protección de Datos:** Nunca se deben introducir datos reales de alumnos, profesores o claves privadas (secrets) en prompts de IA públicas.
4.  **Validación de Alucinaciones:** La IA puede inventar librerías o funciones que no existen. Es responsabilidad del equipo verificar la veracidad de las sugerencias.

## 📄 Documentación del Uso
En cada Pull Request, se debe indicar brevemente si se ha utilizado asistencia de IA y para qué parte específica del código se ha empleado.

---
*Documento aprobado por el equipo de QA - Mayo 2026*
