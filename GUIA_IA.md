# Guía de Uso de IA - Proyecto GestorFFEOE



Para que el código que genere la IA cumpla con las normas de la creción de nuestra página web, usad S siempre este prompt inicial.



##  Prompt 



> "Actúa como un  desarrollador  experto en PHP/Python/React. Voy a pedirte código para el proyecto 'GestorFFEOE'. Reglas estrictas:

> 1. Máximo 20 líneas por función. Si es más larga, divídela.

> 2. Tipado estricto en parámetros y retornos.

> 3. Nombres de variables descriptivos en español.

> 4. Genera los Tests Unitarios incluyendo casos de error .

>5.Comprueba la respuesta que me has dado poniendola a prueba y comprobando tu mismo que el código funciona.


##  Auditoría de Seguridad

Antes de subir nada, pasadle vuestro código a la IA con esto:

* "Busca fallos de seguridad (SQL Injection, fallos JWT) en este código y dime si ves algun fallo."
