from multiprocessing import Process, RLock
import time

def worker_rlock(rlock, i):
    """ Función que adquiere el RLock dos veces. """
    print(f"Proceso {i}: Intentando adquirir (1ra vez)...")
    rlock.acquire()
    print(f"Proceso {i}: Adquirido (1ra vez).")
    try:
        print(f"Proceso {i}: Intentando adquirir (2da vez)...")
        rlock.acquire() # Esto funcionará gracias a RLock
        print(f"Proceso {i}: Adquirido (2da vez).")
        try:
            print(f"Proceso {i}: Trabajando...")
            time.sleep(0.5)
        finally:
            print(f"Proceso {i}: Liberando (2da vez)...")
            rlock.release()
            print(f"Proceso {i}: Liberado (2da vez).")
    finally:
        print(f"Proceso {i}: Liberando (1ra vez)...")
        rlock.release()
        print(f"Proceso {i}: Liberado (1ra vez).")

if __name__ == '__main__':
    rlock = RLock()
    processes = [Process(target=worker_rlock, args=(rlock, i)) for i in range(3)]
    for p in processes: p.start()
    for p in processes: p.join()