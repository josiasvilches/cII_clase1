#!/usr/bin/env python3
import socket
import os
import mimetypes
import urllib.parse
from datetime import datetime

class SimpleHTTPServer:
    """
    Servidor HTTP básico que sirve archivos estáticos
    """
    
    def __init__(self, host='', port=8080, document_root='.'):
        self.host = host
        self.port = port
        self.document_root = os.path.abspath(document_root)
        
    def get_mime_type(self, filepath):
        """
        Determina el tipo MIME de un archivo
        """
        mime_type, _ = mimetypes.guess_type(filepath)
        return mime_type or 'application/octet-stream'
    
    def build_response(self, status_code, headers=None, body=b''):
        """
        Construye una respuesta HTTP válida
        """
        status_messages = {
            200: 'OK',
            404: 'Not Found',
            403: 'Forbidden',
            500: 'Internal Server Error'
        }
        
        status_message = status_messages.get(status_code, 'Unknown')
        
        if headers is None:
            headers = {}
        
        # Headers básicos
        response_headers = {
            'Server': 'SimpleHTTPServer/1.0',
            'Date': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'Connection': 'close',
            'Content-Length': str(len(body))
        }
        
        response_headers.update(headers)
        
        # Construir respuesta
        response_lines = [f"HTTP/1.1 {status_code} {status_message}"]
        
        for header, value in response_headers.items():
            response_lines.append(f"{header}: {value}")
        
        response_lines.append("")  # Línea en blanco
        
        response_text = "\r\n".join(response_lines) + "\r\n"
        return response_text.encode('utf-8') + body
    
    def parse_request(self, request_data):
        """
        Parsea una solicitud HTTP
        """
        try:
            request_text = request_data.decode('utf-8')
            lines = request_text.split('\r\n')
            
            # Parsear request line
            request_line = lines[0]
            method, path, version = request_line.split(' ')
            
            # Parsear headers
            headers = {}
            for line in lines[1:]:
                if line == '':  # Fin de headers
                    break
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers[key.strip().lower()] = value.strip()
            
            return {
                'method': method,
                'path': path,
                'version': version,
                'headers': headers
            }
            
        except Exception as e:
            raise ValueError(f"Error parseando solicitud: {e}")
    
    def handle_get(self, path):
        """
        Maneja solicitudes GET
        """
        # Decodificar URL
        path = urllib.parse.unquote(path)
        
        # Remover query string
        if '?' in path:
            path = path.split('?')[0]
        
        # Seguridad básica: prevenir directory traversal
        if '..' in path:
            return self.build_response(403)
        
        # Construir ruta completa
        if path == '/':
            path = '/index.html'
        
        filepath = os.path.join(self.document_root, path.lstrip('/'))
        
        try:
            # Verificar si el archivo existe
            if not os.path.exists(filepath):
                # Generar página 404 simple
                body = b'<html><body><h1>404 Not Found</h1></body></html>'
                headers = {'Content-Type': 'text/html'}
                return self.build_response(404, headers, body)
            
            # Verificar si es un archivo
            if not os.path.isfile(filepath):
                return self.build_response(403)
            
            # Leer archivo
            with open(filepath, 'rb') as f:
                body = f.read()
            
            # Determinar Content-Type
            content_type = self.get_mime_type(filepath)
            headers = {'Content-Type': content_type}
            
            return self.build_response(200, headers, body)
            
        except PermissionError:
            return self.build_response(403)
        except Exception as e:
            print(f"Error sirviendo archivo {filepath}: {e}")
            return self.build_response(500)
    
    def handle_client(self, client_socket, client_address):
        """
        Maneja una conexión cliente individual
        """
        try:
            # Recibir solicitud
            request_data = b''
            while b'\r\n\r\n' not in request_data:
                chunk = client_socket.recv(1024)
                if not chunk:
                    break
                request_data += chunk
            
            if not request_data:
                return
            
            print(f"Solicitud desde {client_address}:")
            print(request_data.decode('utf-8', errors='ignore')[:200] + "...")
            
            # Parsear solicitud
            request = self.parse_request(request_data)
            
            # Manejar según método
            if request['method'] == 'GET':
                response = self.handle_get(request['path'])
            else:
                # Método no soportado
                response = self.build_response(405)
            
            # Enviar respuesta
            client_socket.send(response)
            
        except Exception as e:
            print(f"Error manejando cliente {client_address}: {e}")
            try:
                error_response = self.build_response(500)
                client_socket.send(error_response)
            except:
                pass
        finally:
            client_socket.close()
    
    def serve_forever(self):
        """
        Servidor principal
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            
            print(f"Servidor HTTP corriendo en http://{self.host or 'localhost'}:{self.port}/")
            print(f"Sirviendo archivos desde: {self.document_root}")
            
            while True:
                client_socket, client_address = server_socket.accept()
                print(f"Nueva conexión desde {client_address}")
                
                # En una implementación real, esto debería ser manejado
                # en un thread separado para manejar múltiples clientes
                self.handle_client(client_socket, client_address)
                
        except KeyboardInterrupt:
            print("\nServidor detenido por usuario")
        finally:
            server_socket.close()

if __name__ == "__main__":
    import sys
    
    port = 8080
    document_root = '.'
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        document_root = sys.argv[2]
    
    server = SimpleHTTPServer(port=port, document_root=document_root)
    server.serve_forever()