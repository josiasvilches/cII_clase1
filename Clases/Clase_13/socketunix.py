#!/usr/bin/env python3
import socket
import os
import threading
import time

class UnixSocketServer:
    """
    Servidor que utiliza sockets Unix para comunicación local
    """
    
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.server_socket = None
        
    def start_server(self):
        """
        Inicia el servidor Unix socket
        """
        # Limpiar socket existente si existe
        try:
            os.unlink(self.socket_path)
        except OSError:
            pass
        
        # Crear socket Unix
        self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
        try:
            # Bind al archivo de socket
            self.server_socket.bind(self.socket_path)
            self.server_socket.listen(5)
            
            print(f"Servidor Unix socket escuchando en {self.socket_path}")
            
            while True:
                # Aceptar conexiones
                client_socket, _ = self.server_socket.accept()
                
                # Manejar cliente en thread separado
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\nServidor detenido por usuario")
        finally:
            self.cleanup()
    
    def handle_client(self, client_socket):
        """
        Maneja un cliente individual
        """
        try:
            with client_socket:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    # Procesar mensaje (echo con timestamp)
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    response = f"[{timestamp}] Echo: {data.decode('utf-8')}"
                    
                    client_socket.send(response.encode('utf-8'))
                    
        except Exception as e:
            print(f"Error manejando cliente: {e}")
    
    def cleanup(self):
        """
        Limpia recursos
        """
        if self.server_socket:
            self.server_socket.close()
        
        try:
            os.unlink(self.socket_path)
        except OSError:
            pass

class UnixSocketClient:
    """
    Cliente para comunicación con servidor Unix socket
    """
    
    def __init__(self, socket_path):
        self.socket_path = socket_path
    
    def send_message(self, message):
        """
        Envía un mensaje al servidor
        """
        client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
        try:
            client_socket.connect(self.socket_path)
            
            client_socket.send(message.encode('utf-8'))
            response = client_socket.recv(1024)
            
            return response.decode('utf-8')
            
        finally:
            client_socket.close()
    
    def interactive_session(self):
        """
        Sesión interactiva con el servidor
        """
        print(f"Conectando a {self.socket_path}")
        print("Escribe mensajes (o 'quit' para salir)")
        
        while True:
            message = input("> ")
            if message.lower() in ['quit', 'exit']:
                break
            
            try:
                response = self.send_message(message)
                print(response)
            except Exception as e:
                print(f"Error: {e}")

def demo_unix_sockets():
    """
    Demonstración de sockets Unix
    """
    socket_path = "/tmp/demo_unix_socket"
    
    # Función para ejecutar servidor en thread separado
    def run_server():
        server = UnixSocketServer(socket_path)
        server.start_server()
    
    # Iniciar servidor en background
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Dar tiempo al servidor para inicializar
    time.sleep(1)
    
    # Crear cliente y enviar algunos mensajes
    client = UnixSocketClient(socket_path)
    
    try:
        # Enviar mensajes de prueba
        for i in range(3):
            message = f"Mensaje de prueba {i+1}"
            response = client.send_message(message)
            print(f"Enviado: {message}")
            print(f"Recibido: {response}")
            time.sleep(1)
        
        print("\nDemo completada. El servidor seguirá corriendo...")
        print("Puedes conectarte manualmente usando:")
        print(f"socat - UNIX-CONNECT:{socket_path}")
        
    except Exception as e:
        print(f"Error en demo: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        socket_path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/demo_unix_socket"
        server = UnixSocketServer(socket_path)
        server.start_server()
    elif len(sys.argv) > 1 and sys.argv[1] == "client":
        socket_path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/demo_unix_socket"
        client = UnixSocketClient(socket_path)
        client.interactive_session()
    else:
        demo_unix_sockets()