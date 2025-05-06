# mp_worker.py
from multiprocessing import Pool, Value
import os
import time

contador_global = None

def inicializar_contador(contador_compartido):
    global contador_global
    contador_global = contador_compartido

def tarea(numero):
    print(f"Proceso {os.getpid()} ejecutando tarea con número {numero}")
    time.sleep(1)

    with contador_global.get_lock():  # Protección con Lock automático
        contador_global.value += 1
    return numero * 2
     


if __name__ == '__main__':
    from multiprocessing import set_start_method
    set_start_method('fork')  # Cambia el método de inicio a 'spawn'

    contador = Value('i', 0)
    numeros = list(range(10))
    with Pool(processes=4, initializer=inicializar_contador, initargs=(contador,)) as pool:
        resultados = pool.map(tarea, numeros)

    print("Resultados finales:", resultados)
    print("Contador compartido final:", contador.value)
