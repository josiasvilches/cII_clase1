from multiprocessing import Process, Lock
import time
import os

def write_to_log_safe(lock, process_id, filename="log_safe.txt"):
    """ Adquiere el lock y escribe una línea en el archivo de log. """
    with lock:
        timestamp = time.ctime()
        pid = os.getpid()
        line = f"Proceso {process_id} (PID: {pid}) escribió a las {timestamp}\n"
        with open(filename, 'a') as f:
            print(f"Proceso {process_id} escribiendo...")
            f.write(line)
            time.sleep(0.1) # Simula I/O o trabajo dentro de la sección crítica
        print(f"Proceso {process_id} terminó de escribir.")

if __name__ == '__main__':
    log_filename = "log_safe.txt"
    if os.path.exists(log_filename): os.remove(log_filename) # Limpia el log anterior
    
    lock = Lock()
    processes = [Process(target=write_to_log_safe, args=(lock, i, log_filename)) for i in range(5)]
    
    for p in processes: p.start()
    for p in processes: p.join()
    
    print(f"\nContenido de {log_filename}:\n---")
    with open(log_filename, 'r') as f: print(f.read())
    print("---")