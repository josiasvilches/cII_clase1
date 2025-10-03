#!/usr/bin/env python3
import socket
import sys

def create_client():
    """
    Crea un socket cliente TCP
    """
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def connect_and_communicate(host, port):
    """
    Se conecta al servidor y maneja la comunicación
    """
    client_socket = create_client()
    
    try:
        print("Iniciando conexión...")
        
        # Establecer conexión con el servidor
        client_socket.connect((host, port))
        print("Handshake realizado con éxito!")
        
        # Enviar datos al servidor (opcional en este ejemplo)
        greeting = b'Hola servidor'
        client_socket.send(greeting)
        
        # Recibir respuesta del servidor
        print("Esperando datos desde el servidor...")
        response = client_socket.recv(1024)
        
        # Decodificar y mostrar la respuesta
        print(response.decode('utf-8'))
        
    except socket.gaierror as e:
        print(f"Error de resolución de nombre: {e}")
    except ConnectionRefusedError as e:
        print(f"Conexión rechazada: {e}")
    except socket.timeout as e:
        print(f"Timeout de conexión: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        print("Cerrando conexión")
        client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python client.py <host> <puerto>")
        sys.exit(50)
    
    host = sys.argv[1]
    
    try:
        port = int(sys.argv[2])
        connect_and_communicate(host, port)
    except ValueError:
        print("Error: El puerto debe ser un número entero")
        sys.exit(1)