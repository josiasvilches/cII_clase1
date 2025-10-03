#!/usr/bin/env python3
import os
import stat
import time

class NamedPipeDemo:
    """
    Demonstración de named pipes para IPC
    """
    
    def __init__(self, pipe_path):
        self.pipe_path = pipe_path
    
    def create_pipe(self):
        """
        Crea el named pipe si no existe
        """
        try:
            # Verificar si ya existe
            if os.path.exists(self.pipe_path):
                # Verificar que sea realmente un pipe
                if stat.S_ISFIFO(os.stat(self.pipe_path).st_mode):
                    print(f"Named pipe {self.pipe_path} ya existe")
                    return
                else:
                    print(f"Archivo {self.pipe_path} existe pero no es un pipe")
                    return
            
            # Crear named pipe
            os.mkfifo(self.pipe_path)
            print(f"Named pipe creado: {self.pipe_path}")
            
        except OSError as e:
            print(f"Error creando named pipe: {e}")
            raise
    
    def write_to_pipe(self, messages):
        """
        Escribe mensajes al pipe
        """
        print(f"Abriendo pipe para escritura: {self.pipe_path}")
        
        try:
            # Abrir pipe para escritura (esto bloquea hasta que alguien abra para lectura)
            with open(self.pipe_path, 'w') as pipe:
                print("Pipe abierto para escritura")
                
                for message in messages:
                    print(f"Escribiendo: {message}")
                    pipe.write(f"{message}\n")
                    pipe.flush()
                    time.sleep(1)
                    
        except Exception as e:
            print(f"Error escribiendo al pipe: {e}")
    
    def read_from_pipe(self):
        """
        Lee mensajes del pipe
        """
        print(f"Abriendo pipe para lectura: {self.pipe_path}")
        
        try:
            # Abrir pipe para lectura
            with open(self.pipe_path, 'r') as pipe:
                print("Pipe abierto para lectura")
                print("Esperando mensajes...")
                
                while True:
                    line = pipe.readline()
                    if not line:
                        break
                    
                    print(f"Recibido: {line.strip()}")
                    
        except Exception as e:
            print(f"Error leyendo del pipe: {e}")
    
    def cleanup(self):
        """
        Limpia el named pipe
        """
        try:
            if os.path.exists(self.pipe_path):
                os.unlink(self.pipe_path)
                print(f"Named pipe {self.pipe_path} eliminado")
        except OSError as e:
            print(f"Error eliminando pipe: {e}")

def demo_named_pipes():
    """
    Demonstración de named pipes
    """
    pipe_path = "/tmp/demo_named_pipe"
    demo = NamedPipeDemo(pipe_path)
    
    try:
        # Crear pipe
        demo.create_pipe()
        
        # En una aplicación real, estos correrían en procesos separados
        import threading
        
        # Función para leer en thread separado
        def reader():
            time.sleep(2)  # Dar tiempo al escritor para comenzar
            demo.read_from_pipe()
        
        # Iniciar reader en background
        reader_thread = threading.Thread(target=reader)
        reader_thread.daemon = True
        reader_thread.start()
        
        # Escribir mensajes
        messages = [
            "Primer mensaje",
            "Segundo mensaje",
            "Mensaje final"
        ]
        demo.write_to_pipe(messages)
        
        # Esperar que termine la lectura
        reader_thread.join(timeout=5)
        
    finally:
        demo.cleanup()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        pipe_path = sys.argv[1]
        demo = NamedPipeDemo(pipe_path)
        
        if len(sys.argv) > 2 and sys.argv[2] == "write":
            demo.create_pipe()
            messages = sys.argv[3:] if len(sys.argv) > 3 else ["Mensaje de prueba"]
            demo.write_to_pipe(messages)
        elif len(sys.argv) > 2 and sys.argv[2] == "read":
            demo.read_from_pipe()
        else:
            demo_named_pipes()
    else:
        demo_named_pipes()