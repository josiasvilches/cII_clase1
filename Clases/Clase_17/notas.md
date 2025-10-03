HTTP -> protocolo de transferencia de hipertexto

Solicitud HTTP
```
GET /index.html HTTP/1.1
Host: www.ejemplo.com
User-Agent: Mozilla/5.0
Accept: text/html,application/xhtml+xml
Connection: keep-alive
```

Respuesta HTTP
```
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 1234
Server: Python/HTTPServer

<html>
<body>Contenido de la página</body>
</html>
```

Métodos

GET -> solicita un recurso específico, idempotente (HEAD es parecido, sólo pide headers, sin cuerpo, verifica metadatos sin descargar contenido completo)
```
GET /usuarios/123 HTTP/1.1
```

POST -> envía datos al servidor para ser procesados, usado para crear recursos o datos de formularios, NO idempotente

```
POST /usuarios HTTP/1.1
Content-Type: application/json
{"nombre": "Juan", "email": "juan@ejemplo.com"}
```

PUT -> reemplaza completamente recurso existente, idempotente (PATCH realiza modificaciones parciales)
```
PUT /usuarios/123 HTTP/1.1
Content-Type: application/json

{"nombre": "Juan Pérez", "email": "juan.perez@ejemplo.com"}
```

DELETE -> elimina recurso específico, idempotente
```
DELETE /usuarios/123 HTTP/1.1
```

idempotente -> significa que realizar múltiples solicitudes idénticas produce el mismo resultado que una sola solicitud

OPTIONS -> solicita info sobre opciones de comunicación para el recurso (métodos permitidos, headers soportados)
CONNECT -> establece tunel a server, usado con proxies para conexiones https
TRACE -> realiza prueba bucle de retorno, usado para diagnósticos

Códigos

2xx -> respuestas correctas
- 200 
- 201 creado
- 204 solicitud correcta, sin contenido

3xx -> redirecciones
- 301 -> movido permanentemente a otra url
- 302 -> redirección temporal
- 304 -> recurso no fue modificado desde última solicitud

4xx -> errores cliente
- 400 -> solicitud mal armada
- 401 -> autorización requerida
- 403 -> acceso denegado
- 404 no encontrado
- 405 -> método HTTP no permitido para recurso

5xx -> errores server
- 500 -> error interno server
- 502 -> error gateway
- 503 -> servicio NO disponible temporalmente

Herramientas testing
curl
```
# GET request
curl http://localhost:8080/

# POST con datos
curl -X POST -d "datos=test" http://localhost:8080/api

# Ver headers de respuesta
curl -i http://localhost:8080/

# POST con JSON
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"nombre": "test"}' \
     http://localhost:8080/api
```