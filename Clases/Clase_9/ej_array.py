from multiprocessing import Process, Array, Lock
import ctypes
import random
import time

def fill_array_parallel(arr, lock, start_index, count, value_base, process_id): # Renombrado
    """ Rellena una porción del array de forma segura. """
    for i in range(count):
        index_to_fill = start_index + i
        # Simula algún cálculo para el valor
        value_to_write = value_base + random.randint(0, i*10) 
        with lock: # Protege la escritura en el índice específico
            arr[index_to_fill] = value_to_write
            print(f"Proceso {process_id} (Array): Escribió {arr[index_to_fill]} en índice {index_to_fill}")
        time.sleep(random.uniform(0.01, 0.05)) # Simula trabajo

if __name__ == '__main__':
    ARRAY_SIZE = 10 # Renombrado
    # 'i' para entero C, ARRAY_SIZE es el tamaño
    shared_array_ex = Array(ctypes.c_int, ARRAY_SIZE) # Renombrado
    # Usamos el lock interno del Array o un Lock externo
    lock_arr = shared_array_ex.get_lock() # Renombrado
    # Alternativamente: lock_arr = Lock()

    # Proceso 1 llena la primera mitad
    p1_arr = Process(target=fill_array_parallel, args=(shared_array_ex, lock_arr, 0, ARRAY_SIZE // 2, 100, 1))
    # Proceso 2 llena la segunda mitad
    p2_arr = Process(target=fill_array_parallel, args=(shared_array_ex, lock_arr, ARRAY_SIZE // 2, ARRAY_SIZE - (ARRAY_SIZE // 2), 200, 2))

    # Imprime el estado inicial (antes de que los procesos escriban)
    # Es importante notar que si se accede aquí sin lock mientras los workers están activos,
    # se podría obtener un estado inconsistente.
    with lock_arr:
        print(f"Array inicial (Array): {shared_array_ex[:]}")
    
    p1_arr.start()
    p2_arr.start()
    p1_arr.join()
    p2_arr.join()
    
    with lock_arr: # Proteger la lectura final también
        print(f"Array final (Array): {shared_array_ex[:]}")