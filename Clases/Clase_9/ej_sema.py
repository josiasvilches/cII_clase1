from multiprocessing import Process, Semaphore
import time
import random

def database_worker_sem(semaphore, process_id): # Renombrado
    """ Simula un worker que necesita una conexión a la BD. """
    print(f"Proceso {process_id}: Esperando conexión a la BD...")
    semaphore.acquire()
    print(f"Proceso {process_id}: Conexión obtenida. Trabajando...")
    try:
        # Simula trabajo con la BD
        time.sleep(random.uniform(0.5, 2.0))
    finally:
        print(f"Proceso {process_id}: Liberando conexión.")
        semaphore.release()

if __name__ == '__main__':
    # Creamos un semáforo que permite hasta 2 conexiones simultáneas
    db_connections_sem = Semaphore(2) # Renombrado
    
    processes_sem = [] # Renombrado
    print("Lanzando 15 workers para acceder a 2 conexiones de BD (Semaphore)...")
    for i in range(15):
        p = Process(target=database_worker_sem, args=(db_connections_sem, i))
        processes_sem.append(p)
        p.start()

    for p in processes_sem:
        p.join()
    print("Todos los workers (Semaphore) han terminado.")