#!/usr/bin/env python3
import socketserver
import threading
import time
import json

class ChatHandler(socketserver.BaseRequestHandler):
    """
    Handler para un sistema de chat simple usando TCP concurrente.
    Cada cliente es manejado en un hilo separado.
    """
    
    # Variable de clase para almacenar clientes conectados
    clients = {}
    clients_lock = threading.Lock()
    
    def setup(self):
        """Se ejecuta antes de handle() - inicialización"""
        self.username = None
        print(f"Nueva conexión desde {self.client_address}")
    
    def handle(self):
        """Maneja la comunicación con un cliente específico"""
        try:
            # Solicitar nombre de usuario
            self.request.sendall(b"Ingresa tu nombre de usuario: ")
            username_data = self.request.recv(1024)
            self.username = username_data.decode('utf-8').strip()
            
            # Registrar cliente
            with self.clients_lock:
                self.clients[self.username] = self.request
            
            # Notificar a otros clientes
            self.broadcast_message(f"{self.username} se unió al chat", exclude_self=True)
            self.request.sendall(b"Bienvenido al chat! Escribe 'quit' para salir.\n")
            
            # Bucle principal de chat
            while True:
                data = self.request.recv(1024)
                if not data:
                    break
                    
                message = data.decode('utf-8').strip()
                
                if message.lower() == 'quit':
                    break
                elif message.startswith('/list'):
                    self.send_user_list()
                elif message.startswith('/whisper'):
                    self.handle_whisper(message)
                else:
                    # Mensaje público
                    full_message = f"[{self.username}]: {message}"
                    self.broadcast_message(full_message)
                    
        except Exception as e:
            print(f"Error en handler para {self.username}: {e}")
        
    def finish(self):
        """Se ejecuta después de handle() - limpieza"""
        if self.username:
            # Remover cliente de la lista
            with self.clients_lock:
                self.clients.pop(self.username, None)
            
            # Notificar salida
            self.broadcast_message(f"{self.username} abandonó el chat", exclude_self=True)
            print(f"{self.username} desconectado")
    
    def broadcast_message(self, message, exclude_self=False):
        """Envía un mensaje a todos los clientes conectados"""
        with self.clients_lock:
            dead_clients = []
            
            for username, client_socket in self.clients.items():
                if exclude_self and username == self.username:
                    continue
                    
                try:
                    client_socket.sendall(f"{message}\n".encode('utf-8'))
                except:
                    # Cliente desconectado, marcar para eliminación
                    dead_clients.append(username)
            
            # Limpiar clientes desconectados
            for username in dead_clients:
                self.clients.pop(username, None)
    
    def send_user_list(self):
        """Envía la lista de usuarios conectados"""
        with self.clients_lock:
            users = list(self.clients.keys())
            user_list = f"Usuarios conectados: {', '.join(users)}\n"
            self.request.sendall(user_list.encode('utf-8'))
    
    def handle_whisper(self, message):
        """Maneja mensajes privados"""
        try:
            # Formato: /whisper username mensaje
            parts = message.split(' ', 2)
            if len(parts) < 3:
                self.request.sendall(b"Uso: /whisper <usuario> <mensaje>\n")
                return
                
            target_user = parts[1]
            whisper_message = parts[2]
            
            with self.clients_lock:
                if target_user in self.clients:
                    target_socket = self.clients[target_user]
                    private_msg = f"[PRIVADO de {self.username}]: {whisper_message}\n"
                    target_socket.sendall(private_msg.encode('utf-8'))
                    self.request.sendall(b"Mensaje privado enviado.\n")
                else:
                    self.request.sendall(f"Usuario '{target_user}' no encontrado.\n".encode('utf-8'))
                    
        except Exception as e:
            self.request.sendall(f"Error enviando mensaje privado: {e}\n".encode('utf-8'))

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    Servidor TCP que crea un hilo para cada conexión.
    Hereda de ThreadingMixIn para funcionalidad concurrente.
    """
    
    # Permitir reutilización rápida de la dirección
    allow_reuse_address = True
    
    # Los hilos daemon se terminan automáticamente al cerrar el servidor
    daemon_threads = True

if __name__ == "__main__":
    HOST, PORT = "localhost", 7777
    
    # Crear servidor concurrente
    server = ThreadedTCPServer((HOST, PORT), ChatHandler)
    
    print(f"Servidor de chat iniciado en {HOST}:{PORT}")
    print(f"Máximo de hilos concurrentes: {threading.active_count()}")
    print("Conecta múltiples clientes con: telnet localhost 7777")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\nCerrando servidor... Hilos activos: {threading.active_count()}")
        server.shutdown()
        server.server_close()