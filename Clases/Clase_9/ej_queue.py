from multiprocessing import Process, Queue
import time
import os
import random

def producer_queue(queue): # Renombrado
    """ Pone 5 tareas en la cola. """
    pid = os.getpid()
    for i in range(5):
        task = f"Tarea {i} from PID {pid} (Queue)"
        print(f"Productor (Queue): Poniendo '{task}'")
        queue.put(task)
        time.sleep(0.5)
    # Señal de fin para CADA consumidor. Si hay N consumidores, N señales.
    queue.put("DONE_Q") # Renombrado 

def consumer_queue(queue, worker_id): # Renombrado
    """ Toma tareas de la cola hasta recibir 'DONE_Q'. """
    pid = os.getpid()
    while True:
        task = queue.get() # Bloquea si la cola está vacía
        print(f"Consumidor {worker_id} (PID {pid}, Queue): Obtenido '{task}'")
        if task == "DONE_Q":
            print(f"Consumidor {worker_id} (Queue): Señal de fin recibida.")
            # Si hay varios consumidores, es crucial que el productor ponga
            # una señal "DONE_Q" por cada consumidor.
            break 
        # Procesa la tarea...
        print(f"Consumidor {worker_id} (Queue): Procesando '{task}'...")
        time.sleep(random.uniform(0.5,1.5)) # Simula trabajo
        print(f"Consumidor {worker_id} (Queue): Terminado con '{task}'.")


if __name__ == '__main__':
    q_ex = Queue() # Renombrado

    p_q = Process(target=producer_queue, args=(q_ex,))
    c1_q = Process(target=consumer_queue, args=(q_ex, 1))
    # c2_q = Process(target=consumer_queue, args=(q_ex, 2)) # Si hay 2 consumidores, el productor necesita 2 "DONE_Q"

    p_q.start()
    c1_q.start()
    # c2_q.start()

    p_q.join()
    c1_q.join()
    # c2_q.join()
    print("Sistema Productor-Consumidor (Queue) terminado.")