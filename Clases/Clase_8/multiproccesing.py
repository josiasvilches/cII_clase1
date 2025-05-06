from multiprocessing import Process, current_process
import time, os

def saludar():
    print(f"[PID {os.getpid()}] Hola desde el proceso {current_process().name}")
    time.sleep(1)

if __name__ == '__main__':
    procesos = []

    for i in range(3):
        p = Process(target=saludar, name=f"Proceso-{i}")
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()

    print("Todos los procesos han terminado.")
