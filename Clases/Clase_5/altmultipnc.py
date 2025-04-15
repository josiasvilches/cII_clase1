from multiprocessing import Process, Queue
import time

def productor(nombre, q):
    for i in range(3):
        msg = f"{nombre} dice {i}"
        print(f"[{nombre}] Enviando: {msg}")
        q.put(msg)
        time.sleep(0.3)
    print(f"[{nombre}] Terminé.")

def consumidor(nombre, q):
    while True:
        dato = q.get()
        if dato is None:
            print(f"[{nombre}] Recibí señal de fin. Cerrando.")
            break
        print(f"[{nombre}] Procesando: {dato}")
        time.sleep(1)

if __name__ == "__main__":
    q = Queue()

    productores = [
        Process(target=productor, args=("Prod1", q)),
        Process(target=productor, args=("Prod2", q))
    ]
    consumidores = [
        Process(target=consumidor, args=("Cons1", q)),
        Process(target=consumidor, args=("Cons2", q))
    ]

    for p in productores:
        p.start()
    for c in consumidores:
        c.start()

    for p in productores:
        p.join()

    # Enviar una señal de fin por cada consumidor
    for _ in consumidores:
        q.put(None)

    for c in consumidores:
        c.join()

    print("Todos los procesos terminaron.")
