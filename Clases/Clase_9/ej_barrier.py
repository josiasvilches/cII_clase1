from multiprocessing import Process, Barrier
import time
import random

def phase_worker_barrier(barrier, process_id): # Renombrado
    """ Simula un worker que trabaja en dos fases. """
    
    # Fase 1
    work_time1 = random.uniform(0.5, 3.0)
    print(f"Proceso {process_id} (Barrier): Iniciando Fase 1 ({work_time1:.2f}s)...")
    time.sleep(work_time1)
    print(f"Proceso {process_id} (Barrier): Fase 1 completada. Esperando en Barrera...")
    
    idx = barrier.wait() # Espera a que todos lleguen
    print(f"Proceso {process_id} (Barrier): Soy el {idx}-ésimo en llegar. ¡Todos llegaron!")
    
    # Fase 2
    print(f"Proceso {process_id} (Barrier): Iniciando Fase 2...")
    work_time2 = random.uniform(0.5, 2.0)
    time.sleep(work_time2)
    print(f"Proceso {process_id} (Barrier): Fase 2 completada.")
    
    # Podría haber otra barrera aquí si hubiera una Fase 3

if __name__ == '__main__':
    NUM_PROCESSES_BAR = 8 # Renombrado
    # Creamos una barrera para NUM_PROCESSES_BAR procesos
    barrier_ex = Barrier(NUM_PROCESSES_BAR) # Renombrado
    
    processes_bar = [] # Renombrado
    print(f"Lanzando {NUM_PROCESSES_BAR} workers (Barrier)...")
    for i in range(NUM_PROCESSES_BAR):
        p = Process(target=phase_worker_barrier, args=(barrier_ex, i))
        processes_bar.append(p)
        p.start()

    for p in processes_bar:
        p.join()
    print("Todas las fases (Barrier) completadas.")