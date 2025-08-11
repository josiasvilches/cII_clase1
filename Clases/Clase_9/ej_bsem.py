from multiprocessing import Process, BoundedSemaphore
import time

def worker_bs(b_sem, i):
    """ Intenta liberar el semáforo sin adquirirlo primero o de más. """
    print(f"Proceso {i} (BSem): Intentando adquirir...")
    b_sem.acquire()
    print(f"Proceso {i} (BSem): Adquirido.")
    time.sleep(1)
    print(f"Proceso {i} (BSem): Liberando...")
    b_sem.release()
    print(f"Proceso {i} (BSem): Liberado.")
    
    # Intento de liberación extra
    try:
        print(f"Proceso {i} (BSem): Intentando liberar OTRA VEZ (esto causará error)...")
        b_sem.release()
    except ValueError as e:
        print(f"Proceso {i} (BSem): ¡ERROR! {e}")

if __name__ == '__main__':
    # Creamos un BoundedSemaphore con valor 1 (actúa como un Lock acotado)
    bounded_sem_ex = BoundedSemaphore(1) # Renombrado
    
    p_bs = Process(target=worker_bs, args=(bounded_sem_ex, 1)) # Renombrado
    p_bs.start()
    p_bs.join()
    
    # Intentamos liberar desde el principal (también causará error si el contador ya está en el límite)
    try:
        print("Principal (BSem): Intentando liberar (esto podría causar error)...")
        # Si el worker lo dejó en 1, esta liberación fallará.
        bounded_sem_ex.release() 
    except ValueError as e:
        print(f"Principal (BSem): ¡ERROR! {e}")