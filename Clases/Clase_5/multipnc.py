from multiprocessing import Process, Queue
import time
import random

def productor(q, id):
    for i in range(3):
        mensaje = f"P{id} - tarea {i}"
        print(f"[Productor {id}] Enviando: {mensaje}")
        q.put(mensaje)
        time.sleep(random.uniform(0.1, 0.5))
    q.put(None)  # Señal de fin por cada productor

def consumidor(q, id):
    while True:
        tarea = q.get()
        if tarea is None:
            print(f"[Consumidor {id}] Recibí señal de fin. Cerrando.")
            q.put(None)  # Reenvía señal para otros consumidores
            break
        print(f"[Consumidor {id}] Procesando: {tarea}")
        time.sleep(random.uniform(0.3, 0.8))

if __name__ == "__main__":
    q = Queue()
    productores = [Process(target=productor, args=(q, i)) for i in range(2)]
    consumidores = [Process(target=consumidor, args=(q, i)) for i in range(2)]

    for p in productores: p.start()
    for c in consumidores: c.start()
    for p in productores: p.join()
    for c in consumidores: c.join()

    print("Todos los procesos han terminado.")
