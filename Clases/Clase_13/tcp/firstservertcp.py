#!/usr/bin/env python3
import socket
import sys

def create_server(port):
    """
    Crea y configura un socket servidor TCP
    """
    # Crear socket TCP para IPv4
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Configurar para reutilizar la dirección inmediatamente
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    return server_socket

def start_server(port):
    """
    Inicia el servidor y maneja conexiones entrantes
    """
    server_socket = create_server(port)
    
    try:
        # Vincular a todas las interfaces disponibles en el puerto especificado
        host = ""  # Cadena vacía significa "todas las interfaces"
        server_socket.bind((host, port))
        
        # Comenzar a escuchar conexiones (queue máximo de 5)
        server_socket.listen(5)
        print(f"Servidor escuchando en puerto {port}...")
        
        while True:
            print("Esperando conexiones remotas...")
            
            # Aceptar conexión entrante (operación bloqueante)
            client_socket, client_address = server_socket.accept()
            
            print(f"Conexión establecida desde {client_address}")
            
            try:
                # Preparar mensaje de respuesta
                message = 'Hola Mundo\r\n'
                print("Enviando mensaje...")
                
                # Enviar respuesta al cliente
                client_socket.send(message.encode('utf-8'))
                
            except Exception as e:
                print(f"Error al comunicarse con cliente: {e}")
            
            finally:
                print("Cerrando conexión...")
                client_socket.close()
                
    except KeyboardInterrupt:
        print("\nServidor detenido por usuario")
    except Exception as e:
        print(f"Error del servidor: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python server.py <puerto>")
        sys.exit(50)
    
    try:
        port = int(sys.argv[1])
        start_server(port)
    except ValueError:
        print("Error: El puerto debe ser un número entero")
        sys.exit(1)