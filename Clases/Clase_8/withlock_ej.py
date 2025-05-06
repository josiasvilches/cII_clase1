from multiprocessing import Process, Value, Lock

def sumar_100_lockeado(contador, lock):
    for _ in range(100):
        with lock:
            contador.value += 1

if __name__ == '__main__':
    contador = Value('i', 0)
    lock = Lock()
    p1 = Process(target=sumar_100_lockeado, args=(contador, lock))
    p2 = Process(target=sumar_100_lockeado, args=(contador, lock))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print("Valor final con lock:", contador.value)
