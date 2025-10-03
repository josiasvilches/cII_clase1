FROM python:3.9-slim

WORKDIR /app
COPY containerized_app.py .

# Exponer puerto (documentación, no funcional)
EXPOSE 8080

# Variables de entorno por defecto
ENV BIND_HOST=0.0.0.0
ENV BIND_PORT=8080
ENV APP_NAME=containerized-app

# Crear usuario no-root por seguridad
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser
USER appuser

CMD ["python", "networking.py"]