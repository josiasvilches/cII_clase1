from multiprocessing import Process, Value, Lock
import ctypes
import time

def modifier_value(shared_value, lock): # Renombrado
    """ Incrementa el valor compartido 10000 veces de forma segura. """
    for _ in range(10000):
        with lock: # Usa el lock para proteger la operación RMW (Read-Modify-Write)
            shared_value.value += 1

def reader_value(shared_value, lock): # Renombrado
    """ Lee el valor periódicamente de forma segura. """
    for i in range(5):
        with lock: # También usa lock para lectura consistente
            print(f"Lector (Value): Valor actual en iteración {i} = {shared_value.value}")
        time.sleep(0.5)

if __name__ == '__main__':
    # 'i' para entero C, 0 es el valor inicial
    v_ex = Value(ctypes.c_int, 0) # Renombrado
    # Creamos un Lock explícito para proteger v_ex. Alternativamente, v_ex.get_lock()
    l_val = Lock() # Renombrado

    m1_val = Process(target=modifier_value, args=(v_ex, l_val)) # Renombrado
    m2_val = Process(target=modifier_value, args=(v_ex, l_val)) # Renombrado
    r_val = Process(target=reader_value, args=(v_ex, l_val)) # Renombrado

    m1_val.start()
    m2_val.start()
    r_val.start()

    m1_val.join()
    m2_val.join()
    r_val.join()

    # Leer el valor final (también debería estar protegido si otros procesos aún pudieran modificarlo)
    with l_val:
        final_val = v_ex.value
    print(f"Valor final (Value): {final_val}") # Debería ser 20000