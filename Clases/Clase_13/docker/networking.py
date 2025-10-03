#!/usr/bin/env python3
"""
Ejemplo que demuestra cómo crear aplicaciones de red listas para contenedores
"""
import socket
import os
import signal
import sys
import json
import time
from datetime import datetime

class ContainerizedApp:
    """
    Aplicación diseñada para ejecutarse en contenedores
    """
    
    def __init__(self):
        # Configuración desde variables de entorno (patrón Docker)
        self.host = os.getenv('BIND_HOST', '0.0.0.0')
        self.port = int(os.getenv('BIND_PORT', '8080'))
        self.app_name = os.getenv('APP_NAME', 'containerized-app')
        
        self.server_socket = None
        self.running = False
        
        # Configurar manejo de señales para shutdown graceful
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """
        Maneja señales para shutdown graceful
        """
        print(f"\nRecibida señal {signum}, iniciando shutdown graceful...")
        self.shutdown()
    
    def start(self):
        """
        Inicia la aplicación
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"🚀 {self.app_name} corriendo en {self.host}:{self.port}")
            print(f"📊 PID: {os.getpid()}")
            print(f"🐳 Container ID: {os.getenv('HOSTNAME', 'localhost')}")
            
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    self._handle_request(client_socket, client_address)
                except OSError:
                    # Socket cerrado durante shutdown
                    if self.running:
                        raise
                    
        except Exception as e:
            print(f"❌ Error en servidor: {e}")
        finally:
            self.cleanup()
    
    def _handle_request(self, client_socket, client_address):
        """
        Maneja una solicitud HTTP simple
        """
        try:
            with client_socket:
                # Leer solicitud
                request_data = client_socket.recv(1024).decode('utf-8')
                
                if not request_data:
                    return
                
                # Extraer método y path básicos
                lines = request_data.split('\r\n')
                if lines:
                    method, path, _ = lines[0].split(' ')
                    
                    # Generar respuesta JSON
                    response_data = {
                        'app': self.app_name,
                        'timestamp': datetime.now().isoformat(),
                        'client_ip': client_address[0],
                        'client_port': client_address[1],
                        'method': method,
                        'path': path,
                        'container_id': os.getenv('HOSTNAME', 'localhost'),
                        'environment': {
                            'BIND_HOST': self.host,
                            'BIND_PORT': str(self.port),
                            'APP_NAME': self.app_name
                        }
                    }
                    
                    json_response = json.dumps(response_data, indent=2)
                    
                    # Construir respuesta HTTP
                    http_response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: application/json\r\n"
                        f"Content-Length: {len(json_response)}\r\n"
                        "Connection: close\r\n"
                        "\r\n"
                        f"{json_response}"
                    )
                    
                    client_socket.send(http_response.encode('utf-8'))
                    
                    print(f"📡 Solicitud de {client_address[0]}:{client_address[1]} - {method} {path}")
                    
        except Exception as e:
            print(f"❌ Error manejando solicitud: {e}")
    
    def shutdown(self):
        """
        Shutdown graceful de la aplicación
        """
        print("🛑 Iniciando shutdown graceful...")
        self.running = False
        
        if self.server_socket:
            self.server_socket.close()
    
    def cleanup(self):
        """
        Limpieza final
        """
        print("🧹 Cleanup completado")

# Dockerfile correspondiente (como comentario para referencia)
"""
# Dockerfile
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

CMD ["python", "containerized_app.py"]
"""

# docker-compose.yml correspondiente (como comentario)
"""
version: '3.8'

services:
  app1:
    build: .
    ports:
      - "8080:8080"
    environment:
      - APP_NAME=app-instance-1
      - BIND_PORT=8080
    networks:
      - app-network

  app2:
    build: .
    ports:
      - "8081:8080"
    environment:
      - APP_NAME=app-instance-2
      - BIND_PORT=8080
    networks:
      - app-network

  load_balancer:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app1
      - app2
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
"""

if __name__ == "__main__":
    app = ContainerizedApp()
    app.start()