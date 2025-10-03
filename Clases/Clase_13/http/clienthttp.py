#!/usr/bin/env python3
import socket
import urllib.parse
import re

class SimpleHTTPClient:
    """
    Cliente HTTP básico que implementa funcionalidad GET
    """
    
    def __init__(self):
        self.default_port = 80
        self.timeout = 30
        
    def parse_url(self, url):
        """
        Parsea una URL en sus componentes
        """
        # Agregar esquema si no está presente
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
            
        parsed = urllib.parse.urlparse(url)
        
        host = parsed.hostname
        port = parsed.port if parsed.port else self.default_port
        path = parsed.path if parsed.path else '/'
        
        # Incluir query string si existe
        if parsed.query:
            path += '?' + parsed.query
            
        return host, port, path
    
    def build_request(self, method, path, host, headers=None):
        """
        Construye una solicitud HTTP válida
        """
        if headers is None:
            headers = {}
            
        # Headers básicos requeridos
        request_headers = {
            'Host': host,
            'User-Agent': 'SimpleHTTPClient/1.0',
            'Connection': 'close',  # Simplifica el manejo de conexiones
        }
        
        # Agregar headers personalizados
        request_headers.update(headers)
        
        # Construir la solicitud
        request_lines = [f"{method} {path} HTTP/1.1"]
        
        for header, value in request_headers.items():
            request_lines.append(f"{header}: {value}")
            
        request_lines.append("")  # Línea en blanco requerida
        
        return "\r\n".join(request_lines) + "\r\n"
    
    def parse_response(self, response_data):
        """
        Parsea una respuesta HTTP en sus componentes
        """
        try:
            # Separar headers del body
            headers_end = response_data.find(b'\r\n\r\n')
            if headers_end == -1:
                raise ValueError("Respuesta HTTP malformada: no se encontró separación headers/body")
            
            headers_data = response_data[:headers_end].decode('utf-8', errors='ignore')
            body_data = response_data[headers_end + 4:]
            
            lines = headers_data.split('\r\n')
            status_line = lines[0]
            
            # Parsear status line
            status_parts = status_line.split(' ', 2)
            if len(status_parts) < 3:
                raise ValueError(f"Status line malformada: {status_line}")
            
            version = status_parts[0]
            status_code = int(status_parts[1])
            reason_phrase = status_parts[2]
            
            # Parsear headers
            headers = {}
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().lower()] = value.strip()
            
            return {
                'version': version,
                'status_code': status_code,
                'reason_phrase': reason_phrase,
                'headers': headers,
                'body': body_data
            }
            
        except Exception as e:
            raise ValueError(f"Error parseando respuesta HTTP: {e}")
    
    def get(self, url, headers=None):
        """
        Realiza una solicitud GET HTTP
        """
        try:
            # Parsear URL
            host, port, path = self.parse_url(url)
            
            # Crear socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            try:
                print(f"Conectando a {host}:{port}...")
                sock.connect((host, port))
                
                # Construir y enviar solicitud
                request = self.build_request('GET', path, host, headers)
                print(f"Enviando solicitud:\n{request}")
                
                sock.send(request.encode('utf-8'))
                
                # Recibir respuesta
                response_data = b''
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response_data += chunk
                
                # Parsear respuesta
                response = self.parse_response(response_data)
                
                print(f"Respuesta recibida: {response['status_code']} {response['reason_phrase']}")
                
                return response
                
            finally:
                sock.close()
                
        except socket.gaierror as e:
            raise ConnectionError(f"Error de resolución DNS: {e}")
        except socket.timeout as e:
            raise ConnectionError(f"Timeout de conexión: {e}")
        except ConnectionRefusedError as e:
            raise ConnectionError(f"Conexión rechazada: {e}")

def demo_http_client():
    """
    Demonstración del cliente HTTP
    """
    client = SimpleHTTPClient()
    
    try:
        # Solicitud básica
        response = client.get('httpbin.org/get')
        
        print(f"\nStatus: {response['status_code']}")
        print(f"Headers: {response['headers']}")
        print(f"Body (primeros 500 chars): {response['body'][:500].decode('utf-8', errors='ignore')}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    demo_http_client()