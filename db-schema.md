# Esquema de Base de Datos - GestorFFEOE-HLANZ

Este documento describe el esquema de la base de datos relacional para el proyecto GestorFFEOE-HLANZ, tal como ha sido finalizado por el equipo.

## Entidades y Relaciones

### Tabla: `users`

Representa a los usuarios del sistema (administradores, profesores).

| Campo      | Tipo de Dato | Descripción                               |
| :--------- | :----------- | :---------------------------------------- |
| `id`       | INT (PK)     | Identificador único del usuario.          |
| `email`    | VARCHAR      | Correo electrónico del usuario (único).   |
| `password` | VARCHAR      | Contraseña hasheada del usuario.          |
| `full_name`| VARCHAR      | Nombre completo del usuario.              |
| `role`     | VARCHAR      | Rol del usuario (admin, profesor).        |

### Tabla: `alumnos`

Representa a los estudiantes que realizan prácticas FCT/Dual.

| Campo                 | Tipo de Dato | Descripción                                       |
| :-------------------- | :----------- | :------------------------------------------------ |
| `id`                  | INT (PK)     | Identificador único del alumno.                   |
| `nombre`              | VARCHAR      | Nombre del alumno.                                |
| `apellido`            | VARCHAR      | Apellido del alumno.                              |
| `email`               | VARCHAR      | Correo electrónico del alumno (único).            |
| `registrado_por`      | INT (FK)     | ID del usuario que registró al alumno.            |
| `empresa_asignada_id` | INT (FK)     | ID de la empresa a la que está asignado el alumno. |

### Tabla: `empresas`

Representa a las empresas colaboradoras que ofrecen prácticas.

| Campo            | Tipo de Dato | Descripción                                       |
| :--------------- | :----------- | :------------------------------------------------ |
| `id`             | INT (PK)     | Identificador único de la empresa.                |
| `nombre`         | VARCHAR      | Nombre de la empresa.                             |
| `cif`            | VARCHAR      | CIF de la empresa (único).                        |
| `contacto`       | VARCHAR      | Nombre de la persona de contacto en la empresa.   |
| `plazas_totales` | INT          | Número total de plazas de prácticas ofrecidas.    |
| `registrado_por` | INT (FK)     | ID del usuario que registró la empresa.           |

### Tabla: `contactos_empresa`

Representa los convenios o contactos específicos de prácticas con empresas.

| Campo              | Tipo de Dato | Descripción                                       |
| :----------------- | :----------- | :------------------------------------------------ |
| `id`               | INT (PK)     | Identificador único del contacto/convenio.        |
| `profesor_id`      | INT (FK)     | ID del profesor responsable del contacto.         |
| `nombre_profesor`  | VARCHAR      | Nombre del profesor (redundante, se puede obtener de `users`). |
| `empresa_id`       | INT (FK)     | ID de la empresa asociada al contacto.             |
| `estado`           | VARCHAR      | Estado del convenio (ej. Pendiente, Aprobado, Finalizado). |
| `fecha_inicio`     | DATE         | Fecha de inicio de las prácticas.                 |
| `fecha_fin`        | DATE         | Fecha de fin de las prácticas.                    |
| `horas_totales`    | INT          | Horas totales de prácticas.                       |
| `plazas_ofrecidas` | INT          | Número de plazas ofrecidas en este convenio.      |
| `observaciones`    | TEXT         | Notas o comentarios adicionales.                  |
| `fecha_contacto`   | DATE         | Fecha del último contacto con la empresa.         |

## Relaciones Clave

*   `alumnos.registrado_por` -> `users.id` (Un usuario registra a muchos alumnos)
*   `alumnos.empresa_asignada_id` -> `empresas.id` (Una empresa puede tener muchos alumnos asignados)
*   `empresas.registrado_por` -> `users.id` (Un usuario registra a muchas empresas)
*   `contactos_empresa.profesor_id` -> `users.id` (Un profesor gestiona muchos contactos/convenios)
*   `contactos_empresa.empresa_id` -> `empresas.id` (Una empresa puede tener muchos contactos/convenios)
