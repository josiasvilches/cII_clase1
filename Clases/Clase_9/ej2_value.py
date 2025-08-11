from multiprocessing import Process, Value, Lock
import ctypes
import time
import random

def worker_stoppable_value(stop_flag, lock, worker_id): # Renombrado
    """ Trabaja hasta que el flag de parada (un Value) se active. """
    count = 0
    while True:
        with lock: # Necesario para leer el flag de forma segura
            if stop_flag.value == 1: # 1 significa parar
                print(f"Worker {worker_id} (Value-Flag): ¡Señal de parada recibida! Terminando tras {count} iteraciones.")
                break
        
        print(f"Worker {worker_id} (Value-Flag): Trabajando (iteración {count})...")
        count += 1
        time.sleep(random.uniform(0.5,1.0)) # Simula trabajo

def manager_value_flag(stop_flag, lock): # Renombrado
    """ Espera un tiempo y luego activa el flag de parada. """
    duration = 5
    print(f"Manager (Value-Flag): Workers trabajando por {duration} segundos...")
    time.sleep(duration)
    print("Manager (Value-Flag): ¡Enviando señal de parada!")
    with lock:
        stop_flag.value = 1 # Establece el flag a 1

if __name__ == '__main__':
    # 'i' para entero C, 0 es el valor inicial (0=seguir, 1=parar)
    flag_val = Value(ctypes.c_int, 0) # Renombrado
    lock_flag = Lock() # Renombrado

    workers_vf = [Process(target=worker_stoppable_value, args=(flag_val, lock_flag, i)) for i in range(3)] # Renombrado
    mgr_vf = Process(target=manager_value_flag, args=(flag_val, lock_flag)) # Renombrado

    for w in workers_vf:
        w.start()
    mgr_vf.start()

    for w in workers_vf:
        w.join()
    mgr_vf.join()
    print("Sistema (Value-Flag) terminado.")