#!/usr/bin/env python3
import socket
import sys

def echo_server(host='', port=50007):
    """
    Implementa un servidor echo que devuelve todos los datos recibidos
    """
    # Crear socket servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Vincular a la dirección especificada
        server_socket.bind((host, port))
        server_socket.listen(1)  # Aceptar una conexión a la vez para simplicidad
        
        print(f"Echo server escuchando en {host if host else 'todas las interfaces'}:{port}")
        
        while True:
            # Aceptar conexión entrante
            print("Esperando conexión...")
            client_socket, client_address = server_socket.accept()
            
            print(f"Conectado desde {client_address}")
            
            try:
                # Usar context manager para asegurar cleanup
                with client_socket:
                    # Loop principal de echo para esta conexión
                    while True:
                        # Recibir datos del cliente
                        data = client_socket.recv(1024)
                        if not data:
                            print("Desconexión limpia")
                            break
                        
                        print(f"Recibido: {data}")
                        
                        # Echo: enviar los datos de vuelta al cliente
                        client_socket.sendall(data)
                        
            except ConnectionResetError:
                print("Cliente terminó la conexión abruptamente")
            except socket.timeout:
                print("Timeout - cliente no responde")
            except Exception as e:
                print(f"Error manejando cliente: {e}")
            
            print("Conexión con cliente finalizada")
            
    except KeyboardInterrupt:
        print("\nServidor detenido por usuario")
    except Exception as e:
        print(f"Error del servidor: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Usar valores por defecto
        echo_server()
    elif len(sys.argv) == 2:
        # Solo puerto especificado
        port = int(sys.argv[1])
        echo_server(port=port)
    elif len(sys.argv) == 3:
        # Host y puerto especificados
        host = sys.argv[1]
        port = int(sys.argv[2])
        echo_server(host, port)
    else:
        print("Uso: python echo_server.py [host] [puerto]")
        sys.exit(1)