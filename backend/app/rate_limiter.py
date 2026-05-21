import time
import json
from collections import defaultdict, deque
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


# LIMITES POR DEFECTO

DEFAULT_MAX_REQUESTS: int   = 60   # peticiones por defecto en la ventana
DEFAULT_WINDOW_SECONDS: int = 60   # tamaño de la ventana por defecto (segundos)





# Rutas en las que no actua el rate limiter

EXEMPT_PATHS: set[str] = {
    "/",
    "/docs",
    "/openapi.json",
}




# Límites específicos por ruta

ROUTE_LIMITS: dict[tuple[str, str], tuple[int, int]] = {
    ("POST", "/api/v1/auth/login"):           (5,   60),   # anti fuerza bruta
    ("POST", "/api/v1/usuarios/"):            (10,  60),   # anti registro masivo
    ("POST", "/api/v1/alumnos/importar-csv"): (100, 60),   # carga de CSV
}


# Almacén en memoria

_request_log: dict[tuple[str, str, str], deque] = defaultdict(deque)


# Middleware 

class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Middleware de ventana deslizante con límites por ruta.

    Para cada petición entrante:
        + Comprueba si la ruta está exenta.
        + Determina el límite a poner.
        + Limpia la cola de timestamps caducados.
        + Si se supera el límite, 429. Si no, añade timestamp y continúa.
    """

    async def dispatch(self, request: Request, call_next):

        path   = request.url.path
        method = request.method

        # Rutas exentas
        if path in EXEMPT_PATHS:
            return await call_next(request)

        # Determinar límite aplicable
        limit_config = (
            ROUTE_LIMITS.get((method, path))
            or ROUTE_LIMITS.get(("*", path))
        )
        if limit_config:
            max_requests, window_seconds = limit_config
        else:
            max_requests   = DEFAULT_MAX_REQUESTS
            window_seconds = DEFAULT_WINDOW_SECONDS

        # Identifica cliente por IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for
            else (request.client.host if request.client else "unknown")
        )

        now          = time.time()
        window_start = now - window_seconds
        log_key      = (client_ip, method, path)
        log          = _request_log[log_key]

        # Descarta timestamps fuera de la ventana
        while log and log[0] < window_start:
            log.popleft()

        # Comprueba límite
        if len(log) >= max_requests:
            retry_after = int(log[0] - window_start) + 1
            body = json.dumps({
                "detail": (
                    f"Demasiadas peticiones a '{path}'. "
                    f"Límite: {max_requests} peticiones cada {window_seconds} segundos. "
                    f"Inténtalo de nuevo en {retry_after} segundo(s)."
                )
            })
            return Response(
                content=body,
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After":           str(retry_after),
                    "X-RateLimit-Limit":     str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset":     str(int(log[0] + window_seconds)),
                },
            )

        # Registra la petición y continua
        log.append(now)
        response = await call_next(request)

        remaining = max_requests - len(log)
        response.headers["X-RateLimit-Limit"]     = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"]     = str(int(now + window_seconds))
        return response

