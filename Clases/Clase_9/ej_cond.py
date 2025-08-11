from multiprocessing import Process, Condition, Lock, Value
import time
import ctypes

def producer_cond_ex(condition, shared_value, process_id): # Renombrado
    """ Produce valores y notifica. """
    for i in range(1, 6):
        with condition: # Adquiere el lock asociado
            shared_value.value = i
            print(f"Proceso {process_id} (Productor-Cond): Producido {i}")
            print(f"Proceso {process_id} (Productor-Cond): Notificando a todos...")
            condition.notify_all() # Notifica a todos los waiters
            time.sleep(1) # Da tiempo a que los consumidores reaccionen

def consumer_cond_ex(condition, shared_value, process_id): # Renombrado
    """ Espera una condición y consume. """
    with condition: # Adquiere el lock asociado
        print(f"Proceso {process_id} (Consumidor-Cond): Esperando valor >= 3...")
        while shared_value.value < 3:
            condition.wait() # Libera el lock y espera
        # Cuando despierta, tiene el lock y la condición es (o era) >= 3
        print(f"Proceso {process_id} (Consumidor-Cond): ¡Condición cumplida! Valor = {shared_value.value}")

if __name__ == '__main__':
    lock_cond = Lock() # Renombrado
    condition_ex = Condition(lock_cond) # Renombrado, Condition usa un Lock
    value_cond = Value(ctypes.c_int, 0) # Renombrado

    p_cond = Process(target=producer_cond_ex, args=(condition_ex, value_cond, 0))
    consumers_cond = [Process(target=consumer_cond_ex, args=(condition_ex, value_cond, i+1)) for i in range(3)]

    for c in consumers_cond:
        c.start()
    time.sleep(0.1) # Asegurar que los consumidores esperen primero
    p_cond.start()

    p_cond.join()
    for c in consumers_cond:
        c.join()
    print("Sistema Productor-Consumidor (Condition) terminado.")