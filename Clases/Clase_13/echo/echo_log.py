import time
import logging
import socket

def setup_logging():
    """Configura logging detallado"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def echo_server_with_logging(host='', port=50007):
    """
    Servidor echo con logging detallado
    """
    logger = setup_logging()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(1)
        logger.info(f"Servidor iniciado en puerto {port}")
        
        connection_count = 0
        
        while True:
            logger.info("Esperando conexión...")
            client_socket, client_address = server_socket.accept()
            connection_count += 1
            
            logger.info(f"Conexión #{connection_count} desde {client_address}")
            
            try:
                with client_socket:
                    bytes_transferred = 0
                    start_time = time.time()
                    
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        
                        bytes_transferred += len(data)
                        logger.debug(f"Recibidos {len(data)} bytes: {data[:50]}...")
                        
                        client_socket.sendall(data)
                        logger.debug(f"Enviados {len(data)} bytes de vuelta")
                    
                    duration = time.time() - start_time
                    logger.info(f"Conexión #{connection_count} terminada. "
                              f"Duración: {duration:.2f}s, "
                              f"Bytes transferidos: {bytes_transferred}")
                              
            except Exception as e:
                logger.error(f"Error en conexión #{connection_count}: {e}")
                
    except KeyboardInterrupt:
        logger.info("Servidor detenido por usuario")
    finally:
        server_socket.close()
        logger.info("Servidor cerrado")

if __name__ == "__main__":
    echo_server_with_logging()