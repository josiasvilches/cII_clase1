from multiprocessing import Process, Condition, Lock, Queue
import time
import random

BUFFER_SIZE_COND_Q = 3 # Renombrado
def producer_cond_q(queue, condition): # Renombrado
    for i in range(10):
        item = f"Item-CQ {i}" # Renombrado
        with condition:
            while queue.qsize() >= BUFFER_SIZE_COND_Q:
                print(f"Productor-CQ: Buffer lleno ({queue.qsize()}), esperando...")
                condition.wait() # Espera si está lleno
            
            print(f"Productor-CQ: Añadiendo {item}")
            queue.put(item)
            condition.notify() # Notifica al consumidor (podría ser notify_all si hay varios consumidores)
        time.sleep(random.uniform(0.0, 0.2))

def consumer_cond_q(queue, condition): # Renombrado
    for _ in range(10):
        with condition:
            while queue.empty():
                print(f"Consumidor-CQ: Buffer vacío, esperando...")
                condition.wait() # Espera si está vacío

            item = queue.get()
            print(f"Consumidor-CQ: Consumiendo {item}")
            condition.notify() # Notifica al productor (si podría estar esperando por espacio)
        time.sleep(random.uniform(0.1, 0.4))

if __name__ == '__main__':
    q_cq = Queue() # Renombrado
    lock_cq = Lock() # Renombrado
    cond_cq = Condition(lock_cq) # Renombrado

    p_proc_cq = Process(target=producer_cond_q, args=(q_cq, cond_cq))
    c_proc_cq = Process(target=consumer_cond_q, args=(q_cq, cond_cq))

    p_proc_cq.start()
    c_proc_cq.start()

    p_proc_cq.join()
    c_proc_cq.join()
    print("Productor-Consumidor con Condition y Queue terminado.")