#!/usr/bin/env python3
"""
Servidor de Procesamiento con Multiprocessing (Parte B)
Servidor que procesa tareas CPU-bound usando multiprocessing
"""

import socket
import struct
import argparse
import sys
import signal
from multiprocessing import Pool, cpu_count, Manager
from typing import Dict, Any
import json

# Importar módulos de procesamiento
from processor.screenshot import capture_screenshot, is_screenshot_available
from processor.performance import analyze_performance
from processor.image_processor import process_images_parallel
from common.protocol import (
    ProtocolMessage,
    create_response,
    create_error_response,
    MSG_TYPE_SCREENSHOT,
    MSG_TYPE_PERFORMANCE,
    MSG_TYPE_IMAGE_PROCESSING
)
from common.serialization import serialize_json, deserialize_json


class ProcessingServer:
    """Servidor de procesamiento con multiprocessing"""
    
    def __init__(self, host: str, port: int, num_processes: int = None):
        """
        Inicializa el servidor de procesamiento
        
        Args:
            host: Dirección de escucha
            port: Puerto de escucha
            num_processes: Número de procesos en el pool
        """
        self.host = host
        self.port = port
        self.num_processes = num_processes or cpu_count()
        self.pool = None
        self.socket = None
        self.running = False
    
    def start(self):
        """Inicia el servidor"""
        print(f"Inicializando pool de {self.num_processes} procesos...")
        self.pool = Pool(processes=self.num_processes)
        
        print(f"Creando socket en {self.host}:{self.port}...")

        # Resolver la familia (IPv4/IPv6) usando getaddrinfo para soportar ambos
        try:
            addrinfo = socket.getaddrinfo(self.host, self.port, 0, socket.SOCK_STREAM)
            af, socktype, proto, canonname, sa = addrinfo[0]

            self.socket = socket.socket(af, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Si es IPv6, intentar configurar dual-stack cuando sea posible
            try:
                if af == socket.AF_INET6:
                    # Intentar permitir conexiones IPv4 en la misma socket (si el SO lo permite)
                    self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            except Exception:
                # No todos los sistemas permiten cambiar esta opción; ignorar si falla
                pass

            self.socket.bind(sa)
            self.socket.listen(5)
            self.running = True
            
            print(f"Servidor de procesamiento escuchando en {self.host}:{self.port}")
            print(f"Procesos en pool: {self.num_processes}")
            print("Esperando conexiones...\n")
            
            self.accept_connections()
            
        except OSError as e:
            print(f"Error al iniciar servidor: {e}")
            self.cleanup()
            sys.exit(1)
    
    def accept_connections(self):
        """Acepta conexiones entrantes"""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                print(f"Conexión recibida desde {address}")
                
                # Manejar cliente
                self.handle_client(client_socket, address)
                
            except KeyboardInterrupt:
                print("\nDeteniendo servidor...")
                break
            except Exception as e:
                print(f"Error aceptando conexión: {e}")
    
    def handle_client(self, client_socket: socket.socket, address: tuple):
        """
        Maneja una conexión de cliente
        
        Args:
            client_socket: Socket del cliente
            address: Dirección del cliente
        """
        try:
            # Leer header (5 bytes: 4 de longitud + 1 de tipo)
            header = self.recv_exact(client_socket, 5)
            
            if not header:
                return
            
            length, msg_type = struct.unpack('!IB', header)
            
            # Leer datos (length ya incluye el byte del tipo)
            data_bytes = self.recv_exact(client_socket, length - 1)
            
            if not data_bytes:
                return
            
            # Deserializar mensaje
            message_data = deserialize_json(data_bytes)
            message = ProtocolMessage(msg_type, message_data)
            
            # Procesar mensaje
            response = self.process_message(message)
            
            # Enviar respuesta
            response_bytes = response.encode()
            client_socket.sendall(response_bytes)
            
            # Asegurar que los datos se envíen antes de cerrar
            client_socket.shutdown(socket.SHUT_WR)
            
        except socket.error as e:
            # Ignorar errores de socket cerrado, es esperado
            if e.errno not in (32, 104):  # EPIPE, ECONNRESET
                print(f"Error de socket con cliente {address}: {e}")
        
        except Exception as e:
            print(f"Error manejando cliente {address}: {e}")
        
        finally:
            try:
                client_socket.close()
            except:
                pass
            print(f"Conexión cerrada con {address}")
    
    def recv_exact(self, sock: socket.socket, num_bytes: int) -> bytes:
        """
        Recibe exactamente num_bytes del socket
        
        Args:
            sock: Socket
            num_bytes: Número de bytes a recibir
            
        Returns:
            bytes: Datos recibidos
        """
        data = b''
        while len(data) < num_bytes:
            chunk = sock.recv(num_bytes - len(data))
            if not chunk:
                return b''
            data += chunk
        return data
    
    def process_message(self, message: ProtocolMessage) -> ProtocolMessage:
        """
        Procesa un mensaje y retorna la respuesta
        
        Args:
            message: Mensaje a procesar
            
        Returns:
            ProtocolMessage con la respuesta
        """
        try:
            if message.msg_type == MSG_TYPE_SCREENSHOT:
                # Procesar screenshot en el pool
                url = message.data.get('url')
                print(f"Procesando screenshot para {url}")
                
                # Ejecutar en proceso separado
                result = self.pool.apply(process_screenshot_task, (url,))
                
                return create_response({'screenshot': result})
            
            elif message.msg_type == MSG_TYPE_PERFORMANCE:
                # Procesar análisis de rendimiento
                url = message.data.get('url')
                print(f"Analizando rendimiento de {url}")
                
                # Ejecutar en proceso separado
                result = self.pool.apply(process_performance_task, (url,))
                
                return create_response({'performance': result})
            
            elif message.msg_type == MSG_TYPE_IMAGE_PROCESSING:
                # Procesar imágenes
                url = message.data.get('url')
                images = message.data.get('images', [])
                print(f"Procesando {len(images)} imágenes para {url}")
                
                # Ejecutar en proceso separado
                result = self.pool.apply(process_images_task, (images,))
                
                return create_response({'thumbnails': result})
            
            else:
                return create_error_response(f"Tipo de mensaje desconocido: {message.msg_type}")
        
        except Exception as e:
            print(f"Error procesando mensaje: {e}")
            return create_error_response(str(e))
    
    def cleanup(self):
        """Limpia recursos"""
        print("Limpiando recursos...")
        
        if self.pool:
            self.pool.close()
            self.pool.join()
        
        if self.socket:
            self.socket.close()
    
    def stop(self):
        """Detiene el servidor"""
        self.running = False
        self.cleanup()


# Funciones de procesamiento que se ejecutarán en procesos separados

def process_screenshot_task(url: str) -> str:
    """
    Tarea para procesar screenshot en un proceso separado
    
    Args:
        url: URL a capturar
        
    Returns:
        str: Screenshot en base64 o None
    """
    try:
        if is_screenshot_available():
            screenshot = capture_screenshot(url, timeout=30000)
            return screenshot
        else:
            print("Selenium no disponible, screenshot omitido")
            return None
    except Exception as e:
        print(f"Error en process_screenshot_task: {e}")
        return None


def process_performance_task(url: str) -> Dict[str, Any]:
    """
    Tarea para analizar rendimiento en un proceso separado
    
    Args:
        url: URL a analizar
        
    Returns:
        Dict con métricas de rendimiento
    """
    try:
        performance = analyze_performance(url, timeout=30)
        return performance
    except Exception as e:
        print(f"Error en process_performance_task: {e}")
        return {'error': str(e)}


def process_images_task(image_urls: list) -> list:
    """
    Tarea para procesar imágenes en un proceso separado
    
    Args:
        image_urls: Lista de URLs de imágenes
        
    Returns:
        list: Lista de thumbnails en base64
    """
    try:
        result = process_images_parallel(image_urls, max_images=5)
        return result.get('thumbnails', [])
    except Exception as e:
        print(f"Error en process_images_task: {e}")
        return []


def parse_arguments():
    """Parsea argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description='Servidor de Procesamiento Distribuido',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--ip',
        type=str,
        required=True,
        help='Dirección de escucha'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        required=True,
        help='Puerto de escucha'
    )
    
    parser.add_argument(
        '-n', '--processes',
        type=int,
        default=None,
        help=f'Número de procesos en el pool (default: {cpu_count()})'
    )
    
    return parser.parse_args()


def signal_handler(sig, frame):
    """Manejador de señales para Ctrl+C"""
    print("\n\nSeñal de interrupción recibida. Deteniendo servidor...")
    sys.exit(0)


def main():
    """Función principal"""
    # Registrar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    args = parse_arguments()
    
    print("=" * 60)
    print("Servidor de Procesamiento Distribuido (Parte B)")
    print("=" * 60)
    print(f"Escuchando en: {args.ip}:{args.port}")
    print(f"Procesos en pool: {args.processes or cpu_count()}")
    print("=" * 60)
    print("\nCapacidades:")
    print("  - Captura de screenshots (selenium)")
    print("  - Análisis de rendimiento")
    print("  - Procesamiento de imágenes (thumbnails)")
    print("\nPresiona Ctrl+C para detener el servidor\n")
    
    # Crear y arrancar servidor
    server = ProcessingServer(args.ip, args.port, args.processes)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\nServidor detenido por el usuario")
    finally:
        server.cleanup()
        sys.exit(0)


if __name__ == '__main__':
    main()
