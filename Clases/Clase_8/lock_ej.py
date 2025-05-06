from multiprocessing import Process, Lock

def imprimir_con_lock(lock, mensaje):
    with lock:
        print(mensaje)

if __name__ == '__main__':
    lock = Lock()
    procesos = []

    for i in range(5):
        p = Process(target=imprimir_con_lock, args=(lock, f"Soy el proceso {i}"))
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()
