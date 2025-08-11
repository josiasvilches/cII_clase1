from multiprocessing import Process, Array, Lock
import ctypes
import time # Necesario para time.sleep
import random

def swap_elements_array(arr, lock, index1, index2, worker_id): # Renombrado
    """ Intercambia dos elementos del array de forma segura. """
    with lock:
        # Guardamos temporalmente antes de que otro proceso pueda cambiarlo
        # Esto es crucial si el lock es granular y otro proceso podría estar
        # modificando index2 mientras este proceso lee index1.
        # Con un lock global para todo el array, es menos crítico pero buena práctica.
        temp = arr[index1]
        arr[index1] = arr[index2]
        arr[index2] = temp
        print(f"Worker {worker_id} (Array-Rev): Intercambió arr[{index1}] ({arr[index2]}) <-> arr[{index2}] ({temp})")
    # Simula un poco de trabajo o retardo
    time.sleep(random.uniform(0.01, 0.05))


def parallel_reverser_array(arr, lock, worker_id, num_total_workers, array_size): # Renombrado
    """ 
    Invierte el array de forma paralela. Cada worker se encarga de una
    fracción de los intercambios necesarios.
    """
    # Cada worker procesa un subconjunto de los pares a intercambiar.
    # El bucle va hasta la mitad del array.
    # El 'step' es num_total_workers para que cada worker tome un par,
    # luego el siguiente worker tome el siguiente, y así sucesivamente.
    for i in range(worker_id, array_size // 2, num_total_workers):
        j = array_size - 1 - i
        # Solo hacemos el swap si i y j son diferentes (para arrays de tamaño impar, el del medio no se mueve)
        if i < j : # Asegura que no intentemos swapear el mismo elemento consigo mismo ni crucemos
            swap_elements_array(arr, lock, i, j, worker_id)


if __name__ == '__main__':
    ARRAY_REV_SIZE = 11 # Renombrado
    NUM_REV_WORKERS = 2 # Renombrado
    
    # 'i' para entero C, creamos el array [0, 1, 2, ..., ARRAY_REV_SIZE-1]
    my_array_rev = Array(ctypes.c_int, list(range(ARRAY_REV_SIZE))) # Renombrado
    lock_rev = my_array_rev.get_lock() # Renombrado

    with lock_rev: # Leer estado inicial de forma segura
        print(f"Array inicial (Array-Rev): {my_array_rev[:]}")
    
    processes_rev = [] # Renombrado
    for i in range(NUM_REV_WORKERS):
        p = Process(target=parallel_reverser_array, args=(my_array_rev, lock_rev, i, NUM_REV_WORKERS, ARRAY_REV_SIZE))
        processes_rev.append(p)
        p.start()

    for p in processes_rev:
        p.join()

    with lock_rev: # Leer estado final de forma segura
        print(f"Array final (Array-Rev):   {my_array_rev[:]}")
