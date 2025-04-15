from multiprocessing import Process, Queue

def productor(q):
    q.put("Hola desde el productor")

def consumidor(q):
    dato = q.get()
    print(f"Consumidor recibió: {dato}")

if __name__ == "__main__":
    q = Queue()

    p1 = Process(target=productor, args=(q,))
    p2 = Process(target=consumidor, args=(q,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
