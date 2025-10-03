 broker es un componente intermediario que se encarga de conectar dos o más partes que necesitan comunicarse, pero que no lo hacen directamente

 desventaja de docker es su seguridad, su manejo de red es complejo y es más complicado debuggear apps distribuidas

 docker engine -> runtime de contenedores
 dockerd -> daemon gestiona containers, imagenes, redes y vol
 containerd -> runtime de containers de bajo nivel
 runc -> runtime OCI que ejecuta contenedores

 Anatomía de imagen Docker
 ```
 FROM ubuntu:20.04          # Capa base
RUN apt-get update         # Capa 1
RUN apt-get install -y nginx  # Capa 2
COPY . /app               # Capa 3
CMD ["nginx", "-g", "daemon off;"]  # Metadata
```

Comandos:
```
# Listar imágenes locales
docker images
docker image ls
# Descargar imagen sin ejecutar
docker pull ubuntu:20.04
# Eliminar imágenes
docker rmi image_name
docker image rm image_name
# Información detallada de imagen
docker inspect ubuntu:20.04
# Historial de capas
docker history ubuntu:20.04
# Buscar imágenes en Docker Hub
docker search nginx
```

Docker Hub (registry público), registries privados (Harbor, AWS ECR y Google y Amazon CR)

```
# Login en registry
docker login

# Tag para registry específico
docker tag local-image:latest myregistry.com/myimage:v1.0

# Push a registry
docker push myregistry.com/myimage:v1.0

# Pull desde registry específico
docker pull myregistry.com/myimage:v1.0
```

ESTRUCTURA BÁSICA DE DOCKERFILE
```
# Comentario
FROM base_image:tag
LABEL maintainer="engineer@company.com"
LABEL version="1.0"

# Variables de entorno
ENV NODE_ENV=production
ENV PORT=3000

# Directorio de trabajo
WORKDIR /app

# Instalación de dependencias del sistema
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copia de archivos
COPY package*.json ./
RUN npm install --only=production

COPY . .

# Exposición de puerto
EXPOSE 3000

# Usuario no privilegiado
USER node

# Comando por defecto
CMD ["npm", "start"]
```

FROM -> imagen base
RUN -> self-explanatory
EXPOSE -> "Documenta" puertos expuestos

Practicas para Dockerfiles

Optimización capas:
```
# ❌ Múltiples capas RUN
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get clean

# ✅ Single RUN con limpieza
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

aprovechamiento capas
```
# ✅ Copiar dependencias primero
COPY package*.json ./
RUN npm install

# Después copiar código fuente
COPY . .
```

imagenes mínimas
```
# Usar imágenes base pequeñas
FROM node:16-alpine

# O multi-stage builds
FROM node:16 AS builder
COPY . .
RUN npm run build

FROM node:16-alpine
COPY --from=builder /app/dist /app
```

ciclo de vida consta de creado -> corriendo -> pausado -> (restarted) -> detenido -> borrado (exited) -> dead (no pueo detenerse correctamente)


comandos fundamentales gestión básica
```
# Ejecutar contenedor
docker run [opciones] imagen [comando]

# Ejemplos específicos
docker run -d --name webserver -p 80:80 nginx
docker run -it ubuntu:20.04 /bin/bash
docker run --rm alpine echo "Hello World"

# Listar contenedores
docker ps                    # Solo ejecutándose
docker ps -a                # Todos los contenedores
docker ps -f status=running  # Filtrar por estado

# Controlar contenedores
docker start container_name
docker stop container_name
docker restart container_name
docker pause container_name
docker unpause container_name

# Eliminar contenedores
docker rm container_name
docker rm -f container_name  # Forzar eliminación
docker container prune      # Eliminar contenedores detenidos
```

Opciones importantes de docker run

    -d, --detach: Ejecutar en background
    -it: Interactivo con TTY
    --name: Nombre del contenedor
    -p, --publish: Mapeo de puertos
    -v, --volume: Montaje de volúmenes
    --env, -e: Variables de entorno
    --rm: Eliminar automáticamente al salir
    --restart: Política de reinicio

Env en docker

```
# Database configuration
POSTGRES_DB=myapp
POSTGRES_USER=appuser
POSTGRES_PASSWORD=secret123

# Application configuration
NODE_ENV=production
API_PORT=3000
JWT_SECRET=your-super-secret-jwt-key

# Build arguments
BUILD_VERSION=1.2.3
```

Docker compose

local vs producción
local
```
version: '3.8'
services:
  app:
    environment:
      - NODE_ENV=development
      - DEBUG=true
    volumes:
      - .:/app
    ports:
      - "3000:3000"
```

producción
```
version: '3.8'
services:
  app:
    image: myregistry.com/myapp:${VERSION}
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512M
```

Escaneo vulnerabilidades
Trivy
```
# Escanear imagen
trivy image nginx:latest

# Escanear vulnerabilidades críticas y altas
trivy image --severity HIGH,CRITICAL myapp:latest

# Generar reporte JSON
trivy image --format json --output result.json myapp:latest

# Escanear filesystem
trivy fs ./project-directory
```

Secrets mgmt

PÉSIMO
```
# NO hacer esto
ENV API_KEY=secret123
RUN echo "password=secret" > /app/config
```

Swarm (buena práctica)
```
version: '3.8'

services:
  app:
    image: myapp:latest
    secrets:
      - db_password
      - api_key
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    external: true
```