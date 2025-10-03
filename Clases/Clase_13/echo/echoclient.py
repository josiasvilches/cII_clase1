#!/usr/bin/env python3
import socket
import sys
import time

def echo_client(host='localhost', port=50007):
    """
    Cliente interactivo para el servidor echo
    """
    # Crear socket cliente
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Conectar al servidor
        print(f"Conectando a {host}:{port}...")
        client_socket.connect((host, port))
        print("Conectado! Escribe mensajes (o 'quit' para salir)")
        
        while True:
            # Obtener entrada del usuario
            message = "Este es un mensaje largo que será fragmentado"
            data = message.encode('utf-8')
            
            # Permitir al usuario terminar la sesión
            if message.lower() in ['quit', 'exit', 'q']:
                break
            
            try:
                # Enviar mensaje al servidor
                for i in range(0, len(data), 5):
                    fragment = data[i:i+5]
                    client_socket.send(fragment)
                    time.sleep(0.1) 
                                
                # Recibir respuesta del servidor
                response = client_socket.recv(1024)
                
                if not response:
                    print("Servidor cerró la conexión")
                    break
                
                print(f"Echo: {response.decode('utf-8')}")
                
            except Exception as e:
                print(f"Error en comunicación: {e}")
                break
        
    except ConnectionRefusedError:
        print(f"No se pudo conectar a {host}:{port}")
        print("¿Está el servidor ejecutándose?")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Conexión cerrada")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        echo_client()
    elif len(sys.argv) == 2:
        echo_client(port=int(sys.argv[1]))
    elif len(sys.argv) == 3:
        echo_client(sys.argv[1], int(sys.argv[2]))
    else:
        print("Uso: python echo_client.py [host] [puerto]")