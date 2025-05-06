from multiprocessing import Process, Queue

def productor(q):
    q.put("Mensaje desde el productor")

def consumidor(q):
    mensaje = q.get()
    print("Consumidor recibió:", mensaje)

if __name__ == '__main__':
    q = Queue()
    p1 = Process(target=productor, args=(q,))
    p2 = Process(target=consumidor, args=(q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
