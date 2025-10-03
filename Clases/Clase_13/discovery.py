#!/usr/bin/env python3
"""
Cliente que demuestra service discovery en entornos containerizados
"""
import socket
import json
import time
import os
import random

class ServiceDiscoveryClient:
    """
    Cliente que puede conectarse a servicios a través de service discovery
    """
    
    def __init__(self):
        # En un entorno real, esto vendría de un service registry
        self.services = {
            'user-service': [
                ('user-service-1', 8080),
                ('user-service-2', 8080)
            ],
            'data-service': [
                ('data-service-1', 8080),
                ('data-service-2', 8080)
            ]
        }
    
    def discover_service(self, service_name):
        """
        Descubre instancias disponibles de un servicio
        """
        if service_name in self.services:
            return self.services[service_name]
        return []
    
    def call_service(self, service_name, path="/", method="GET"):
        """
        Llama a un servicio con load balancing simple
        """
        instances = self.discover_service(service_name)
        
        if not instances:
            raise Exception(f"No se encontraron instancias del servicio {service_name}")
        
        # Load balancing simple (random)
        host, port = random.choice(instances)
        
        try:
            # En Docker, podemos usar nombres de servicio como hostnames
            response = self._make_http_request(host, port, path, method)
            return response
            
        except Exception as e:
            print(f"Error conectando a {host}:{port} - {e}")
            
            # Retry con otra instancia
            remaining_instances = [inst for inst in instances if inst != (host, port)]
            if remaining_instances:
                host, port = random.choice(remaining_instances)
                return self._make_http_request(host, port, path, method)
            
            raise Exception(f"Todos los servicios {service_name} no disponibles")
    
    def _make_http_request(self, host, port, path, method):
        """
        Hace una solicitud HTTP simple
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        try:
            sock.connect((host, port))
            
            request = f"{method} {path} HTTP/1.1\r\n"
            request += f"Host: {host}\r\n"
            request += "Connection: close\r\n"
            request += "\r\n"
            
            sock.send(request.encode('utf-8'))
            
            response = b''
            while True:
                data = sock.recv(1024)
                if not data:
                    break
                response += data
            
            return response.decode('utf-8')
            
        finally:
            sock.close()

def demo_service_discovery():
    """
    Demonstración de service discovery
    """
    client = ServiceDiscoveryClient()
    
    for i in range(5):
        try:
            response = client.call_service('user-service', '/api/users')
            print(f"Respuesta {i+1}:")
            print("="*50)
            
            # Extraer solo el body JSON
            if '\r\n\r\n' in response:
                _, body = response.split('\r\n\r\n', 1)
                try:
                    data = json.loads(body)
                    print(f"Servicio: {data.get('app', 'unknown')}")
                    print(f"Container: {data.get('container_id', 'unknown')}")
                    print(f"Timestamp: {data.get('timestamp', 'unknown')}")
                except json.JSONDecodeError:
                    print("Respuesta no es JSON válido")
            
            print()
            time.sleep(2)
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    demo_service_discovery()