import secrets

# Ejecuta este programa cada vez que necesites una key nueva 
# guarda las más importantes. Preferiblemente fuera del código fuente.


print(secrets.token_hex(32))


# Key almacenada para auth_tokens.py
key="3a5878ad1068da64a065f1f68b00a17aa2c4ad33a84effe1c5ad499ef2c7dda5"


# Key usada para la contraseña de la base de datos en el docker-compose.yml
db_key="2b295fed2ac875775c825fbe2ba996842d09ebc3381cf148b81a68a7a0236373"