from multiprocessing import Process, Queue
import time

def productor(q):
    for i in range(5):
        mensaje = f"Mensaje {i}"
        print(f"[Productor] Enviando: {mensaje}")
        q.put(mensaje)
        time.sleep(0.5)  # Simula trabajo
    q.put(None)  # Señal de fin
    print("[Productor] Terminé de enviar.")

def consumidor(q):
    while True:
        dato = q.get()
        if dato is None:
            print("[Consumidor] Recibí señal de fin. Cerrando.")
            break
        print(f"[Consumidor] Procesando: {dato}")
        time.sleep(1)  # Simula trabajo más pesado

if __name__ == "__main__":
    q = Queue()
    p1 = Process(target=productor, args=(q,))
    p2 = Process(target=consumidor, args=(q,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    print("Programa finalizado.")
