from multiprocessing import Process, Lock, Value
import time
import ctypes

def safe_increment(counter, lock):
    """ Incrementa un contador 10000 veces usando un Lock. """
    for _ in range(10000):
        with lock: # Adquiere y libera automáticamente
            temp = counter.value
            time.sleep(0.0001) # Descomentar para ver más claramente el efecto sin lock
            counter.value = temp + 1

if __name__ == '__main__':
    shared_counter = Value(ctypes.c_int, 0)
    lock = Lock()
    
    p1 = Process(target=safe_increment, args=(shared_counter, lock))
    p2 = Process(target=safe_increment, args=(shared_counter, lock))

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print(f"Valor final (seguro con Lock): {shared_counter.value}") # Debería ser 20000