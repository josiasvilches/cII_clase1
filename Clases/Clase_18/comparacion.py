#!/usr/bin/env python3
import socketserver
import threading
import os
import time

class BenchmarkHandler(socketserver.BaseRequestHandler):
    """Handler que simula trabajo computacional para benchmarks"""
    
    def handle(self):
        # Identificar el tipo de servidor y modelo de concurrencia
        server_type = type(self.server).__name__
        thread_id = threading.current_thread().name
        process_id = os.getpid()
        
        # Simular trabajo computacional
        start_time = time.time()
        result = sum(i*i for i in range(10000))  # Trabajo CPU-intensivo
        end_time = time.time()
        
        # Preparar respuesta con métricas
        response = f"""
Servidor: {server_type}
Hilo/Proceso: {thread_id} (PID: {process_id})
Cliente: {self.client_address}
Tiempo de procesamiento: {end_time - start_time:.4f}s
Resultado: {result}
Hilos activos: {threading.active_count()}
"""
        
        self.request.sendall(response.encode('utf-8'))

# Servidor secuencial (una conexión a la vez)
class SequentialServer(socketserver.TCPServer):
    """Servidor que maneja conexiones secuencialmente"""
    allow_reuse_address = True

# Servidor con hilos (Threading)
class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Servidor que crea un hilo por conexión"""
    allow_reuse_address = True
    daemon_threads = True

# Servidor con procesos (Forking) - Solo Unix/Linux
class ForkedServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    """Servidor que crea un proceso por conexión"""
    allow_reuse_address = True

def demo_concurrent_servers():
    """Demostración de diferentes modelos de concurrencia"""
    
    servers = [
        ("Secuencial", SequentialServer, 9001),
        ("Con Hilos", ThreadedServer, 9002),
        # ("Con Procesos", ForkedServer, 9003),  # Descomentar en Unix/Linux
    ]
    
    print("Iniciando servidores de demostración...")
    print("Usa múltiples conexiones telnet para probar concurrencia:")
    
    for name, server_class, port in servers:
        print(f"  telnet localhost {port}  # {name}")
    
    print("\nPresiona Ctrl+C para detener todos los servidores\n")
    
    # Iniciar todos los servidores en hilos separados
    server_threads = []
    actual_servers = []
    
    for name, server_class, port in servers:
        try:
            server = server_class(("localhost", port), BenchmarkHandler)
            actual_servers.append(server)
            
            thread = threading.Thread(
                target=server.serve_forever,
                name=f"{name}Server"
            )
            thread.daemon = True
            thread.start()
            server_threads.append(thread)
            
            print(f"✓ Servidor {name} iniciado en puerto {port}")
            
        except Exception as e:
            print(f"✗ Error iniciando servidor {name}: {e}")
    
    try:
        # Mantener el programa principal activo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo servidores...")
        for server in actual_servers:
            server.shutdown()
            server.server_close()

if __name__ == "__main__":
    demo_concurrent_servers()