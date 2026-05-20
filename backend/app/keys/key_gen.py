import secrets

# Ejecuta este programa cada vez que necesites una key nueva 
# guarda las más importantes. Preferiblemente fuera del código fuente.


print(secrets.token_hex(32))