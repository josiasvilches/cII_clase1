#!/usr/bin/env python3
import socket
import sys

def echo_server_with_timeout(host='', port=50007, timeout=30):
    """
    Servidor echo que termina conexiones inactivas
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"Echo server con timeout de {timeout}s escuchando en puerto {port}")
        
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Conectado desde {client_address}")
            
            # Configurar timeout para este cliente
            client_socket.settimeout(timeout)
            
            try:
                with client_socket:
                    while True:
                        try:
                            data = client_socket.recv(1024)
                            if not data:
                                break
                            client_socket.sendall(data)
                            
                        except socket.timeout:
                            print(f"Cliente {client_address} expiró por inactividad")
                            break
                            
            except Exception as e:
                print(f"Error con cliente {client_address}: {e}")
                
    except KeyboardInterrupt:
        print("\nServidor detenido")
    finally:
        server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Usar valores por defecto
        echo_server_with_timeout()
    elif len(sys.argv) == 2:
        # Solo puerto especificado
        port = int(sys.argv[1])
        echo_server_with_timeout(port=port)
    elif len(sys.argv) == 3:
        # Host y puerto especificados
        host = sys.argv[1]
        port = int(sys.argv[2])
        echo_server_with_timeout(host, port)
    else:
        print("Uso: python echo_server.py [host] [puerto]")
        sys.exit(1)